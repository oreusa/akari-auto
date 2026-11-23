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


# ---------- 前のページ（頭・mk3＋jh の見出し・jn の数字・st の順番・jb のボタン・jl のリンク）の中身を、新しい部品（doc.js の .dc）に ----------
def _txt(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()


def v2_head(b):
    h = re.search(r'<h1>(.*?)</h1>', b, re.S).group(1)
    span = (re.search(r'<span>(.*?)</span>', h, re.S) or [None, ''])[1]
    h1 = _txt(re.sub(r'<span>.*?</span>', '', h))
    sub = (re.search(r'<p class="sub">(.*?)</p>', b, re.S) or [None, ''])[1].replace('<br>', '')
    upd = _txt((re.search(r'<div class="upd">(.*?)</div>', b, re.S) or [None, ''])[1])
    return h1, span, sub, upd


def v2_body(b, near_label='', k=''):
    """mk3 の区切りごとに .dsec へ。中の部品の名前を新しい物に直す"""
    b = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', b, flags=re.S)
    b = b[b.index('</div>', b.index('<div class="upd">')) + 6:] if '<div class="upd">' in b else b
    b = re.sub(r'<div class="ft">.*$', '', b, flags=re.S)
    b = re.sub(r'^\s*(</div>\s*)+', '', b)
    parts = re.split(r'<p class="mk3"[^>]*>.*?</p>', b)
    out = []
    for i, sc in enumerate(parts):
        if not sc.strip(): continue
        h2 = re.search(r'<h2 class="jh">(.*?)</h2>', sc, re.S)
        h2t = _txt(h2.group(1)) if h2 else ''
        sc = re.sub(r'<h2 class="jh">.*?</h2>', '', sc, flags=re.S)
        near = re.findall(r'<a class="jl" href="([^"]+)"[^>]*style="[^"]*"[^>]*>(.*?)<i>→</i></a>', sc, re.S)
        if near:
            sc = re.sub(r'<a class="jl" href="[^"]+"[^>]*style="[^"]*"[^>]*>.*?</a>', '', sc, flags=re.S)
            sc = '<div class="drel">' + ''.join(f'<a href="{u}" data-k="{k}｜近くの街">{_txt(n)}<small>{near_label}</small></a>' for u, n in near) + '</div>' + sc
        # 3問診断などの、文字で書いた枠のボタン
        sc = re.sub(r'<a href="([^"]+)" data-k="([^"]+)" style="[^"]*">(.*?)<small style="[^"]*">(.*?)</small></a>',
                    lambda m: f'<a class="dbtn2 dgo" href="{m.group(1)}" data-k="{m.group(2)}">{m.group(3).replace(" →", "")}<small>{m.group(4)}</small></a>', sc, flags=re.S)
        sc = re.sub(r'<div class="st"><i>(\d+)</i><div><b>(.*?)</b>', r'<div class="dstp"><i>\1</i><div><b>\2</b>', sc)
        sc = sc.replace('class="jb b1"', 'class="dbtn"').replace('class="jb"', 'class="dbtn2"').replace('class="jp"', 'class="dnote"').replace('class="src"', 'class="dnote"')
        sc = re.sub(r'<a class="jl" href="([^"]+)"([^>]*)>(.*?)\s*<i>→</i></a>', r'<a class="dlk" href="\1"\2>\3</a>', sc, flags=re.S)
        sc = re.sub(r'<p style="[^"]*">', '<p class="dtx">', sc)
        out.append('<section class="dsec">' + (f'<h2>{E(h2t)}</h2>' if h2t else '') + sc.strip() + '</section>')
    return ''.join(out)


def jikka_town(path, brand):
    t = old(path)
    if not t: return None
    b = t[t.index('<body'):]
    h1, span, sub, upd = v2_head(b)
    body = v2_body(b, '実家・空き家ノート', '実家')
    return {'h1': h1, 'sub': f'<b>{E(span)}</b><br>{sub}' + (f'<br><small>{E(upd)}</small>' if upd else ''), 'html': body}


def jikka_index(path, ex):
    t = old(path)
    if not t: return None
    b = t[t.index('<body'):]
    h1, span, sub, upd = v2_head(b)
    tabs = re.findall(r'<button data-p="(\w+)"[^>]*>(.*?)</button>', b)
    panes, tw = [], []
    for pid, lab in tabs:
        sec = re.search(r'<section class="pane[^"]*" id="' + pid + r'">(.*?)</section>', b, re.S).group(1)
        rows = re.findall(r'<a href="(/jikka/([\w-]+))"[^>]*>(.*?)<small>(.*?)</small></a>', sec)
        tw += [{'id': i, 'n': _txt(n), 'p': lab, 'k': ''} for _, i, n, _ in rows]
        panes.append(f'<ul class="dli" data-p="{pid}"' + ('' if not panes else ' hidden') + '>' + ''.join(
            f'<li><a href="{u}" data-k="実家一覧｜{_txt(n)}"><b>{n}</b><small>{s}</small></a></li>' for u, _, n, s in rows) + '</ul>')
    note = (re.search(r'<p class="note">(.*?)</p>', b, re.S) or [None, ''])[1]
    go = re.search(r'<a href="(/jikka/shindan/)" data-k="([^"]+)"[^>]*>(.*?)<small[^>]*>(.*?)</small></a>', b, re.S)
    html_ = ((f'<a class="dbtn dgo" href="{go.group(1)}" data-k="{go.group(2)}">{go.group(3).replace(" →", "")}<small>{go.group(4)}</small></a>' if go else '') +
             f'<section class="dsec"><h2>街をえらぶ</h2><input class="din" id="tq" type="search" placeholder="街の名前（例：{E(ex)}）" autocomplete="off" aria-label="街の名前で探す"><div id="tqo"></div>'
             '<div class="dchs rkg djp" id="jp">' + ''.join(f'<button type="button" data-p="{pid}" aria-pressed="{"true" if i == 0 else "false"}">{E(lab)}</button>' for i, (pid, lab) in enumerate(tabs)) + '</div>'
             + ''.join(panes) + '</section>' + (f'<p class="dnote">{note}</p>' if note else ''))
    js = ('var b=document.getElementById("jp");if(b){var go=function(p){[].forEach.call(b.children,function(x){x.setAttribute("aria-pressed",x.dataset.p===p?"true":"false")});'
          '[].forEach.call(document.querySelectorAll(".dli"),function(u){u.hidden=u.dataset.p!==p})};b.addEventListener("click",function(e){var x=e.target.closest("button");if(x)go(x.dataset.p)});'
          'var h=location.hash.slice(1);if(h&&b.querySelector(\'[data-p="\'+h+\'"]\'))go(h)}')
    return {'h1': h1, 'sub': f'<b>{E(span)}</b><br>{sub}' + (f'<br><small>{E(upd)}</small>' if upd else ''), 'html': html_, 'js': js, 'tw': tw, 'tqb': '/jikka/'}


def meta(path):
    t = old(path) or ''
    ti = _txt((re.search(r'<title>(.*?)</title>', t, re.S) or [None, ''])[1])
    de = html.unescape((re.search(r'<meta name="description" content="([^"]*)"', t) or [None, ''])[1])
    return ti, de


def shindan(path):
    """3問診断：問い・計算（script）は前のページのまま。見た目だけ新しい部品（shin.css の .dqz）"""
    t = old(path)
    if not t: return None
    b = t[t.index('<body'):]
    js = max(re.findall(r'<script>(.*?)</script>', b, re.S), key=len)
    h1 = _txt(re.search(r'<h1>(.*?)</h1>', b, re.S).group(1))
    inner = b[b.index('<p class="lead"'):b.index('<div class="ft">')]
    return {'h1': h1, 'sub': '', 'html': '<div class="dqz">' + inner + '</div>', 'js': js}
