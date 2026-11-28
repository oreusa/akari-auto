"""新しいHP：前のページ（頭をかぶせただけ）を、この土台で作り直す（11/23 owner「hpと同じじゃないのあるんじゃない？全部やり変えて」）。
関西と関東で同じファイル（燈 akari-auto scripts/shin_yari.py は この写し）。
数字・計算の元は前のページのまま（毎朝ほかの機械が作る）。前のページは消さない。新しい形に書き替えた後は kyu/ に残した前のページから読む。"""
import html, json, os, re

E = html.escape


def old(path):
    if os.path.exists(path) and '/shin/shin.css' in open(path, encoding='utf-8').read():
        d, b = os.path.split(path)
        a = os.path.join(d, 'kyu', b)  # site/kyu/x.html
        if not os.path.exists(a):  # site/kyu/o/x.html（下の階の前のページ）
            u, s = os.path.split(d); a = os.path.join(u, 'kyu', s, b)
        path = a
    return open(path, encoding='utf-8').read() if os.path.exists(path) else None


# 11/23 owner「収益化が何一つ上手くいってない」：見られている家・地価のページの1画面目に「いくらで売れるか無料で聞く（◯◯市）」を1つ（shin.js sellCta）。
# 関西は自分の申し込み（街を入れて開く）・関東は契約済みの査定（A8 ざっくりAI査定＋）。
SELL_A8 = 'https://px.a8.net/svt/ejp?a8mat=4BGH3I+E2NY4I+5Y9M+5YJRM'


def sell_cfg(kanto, n='', id=''):
    if kanto:
        c = {'u': SELL_A8, 'ad': 1, 'sm': '無料・約1分でわかる（ざっくりAI査定＋・広告）', 'any': '関東どこでも'}
    else:
        c = {'u': '/moushikomi?want=' + '査定してほしい', 'sm': '無料・売るか決めていなくても大丈夫・約1分', 'any': '関西どこでも'}
    if n: c['n'] = n
    if id: c['id'] = id
    return c


def town_of(d):
    """実家の街のページの h1（神戸市東灘区の実家・空き家ノート）から街の名前。"""
    m = re.match(r'(.+?)の実家', (d or {}).get('h1', ''))
    return m.group(1) if m else ''

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


# ---------- 解体（入口 /kaitai・市ごと /kaitai-<市>・補助金ランキング /kaitai-ranking）：中の部品と30秒の計算はそのまま、見た目を新しい部品（.ktz）に ----------
def kaitai(path, rel_note=''):
    t = old(path)
    if not t: return None
    b = t[t.index('<body'):]
    js = '\n'.join(s for s in re.findall(r'<script>(.*?)</script>', b, re.S))
    b = re.sub(r'<script[^>]*>.*?</script>', '', b, flags=re.S)
    h = re.search(r'<h1>(.*?)</h1>', b, re.S).group(1)
    h1 = _txt(re.sub(r'<span>.*?</span>', '', h)); span = _txt((re.search(r'<span>(.*?)</span>', h, re.S) or [None, ''])[1])
    sub = (re.search(r'<p class="sub">(.*?)</p>', b, re.S) or [None, ''])[1].replace('<br>', '')
    upd = _txt((re.search(r'<div class="upd">(.*?)</div>', b, re.S) or [None, ''])[1])
    fv = re.search(r'<div class="fv">(.*?)</div>\s*<div class="upd">', b, re.S)
    top = ''
    if fv:
        f = fv.group(1)
        n = (re.search(r'<div class="n">(.*?)</div>', f, re.S) or [None, ''])[1]
        d = (re.search(r'<div class="d">(.*?)</div>', f, re.S) or [None, ''])[1]
        bt = re.findall(r'<a class="([kw])" (href="[^"]*" data-k="[^"]*")>(.*?)</a>', f, re.S)
        top = ('<div class="kzv">' + f'<div class="kzn">{n}</div>' + (f'<p>{d}</p>' if d else '') + '<div class="kzb">' +
               ''.join(f'<a class="{"dbtn" if c == "k" else "dbtn2"}" {a}>{x}</a>' for c, a, x in bt) + '</div></div>')
    i0 = b.index('</div>', b.index('<div class="upd">')) + 6 if '<div class="upd">' in b else b.index('<nav')
    i0 = b.index('</div>', i0) + 6 if b[i0:i0 + 40].strip().startswith('</div>') else i0
    body = b[i0:b.index('<div class="ft">')]
    body = re.sub(r'^\s*</div>', '', body)
    body = body.replace('<nav class="toc"', '<nav class="ktoc"')
    body = re.sub(r'<section (id="[^"]+" )?class="ps"[^>]*>', lambda m: f'<section {m.group(1) or ""}class="dsec ps">', body)
    body = body.replace('<section class="faq">', '<section class="dsec faq">')
    body = re.sub(r'<details>\s*<summary>(.*?)</summary>(.*?)</details>', r'<details><summary>\1</summary><div class="ddd">\2</div></details>', body, flags=re.S)
    body = body.replace('class="kt-b"', 'class="dbtn kt-b"').replace('class="kt-b ', 'class="dbtn kt-b ').replace('class="kt-k"', 'class="dbtn2 kt-k"').replace('<p class="note">', '<p class="dnote">')
    al = re.search(r'<nav class="also"[^>]*>(.*?)</nav>', body, re.S)
    if al:
        links = re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', al.group(1))
        body = body.replace(al.group(0), '<section class="dsec"><h2>あわせて見る</h2><div class="drel">' + ''.join(f'<a href="{u}" data-k="解体｜関連｜{_txt(x)}">{x}<small>{rel_note}</small></a>' for u, x in links) + '</div></section>')
    body = re.sub(r'<a class="back"[^>]*>.*?</a>', '', body, flags=re.S)
    return {'h1': h1, 'sub': (f'<b>{E(span)}</b>' if span else '') + (f'<br>{sub}' if sub else '') + (f'<br><small>{E(upd)}</small>' if upd else ''),
            'html': top + '<div class="ktz">' + body + '</div>', 'js': js}


# ---------- 空き家の割合ランキング（/akiya-ranking）：地価ランキングと同じ rk.js ----------
def akiya(path, an, ex, rel):
    t = old(path)
    if not t: return None
    b = t[t.index('<body'):]
    h = re.search(r'<h1>(.*?)</h1>', b, re.S).group(1)
    h1 = _txt(re.sub(r'<span>.*?</span>', '', h)); span = _txt((re.search(r'<span>(.*?)</span>', h, re.S) or [None, ''])[1])
    sub = (re.search(r'<p class="sub">(.*?)</p>', b, re.S) or [None, ''])[1].replace('<br>', '')
    btn = re.findall(r'<button data-p="(\w+)"[^>]*>(.*?)</button>', b)
    allp = re.search(r'<section class="pane[^"]*" id="all">(.*?)</section>', b, re.S).group(1)
    rows = []
    for u, nm, sm, v in re.findall(r'<a href="([^"]+)"[^>]*><span class="no">\d+</span><span class="nm">(.*?)((?:<small>.*?</small>)+)</span>.*?<span class="v"[^>]*>([\d.]+)%</span>', allp, re.S):
        sms = re.findall(r'<small>(.*?)</small>', sm)
        rows.append({'n': _txt(nm), 's': _txt(nm), 'u': u, 'id': u.rsplit('/', 1)[-1], 'p': sms[0] if len(sms) > 1 else '', 'x': '空き家 ' + sms[-1], 'k': '', 'v': {'a': [None, float(v)]}})
    groups = [{'k': 'all', 'l': an + 'ぜんぶ'}] + [{'k': l, 'l': l, 'h': k} for k, l in btn if k != 'all']
    faq = [(_txt(q), f'<p>{a}</p>' if not a.strip().startswith('<p') else a) for q, a in re.findall(r'<details>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>', b, re.S)]
    note = (re.search(r'<p class="note">(.*?)</p>', b, re.S) or [None, ''])[1]
    foot = (('<section class="dsec"><h2>よくある質問</h2>' + ''.join(f'<details><summary>{E(q)}</summary><div class="ddd">{a}</div></details>' for q, a in faq) + '</section>' if faq else '')
            + f'<section class="dsec"><h2>数字の出どころ</h2><p class="dnote">{note}</p></section>' + rel_html(rel, '空き家ランキング'))
    pre = '<ol>' + ''.join(f'<li>{E(r["n"])}（{E(r["p"])}）空き家の割合 {r["v"]["a"][1]}%</li>' for r in rows) + '</ol>' + foot
    return {'h1': h1, 'sub': f'{E(span)}・{_txt(sub)}', 'an': an, 'tabs': [{'k': 'a', 'l': '空き家の割合'}], 'groups': groups, 'rows': rows, 'avg': {}, 'ex': ex, 'plain': 1, 'foot': foot, 'html': pre}


# ---------- 申し込み（/moushikomi）・リクエストと感想（/koe）：入力の部品と送る仕組み（script）はそのまま、見た目を新しい部品（.fmz）に ----------
def form(path):
    t = old(path)
    if not t: return None
    b = t[t.index('<body'):]
    js = '\n'.join(re.findall(r'<script>(.*?)</script>', b, re.S))
    b = re.sub(r'<script[^>]*>.*?</script>', '', b, flags=re.S)
    b = b[b.index('<div class="wrap">') + 18:b.index('<div class="ft">')]
    b = re.sub(r'<img [^>]*logo[^>]*>', '', b)
    b = re.sub(r'<div class="en">.*?</div>', '', b)
    # 見出し：前の script が .s3h h1・.s3l・.s3m を書き替えるので、その名前のまま新しい見出しの形に
    b = re.sub(r'<div class="s3h"><div>\s*<h1>(.*?)</h1></div></div>', r'<section class="hero s3h"><h1 class="h1t">\1</h1></section>', b, flags=re.S)
    b = re.sub(r'<div class="head">\s*<h1>(.*?)</h1>(.*?)</div>', lambda m: f'<section class="hero"><h1 class="h1t">{m.group(1)}</h1>' + m.group(2).replace('class="sub"', 'class="h1p"') + '</section>', b, flags=re.S)
    b = re.sub(r'<style[^>]*>.*?</style>', '', b, flags=re.S)  # 11/28 前の <style>（.kw など）は関西では止まっていた・関東だけ生きていた→両方とも新しい部品（shin.css）にまかせる
    b = re.sub(r' style="[^"]*"', '', b)  # 前の色・余白の指定（夜に読めない色もある）は新しい部品にまかせる
    b = b.replace('<p class="s3l">', '<p class="h1p s3l">').replace('class="back"', 'class="back dlk"').replace('<p class="note">', '<p class="dnote">')
    if 'id="mf"' in b and 'name="want"' in b and 'id="kw"' in b:
        b, js = three(b, js)
    h1 = _txt((re.search(r'<h1[^>]*>(.*?)</h1>', b, re.S) or [None, ''])[1])
    return {'h1': h1, 'nohero': 1, 'html': '<div class="fmz">' + b + '</div>', 'js': js}


def three(b, js):
    """11/23 owner「収益化が何一つ上手くいってない」：申し込みは7日で開いた6・書きはじめ2・送信0。
    1画面目は3つだけ（ご用件・お家の場所・ご連絡先）。お名前・種類・内容・お家のことは「ほかにも書く（任意）」にたたむ。送る仕組みは前のまま。"""
    def cut(pat):
        nonlocal b
        m = re.search(pat, b, re.S)
        if not m: raise ValueError('3問：見つからない ' + pat[:30])
        b = b.replace(m.group(0), '', 1)
        return m.group(0)
    A = cut(r'<label class="fl" for="nm">.*?<input[^>]*id="nm"[^>]*>')
    B = cut(r'<label class="fl" for="em">.*?<input[^>]*id="em"[^>]*>')
    C = cut(r'<label class="fl" for="tl">.*?<input[^>]*id="tl"[^>]*><div id="ttw" hidden>.*?</p></div>')
    D = cut(r'<label class="fl" for="pl">.*?<input[^>]*id="pl"[^>]*>')
    E = cut(r'<div class="fl"[^>]*>お家の種類</div>\s*<div class="ch">.*?</div>')
    F = cut(r'<div class="fl"[^>]*>ご希望</div>\s*<div class="ch">.*?</div>')
    G = cut(r'<label class="fl" for="tx">.*?</textarea>')
    H = cut(r'<details class="kw" id="kw"[^>]*>.*?</details>')
    Hin = re.sub(r'^<details[^>]*>\s*<summary>.*?</summary>', '', H, flags=re.S)[:-len('</details>')]
    A = re.sub(r'<em>.*?</em>', '<em>任意</em>', A, count=1).replace(' required', '')
    F = re.sub(r'<div class="fl"[^>]*>ご希望</div>', '<div class="fl q3"><i>1</i>ご用件</div>', F)
    D = re.sub(r'(<label class="fl" for="pl">)(.*?)(<em>.*?</em>)?</label>', r'\1<i>2</i>お家の場所<em>市区町村まで</em></label>', D, count=1, flags=re.S)
    B = re.sub(r'<em>.*?</em>', '<em>お返事はメールで</em>', B, count=1)
    C = re.sub(r'(<label class="fl" for="tl">.*?)<em>.*?</em>', r'\1<em>お電話でのお返事をご希望の方</em>', C, count=1, flags=re.S)
    q3 = '<div class="fl q3"><i>3</i>ご連絡先<em>メールか電話の、どちらかだけ</em></div>'
    more = ('<details class="kw fmore" id="kw"><summary>ほかにも書く<em>任意・書かなくても送れます</em></summary>' + A + E + G + Hin + '</details>')
    b = re.sub(r'(<form class="mf" id="mf"[^>]*>)', lambda m: m.group(1) + F + D + q3 + B + C + more, b, count=1)
    js = js.replace('if(!d.name){er.textContent="お名前を書いてください";return}', 'if(!d.name)d.name="お名前なし";')
    m = re.search(r'<p class="s3m">.*?</p>', b, re.S)  # 「1社に決めていない窓口」の説明は、3問の後ろ（送るボタンの上）へ
    if m:
        b = b.replace(m.group(0), '', 1).replace('<label class="ag">', m.group(0) + '<label class="ag">', 1)
    return b, js


# ---------- お得まとめ（/otoku）：関西・関東とも同じ入口（前は燈の古い形を関西でもそのまま出していた） ----------
OTOKU_JS = r'''var f=document.getElementById("kqf"),q=document.getElementById("kq");if(f){
var C={"water":"水","soda":"炭酸水","rice":"お米","tp":"トイレットペーパー","tea":"お茶","coffee":"コーヒー","detergent":"洗濯洗剤","softener":"柔軟剤","shampoo":"シャンプー","bodysoap":"ボディソープ","dish":"食器用洗剤","tissue":"ティッシュ","diaper":"おむつ","wipes":"おしりふき","trash":"ゴミ袋","battery":"乾電池","mask":"マスク","pasta":"パスタ","beans":"コーヒー豆","dogfood":"ドッグフード","catfood":"キャットフード"};
function nz(x){return (x||"").normalize("NFKC").toLowerCase().replace(/[\s　]/g,"").replace(/[ァ-ヶ]/g,function(c){return String.fromCharCode(c.charCodeAt(0)-96)})}
f.onsubmit=function(e){e.preventDefault();var v=q.value.trim();if(!v)return;var n=nz(v),u;
 if(/ふるさと/.test(n))u="/furusato";else if(/(ぽっきり|まらそん|せーる|買いまわり|かいまわり)/.test(n))u="/kaimawari";else if(/(値下が|ねさが|安くなった|本当に安)/.test(n))u="/nesage";else if(/(宿|ほてる|旅館|泊まり)/.test(n))u="/tomari";
 else{u="/okaimono";for(var k in C){if(n.indexOf(nz(C[k]))>=0){u="/okaimono#"+k;break}}}location.href=u}}'''


def otoku():
    tiles = [['日用品の値段くらべ', '/okaimono', '水・お米・洗剤など21種類の最安'], ['本当に安い？', '/nesage', 'ふだんより安くなった物'], ['セールの買いまわり', '/kaimawari', '楽天の1,000〜1,199円・送料込み'],
             ['ふるさと納税', '/furusato', '寄付1万円あたりの量でくらべる'], ['泊まりの宿', '/tomari', '遠くのおでかけと近くの宿'], ['開店・閉店', '/kaiten', '新しいお店・閉まるお店']]
    html_ = ('<section class="dsec"><h2>探したい物から</h2><form class="otq" id="kqf" role="search"><input class="din" id="kq" type="search" placeholder="例：トイレットペーパー・ふるさと納税" aria-label="探したい物を入れる" enterkeyhint="search">'
             '<button type="submit" class="dbtn">探す</button></form><p class="dhint">入れた言葉に合うページを開きます。</p></section>'
             '<section class="dsec"><h2>お得の入口</h2><div class="drel">' + ''.join(f'<a href="{u}" data-k="お得｜{t}">{t}<small>{s}</small></a>' for t, u, s in tiles) + '</div></section>'
             '<p class="dnote">このページから先の商品・宿へのリンクは広告（PR）です。</p>')
    return {'h1': 'お得まとめ', 'sub': 'セール・値下がり・ふるさと納税・宿。お得の入口をひとつに。', 'html': html_, 'js': OTOKU_JS}


def kau_cfg(cur, desc, foot):
    nav = [{'t': 'くらべる', 'ic': 'find', 'href': '/okaimono'}, {'t': '本当に安い？', 'ic': 'yen', 'href': '/nesage'}, {'t': 'ふるさと', 'ic': 'gift', 'href': '/furusato'}, {'t': 'お得', 'ic': 'star', 'href': '/otoku'}]
    return {'nav': [dict(n, cur=1) if n['href'] == cur else n for n in nav], 'menu': {'k': 'Shopping', 'items': [['お得な物', '/otoku', 1]]}, 'foot': foot, 'desc': desc}


# ---------- おでかけの1件ページ（/o/<id>）：前のページの中身（写真・日程・地図・公式・宿・ほかのおでかけ）を新しい部品に ----------
def spot(path, pn=None):
    t = old(path)
    if not t: return None
    b = t[t.index('<body'):]
    js = '\n'.join(re.findall(r'<script>(.*?)</script>', b, re.S))
    b = re.sub(r'<script[^>]*>.*?</script>', '', b, flags=re.S)
    h1, span, sub, upd = v2_head(b)
    body = b[b.index('</div>', b.index('<div class="upd">')) + 6:b.index('<div class="ft">')]
    body = re.sub(r'^\s*</div>', '', body)
    body = re.sub(r'(<div class="big">.*?</div></div>)', lambda m: re.sub(r' style="[^"]*"', '', m.group(1)), body, count=1, flags=re.S)
    body = body.replace('<p class="lead">', '<p class="dtx olead">').replace('<div class="note">', '<p class="dnote">')
    body = re.sub(r'(<p class="dnote">.*?)</div>', r'\1</p>', body, count=1, flags=re.S)
    body = re.sub(r'<div class="act">(.*?)</div>', lambda m: '<div class="oact">' + re.sub(r'<a class="o"', '<a class="dbtn"', re.sub(r'<a class="g"', '<a class="dbtn2"', m.group(1))) + '</div>', body, count=1, flags=re.S)
    body = re.sub(r'<ul class="yl">(.*?)</ul>', lambda m: '<ul class="dli oyl">' + re.sub(r'<a ([^>]*)>(.*?)<span>(.*?)</span></a>', r'<a \1><b>\2</b><small>\3</small></a>', m.group(1)) + '</ul>', body, flags=re.S)
    # ほかのおでかけ（カード）→ あわせて見るの板
    def fcs(m):
        cards = re.findall(r'<a class="fc" href="([^"]+)"[^>]*><small>(.*?)</small><b>(.*?)</b><span>(.*?)</span></a>', m.group(0), re.S)
        return '<div class="drel">' + ''.join(f'<a href="{u}" data-k="1件｜ほかのおでかけ">{ti}<small>{sp}</small></a>' for u, sm, ti, sp in cards) + '</div>'
    body = re.sub(r'(<a class="fc"[^>]*>.*?</a>)+', fcs, body, flags=re.S)
    body = re.sub(r'<a class="back" href="([^"]+)"[^>]*>(.*?)</a>', r'<a class="dlk" href="\1">\2</a>', body)
    body = re.sub(r'<p class="cap">', '<p class="dhint">', body)
    body = re.sub(r'<nav class="pn" aria-label="([^"]*)">(.*?)</nav>', lambda m: f'<nav class="opn" aria-label="{m.group(1)}"><small>{m.group(1)}</small>' + m.group(2).replace('aria-current=page', 'aria-current="page"') + '</nav>', body, flags=re.S)
    if pn and 'class="opn"' not in body and '<a class="dlk"' in body:  # 府県ごとに見る（関東の前のページにはあった。関西にも同じく）
        cur = re.search(r'<a class="dlk" href="([^"]+)"', body).group(1)
        nav = '<nav class="opn" aria-label="府県ごとに見る"><small>府県ごとに見る</small>' + ''.join(f'<a href="{u}"' + (' aria-current="page"' if u == cur else '') + f'>{l}</a>' for l, u in pn) + '</nav>'
        body = body.replace('<a class="dlk"', nav + '<a class="dlk"', 1)
    parts = re.split(r'(<h2>.*?</h2>)', body)
    out = '<section class="dsec osp">' + parts[0] + '</section>'
    for i in range(1, len(parts), 2):
        out += '<section class="dsec">' + parts[i] + parts[i + 1] + '</section>'
    return {'h1': h1, 'sub': (f'<b>{E(span)}</b><br>' if span else '') + sub + (f'<br><small>{E(upd)}</small>' if upd else ''), 'html': out, 'js': js}


def keep_head(old_path, new_path, only_ld=False, text=None):
    """前のページの og:image（催しごとの絵）・twitter・構造化データ（Event）を新しいページにも残す（検索・SNSで同じに見える）。"""
    t = text or old(old_path); n = open(new_path, encoding='utf-8').read()
    h = t[:t.index('</head>')]
    keep = '' if only_ld else ''.join(re.findall(r'<meta (?:property="og:(?:type|description|image(?::width|:height)?)"|name="twitter:[a-z]+")[^>]*>', h))
    keep += ''.join(re.findall(r'<script type="application/ld\+json">.*?</script>', h, re.S))
    keep += ''.join(re.findall(r'<meta name="robots"[^>]*>', h))  # 11/25 終わった催しのページは検索に出さない（前のページの noindex を残す）
    if not keep: return
    n = re.sub(r'<meta property="og:image" content="[^"]*">', '', n, count=1)
    n = n.replace('</head>', keep + '</head>', 1)
    open(new_path, 'w', encoding='utf-8').write(n)


# ---------- 開店・閉店の1店のページ（/kaiten/<日付>-<id>）：前のページの中身を新しい部品に（数える・あと何日・送るの script は前のまま） ----------
def shop(path, rel=None):
    t = old(path)
    if not t or 'class="sp-when"' not in t: return None
    b = t[t.index('<body'):]
    js = '\n'.join(re.findall(r'<script>(.*?)</script>', b, re.S))
    b = re.sub(r'<script[^>]*>.*?</script>', '', b, flags=re.S)
    h1 = _txt(re.search(r'<h1>(.*?)</h1>', b, re.S).group(1))
    tp = re.search(r'<div class="tp">(.*?)</div>', b, re.S)
    gn = _txt(re.search(r'<span class="gn">(.*?)</span>', tp.group(1), re.S).group(1)) if tp else ''
    tg = re.search(r'<span class="tag ([a-z]+)">(.*?)</span>', tp.group(1)) if tp else None
    when = re.search(r'<div class="sp-when".*?</div>', b, re.S).group(0)
    i0 = b.index('</div>', b.index('<div class="sp-when"')) + 6
    ends = [b.find(x) for x in ('<div class="ft">', '<p class="sign">') if b.find(x) > 0]
    body = b[i0:min(ends)] if ends else b[i0:]
    al = re.search(r'<nav class="also"[^>]*>(.*?)</nav>', body, re.S)
    if al:  # あわせて見る（関東の前のページにはあった）→ 板
        rel = [(_txt(x[1]), x[0]) for x in re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', al.group(1))]
        body = body.replace(al.group(0), '')
    else:
        rel = [(l, u) for l, u in (rel or [])]
    body = re.sub(r'<figure class="sp-ph">(<img[^>]*>)(?:<i>.*?</i>)?(<figcaption>.*?</figcaption>)</figure>', r'<figure class="kph">\1\2</figure>', body, flags=re.S)
    body = body.replace('<p class="sp-pt">', '<p class="dtx olead">').replace('<p class="sp-chk">', '<p class="dnote">')
    body = re.sub(r'<dl class="sp-dl">(.*?)</dl>', lambda m: '<div class="big">' + ''.join(f'<div class="w"><span>{dt}</span><b>{dd}</b></div>' for dt, dd in re.findall(r'<dt>(.*?)</dt><dd>(.*?)</dd>', m.group(1), re.S)) + '</div>', body, flags=re.S)
    body = re.sub(r'<div class="sp-btn">(.*?)</div>', lambda m: '<div class="oact">' + m.group(1).replace('<a class="p"', '<a class="dbtn"').replace('<a class="s"', '<a class="dbtn2"').replace('<button type="button" class="s"', '<button type="button" class="dbtn2"') + '</div>', body, count=1, flags=re.S)
    body = body.replace('<div class="sp-map">', '<div class="tmap smap">')
    # ほかの新しいお店（カード）→ 板
    def its(m):
        out = []
        for a in re.findall(r'<article class="it[^"]*"[^>]*data-d="([^"]*)"[^>]*>(.*?)</article>', m.group(0), re.S):
            d, h = a
            nm = re.search(r'<h3 class="nm"><a href="([^"]+)"[^>]*>(.*?)</a>', h, re.S)
            if not nm: continue
            tg2 = re.search(r'<span class="tag [a-z]+">(.*?)</span>', h); g2 = re.search(r'<span class="gn">(.*?)</span>', h, re.S)
            out.append(f'<a href="{nm.group(1)}" data-k="1店｜ほかの新しいお店">{nm.group(2)}<small>{int(d[5:7])}/{int(d[8:10])} {_txt(tg2.group(1)) if tg2 else ""}・{_txt(g2.group(1)) if g2 else ""}</small></a>')
        return '<div class="drel">' + ''.join(out) + '</div>'
    body = re.sub(r'(<article class="it.*?</article>\s*)+', its, body, flags=re.S)
    body = re.sub(r'<p class="sp-more"><a href="([^"]+)"([^>]*)>(.*?)\s*→</a></p>', r'<a class="dlk" href="\1"\2>\3</a>', body)
    body = re.sub(r'<div class="kfol"><p>(.*?)</p>(.*?)</div>', lambda m: f'<p class="dhint ksns">{m.group(1)} ' + re.sub(r'<a ', '<a class="ksl" ', m.group(2)) + '</p>', body, flags=re.S)
    body = re.sub(r'<a class="back" href="([^"]+)"[^>]*>(.*?)</a>', r'<a class="dlk" href="\1">\2</a>', body)
    body = re.sub(r'<section class="sp-sec">', '', body).replace('</section>', '')
    parts = re.split(r'(<h2>.*?</h2>)', body)
    out = '<section class="dsec osp">' + when.replace('<div class="sp-when"', '<div class="sp-when swz"') + parts[0] + '</section>'
    for k in range(1, len(parts), 2):
        out += '<section class="dsec">' + parts[k] + parts[k + 1] + '</section>'
    if rel:
        out += '<section class="dsec"><h2>あわせて見る</h2><div class="drel">' + ''.join(f'<a href="{u}" data-k="あわせて：{E(l)}">{E(l)}</a>' for l, u in rel) + '</div></section>'
    sub = E(gn) + (f'・{E(tg.group(2))}' if tg else '')
    return {'h1': h1, 'sub': sub, 'html': out, 'js': js}


# ---------- 買いまわり 1,000円ぽっきり（/kaimawari）：燈の kaimawari.py が作る前のページを新しい部品に（計算・残り時間・ジャンルの切りかえの script は前のまま） ----------
def kaimawari(t):
    if not t or 'id="kn"' not in t: return None
    b = t[t.index('<body'):]
    js = '\n'.join(re.findall(r'<script>(.*?)</script>', b, re.S))
    b = re.sub(r'<script[^>]*>.*?</script>', '', b, flags=re.S)
    sm = re.search(r'<h1>.*?<small>(.*?)</small></h1>', b, re.S); ev = _txt(sm.group(1)) if sm else 'お買い物マラソン'
    up = re.search(r'<p class="up">(.*?)</p>', b, re.S)
    hd = b[b.index('<header'):b.index('</header>')]
    sale = ''.join(re.findall(r'<p class="sale">.*?</p>|<a class="entry[^"]*"[^>]*>.*?</a>|<p class="note">.*?</p>', hd, re.S))
    sale = re.sub(r'<a class="entry[^"]*"', '<a class="dbtn kme entry"', sale).replace('<p class="sale">', '<p class="kms">').replace('<p class="note">', '<p class="dhint">')
    lead = re.search(r'<p class="lead">(.*?)</p>', hd, re.S)
    mid = b[b.index('</header>') + 9:b.index('<footer')]
    mid = re.sub(r'<a class="entry[^"]*"', '<a class="dbtn kme entry"', mid).replace('<a class="cpn nofilt"', '<a class="dbtn2 cpn"')
    mid = mid.replace('<section class="pl', '<section class="dsec kpl pl').replace('<div class="calc">', '<section class="dsec kcalc">')
    mid = re.sub(r'(<section class="dsec kcalc">.*?)</div>', r'\1</section>', mid, count=1, flags=re.S)
    mid = mid.replace('<nav class="tabs"', '<nav class="tabs dchs kmt"').replace('<main>', '<div class="kmp">').replace('</main>', '</div>')
    mid = re.sub(r'<details><summary>(.*?)</summary><p>(.*?)</p></details>', r'<details><summary>\1</summary><div class="ddd">\2</div></details>', mid, flags=re.S)
    mid = mid.replace(' style="color:#A8432F"', '')
    for a_, b_ in (('tx', 'ktx'), ('nm', 'knm'), ('mt', 'kmt2'), ('sh', 'ksh'), ('go', 'kgo')):
        mid = mid.replace(f'<span class="{a_}">', f'<span class="{b_}">')
    ft = re.findall(r'<footer class="foot">(.*?)</footer>', b, re.S)
    note = ''.join(f'<p class="dnote">{x}</p>' for x in re.findall(r'<p>(.*?)</p>', ft[0] if ft else '', re.S))
    mid = re.sub(r'\s*→</a>', '</a>', mid); sale = re.sub(r'\s*→</a>', '</a>', sale)
    html_ = ('<section class="dsec osp kmw">' + sale + (f'<p class="dtx">{lead.group(1)}</p>' if lead else '') + '</section>' +
             '<div class="kmw">' + mid + '</div>' + '<section class="dsec">' + note +
             '<a class="dlk" href="/otoku">お得まとめへ</a><a class="dlk" href="/okaimono">日用品の値段くらべへ</a></section>')
    return {'h1': '買いまわりの1,000円ぽっきり', 'sub': f'<b>{E(ev)}</b><br>1店に数える1,000〜1,199円の物（送料込み）' + (f'<br><small>{up.group(1)}</small>' if up else ''), 'html': html_, 'js': js}
