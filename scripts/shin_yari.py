"""新しいHP：前のページ（頭をかぶせただけ）を、この土台で作り直す（11/23 owner「hpと同じじゃないのあるんじゃない？全部やり変えて」）。
関西と関東で同じファイル（燈 akari-auto scripts/shin_yari.py は この写し）。
数字・計算の元は前のページのまま（毎朝ほかの機械が作る）。前のページは消さない。新しい形に書き替えた後は kyu/ に残した前のページから読む。"""
import html, json, os, re

E = html.escape


def old(path):
    if os.path.exists(path) and '/shin/shin.css' in open(path, encoding='utf-8').read():
        path = os.path.join(os.path.dirname(path), 'kyu', os.path.basename(path))
    return open(path, encoding='utf-8').read() if os.path.exists(path) else None


def rel_html(rel, k):
    return ('<section class="dsec"><h2>あわせて見る</h2><div class="drel">' +
            ''.join(f'<a href="{u}" data-k="{k}｜関連｜{E(t)}">{E(t)}<small>{E(s)}</small></a>' for t, u, s in rel) + '</div></section>')


# ---------- 家を買いたい（/sagasu）：sg.js ----------
def sagasu(path, rel):
    t = old(path)
    if not t: return None
    b = t[t.index('<body'):]
    s = re.search(r'<script>(.*?)</script>', b, re.S).group(1)
    J = lambda name: json.loads(re.search(name + r'=(\[.*?\]|\{.*?\}|"[^"]*")(?=[,;])', s, re.S).group(1))
    rows = json.loads(re.search(r'var D=(\[.*?\]),ORD=', s, re.S).group(1))
    kinds = [[k, y, html.unescape(l)] for k, y, l in re.findall(r'<button type="button" data-k="(\w)" data-y="([\w/]+)"[^>]*>(.*?)</button>', b)]
    h1 = html.unescape(re.sub('<[^>]+>', '', re.search(r'<h1>(.*?)</h1>', b, re.S).group(1))).strip()
    sub = re.search(r'<p class="usp">(.*?)</p>', b, re.S).group(1).replace('<br>', '')
    note = re.search(r'<p class="nt">(.*?)</p>', b, re.S).group(1)
    yr = (re.search(r'/search/(\d\d)/', s) or [None, '06'])[1]
    aff = re.search(r'"(https://ck\.jp\.ap\.valuecommerce\.com/servlet/referral\?sid=\d+&pid=\d+&vc_url=)"', s).group(1)  # 関西と関東で番号がちがう
    for r in rows:  # 使わない欄（色など）は落とす
        r.pop('la', None) if r.get('l') is None else None
    return {'h1': h1, 'sub': sub, 'rows': rows, 'ord': J('ORD'), 'bud': J('BUD'), 'unit': J('UNIT'), 'units': J('UNITS'), 'kinds': kinds, 'yr': yr, 'aff': aff,
            'note': note, 'foot': rel_html(rel, '家を買いたい'),
            'html': f'<p>{sub}</p><ol>' + ''.join(f'<li>{E(r["n"])}（{E(r["p"])}）</li>' for r in rows) + '</ol>'}
