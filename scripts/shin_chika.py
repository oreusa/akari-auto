"""新しいHP：地価ランキング（links/shin/rk.js が出す）。関西と関東で同じファイル（燈 akari-auto scripts/shin_chika.py は この写し）。
11/23 owner「hpと同じじゃないのあるんじゃない？全部やり変えて」→ 前のページ（頭をかぶせただけ）を、この土台で作り直した。
数字は前のページを作る機械と同じ元（関西 links/assets/towns.json・tools/chika/make.py、関東 site/assets/towns.json・data/kanto_chika/）。
前のページは消さない（毎朝ほかの機械が作る。よくある質問・出典はそこから読む）。"""
import html, json, os, re

E = html.escape


def acc(rows):
    return ''.join(f'<details><summary>{E(q)}</summary><div class="ddd">{a}</div></details>' for q, a in rows)


def old_faq(path):
    """前のページの よくある質問（そのまま）。もう新しい形に書き替えた後なら kyu/ に残した前のページから"""
    if os.path.exists(path) and '/shin/shin.css' in open(path, encoding='utf-8').read():
        path = os.path.join(os.path.dirname(path), 'kyu', os.path.basename(path))
    if not os.path.exists(path): return []
    t = open(path, encoding='utf-8').read()
    out = []
    for q, a in re.findall(r'<details[^>]*>\s*<summary[^>]*>(.*?)</summary>(.*?)</details>', t, re.S):
        q = html.unescape(re.sub('<[^>]+>', '', q)).strip()
        a = re.sub(r'</?(div|p)[^>]*>', '', a).strip()
        if q: out.append((q, a))
    return out


def page(h1, sub, an, rows, tabs, groups=None, avg=None, srcs=(), faq=(), rel=(), ex='', note='', also=None):
    """rows=[{n,s,id,p,k,v:{tab:[前年,今年]}}]。groups=[{k,l,h}]（h は前のページの #osaka などの印）"""
    srch = ''.join(f'<li><a href="{E(u)}" rel="noopener" target="_blank">{E(t)}</a></li>' for t, u in srcs)
    foot = ((f'<section class="dsec"><h2>{E(also[0])}</h2><a class="dbtn2" href="{also[1]}" data-k="地価｜{E(also[0])}">{E(also[2])}</a></section>' if also else '')
            + (f'<section class="dsec"><h2>よくある質問</h2>{acc(faq)}</section>' if faq else '')
            + f'<section class="dsec"><h2>数字の出どころ</h2><p class="dnote">{note}</p><ul class="dsrc">{srch}</ul></section>'
            + '<section class="dsec"><h2>あわせて見る</h2><div class="drel">' + ''.join(f'<a href="{u}" data-k="地価｜関連｜{E(t)}">{E(t)}<small>{E(s)}</small></a>' for t, u, s in rel) + '</div></section>')
    # 検索の機械にも見えるように、1つめのタブの順位を HTML のまま（JS が描くと入れ替わる）
    tk = tabs[0]['k']
    srt = sorted([r for r in rows if r['v'].get(tk)], key=lambda r: -r['v'][tk][1])
    pre = '<ol>' + ''.join(f'<li>{E(r["n"])}（{E(r.get("p", ""))}）住宅地 {r["v"][tk][1]:+.1f}%</li>' for r in srt[:400]) + '</ol>' + foot
    return {'h1': h1, 'sub': sub, 'an': an, 'tabs': tabs, 'groups': groups or [], 'rows': rows, 'avg': avg or {}, 'ex': ex, 'foot': foot, 'html': pre}


# ---------- 関西 ----------
def build(write, L, R, URL, cfg):
    src = open(os.path.join(R, 'tools/fudosan_list/towns.py'), encoding='utf-8').read()
    PREFS = re.findall(r'\("([^"]+)", "([a-z]+)", "[A-Z]+", "#[0-9A-F]{6}", "([^"]+)", "([^"]+)", "[^"]+"\)', src)
    towns = json.load(open(os.path.join(L, 'assets', 'towns.json'), encoding='utf-8'))
    towns = towns.get('towns', towns) if isinstance(towns, dict) else towns
    rows = [{'n': t['n'], 's': t.get('s') or t['n'], 'id': t['id'], 'p': t['p'], 'k': t.get('k', ''), 'v': {'r': [t.get('r7'), t['r8']]}} for t in towns if t.get('r8') is not None]
    groups = [{'k': 'all', 'l': '関西ぜんぶ'}] + [{'k': p, 'l': p, 'h': c} for p, c, _, _ in PREFS]
    up = sum(1 for r in rows if r['v']['r'][1] > 0)
    rel = [['家と土地の相場', '/fudosan-list', '街ごとの売れた値段'], ['まちランキング', '/ranking', '駅・人口の順位も'], ['いくらで売れる？', '/ikura', '30秒で目安'], ['実家・空き家', '/jikka/', '売る・片付ける前に']]
    note = '令和8年地価公示（2026年1月1日時点）の住宅地の、市区町村ごとの平均の変動率です。1軒ずつの値段ではありません。'
    d = page('関西 地価ランキング', f'住宅地の地価が1年でどれだけ動いたか。{len(rows)}の市区町村を上がり幅の大きい順に（令和8年地価公示）。', '関西', rows,
             [{'k': 'r', 'l': '住宅地'}], groups, None, [(s, u) for _, _, s, u in PREFS], old_faq(os.path.join(L, 'chika-kansai.html')), rel, '寝屋川市', note,
             ['大阪市24区は商業地も', '/chika-osaka', '大阪市24区 地価ランキング（住宅地・商業地）'])
    c = dict(cfg('/chika-kansai', f'関西{len(rows)}の市区町村の住宅地の地価の上がり幅ランキング（令和8年地価公示）。上がったのは{up}。うちの街は何位？で探せます。'))
    URL['chika-kansai'] = '/chika-kansai'
    write('chika-kansai', f'関西 地価ランキング2026｜{len(rows)}の市区町村の住宅地（令和8年地価公示）｜TOWN NOTE', c, d, js='rk')

    # 大阪市24区（住宅地・商業地）
    ms = open(os.path.join(R, 'tools/chika/make.py'), encoding='utf-8').read()
    D = dict((k, tuple(float(x) for x in v.split(','))) for k, v in re.findall(r'"([^"]+区)": \(([-\d., ]+)\)', ms))
    AVG = tuple(float(x) for x in re.search(r'AVG = \(([-\d., ]+)\)', ms).group(1).split(','))
    SRC = re.search(r'SRC = "([^"]+)"', ms).group(1)
    ids = {t['n']: t for t in towns}
    rows = []
    for n, (r7, r8, c7, c8) in D.items():
        t = ids.get('大阪市' + n, {})
        rows.append({'n': n, 's': n, 'id': t.get('id', ''), 'p': '大阪市', 'k': t.get('k', ''), 'v': {'r': [r7, r8], 'c': [c7, c8]}})
    note = '大阪府「令和8年地価公示 報道資料」p.5 市区町村別対前年平均変動率表（2026年1月1日時点）。区の中の調査地点の平均の変動率で、1軒ずつの値段ではありません。'
    rel = [['関西 地価ランキング', '/chika-kansai', '205の市区町村'], ['家と土地の相場', '/fudosan-list', '街ごとの売れた値段'], ['まちランキング', '/ranking', '駅・人口の順位も'], ['いくらで売れる？', '/ikura', '30秒で目安']]
    d = page('大阪市24区 地価ランキング', '住宅地と商業地の地価が1年でどれだけ動いたか。24区を上がり幅の大きい順に（令和8年地価公示）。', '大阪市', rows,
             [{'k': 'r', 'l': '住宅地'}, {'k': 'c', 'l': '商業地'}], None, {'all': {'r': [AVG[0], AVG[1]], 'c': [AVG[2], AVG[3]]}},
             [('大阪府「令和8年地価公示 報道資料」', SRC)], old_faq(os.path.join(L, 'chika-osaka.html')), rel, '都島区', note)
    c = dict(cfg('/chika-kansai', '大阪市24区の住宅地・商業地の地価の上がり幅ランキング（令和8年地価公示）。'))
    URL['chika-osaka'] = '/chika-osaka'
    write('chika-osaka', '大阪市24区 地価ランキング2026｜住宅地・商業地の上がり幅｜TOWN NOTE', c, d, js='rk')


# ---------- 関東（燈 scripts/shin_kanto.py の docs() から。write(fname, url, title, cfg, data, js, desc)） ----------
AVG23 = {'r': [7.9, 9.0]}  # 東京都財務局 区市町村別用途別対前年変動率表「区部全域」住宅地 令和7年・令和8年


def build_kanto(write, S, R, cfg):
    import csv
    K = os.path.join(R, 'data', 'kanto_chika')
    SRC = json.load(open(os.path.join(K, 'sources.json'), encoding='utf-8'))
    towns = json.load(open(os.path.join(S, 'assets', 'towns.json'), encoding='utf-8'))
    towns = towns.get('towns', towns) if isinstance(towns, dict) else towns
    rows = [{'n': t['n'], 's': t.get('s') or t['n'], 'id': t['id'], 'p': t['p'], 'k': t.get('k', ''), 'v': {'r': [t.get('r7'), t['r8']]}} for t in towns if t.get('r8') is not None]
    groups = [{'k': 'all', 'l': '関東ぜんぶ'}] + [{'k': s['p'], 'l': s['p'], 'h': s['csv']} for s in SRC]
    up = sum(1 for r in rows if r['v']['r'][1] > 0)
    rel = [['家と土地の相場', '/fudosan-list', '街ごとの売れた値段'], ['まちランキング', '/ranking', '人口の順位も'], ['いくらで売れる？', '/ikura', '30秒で目安'], ['実家・空き家', '/jikka/', '売る・片付ける前に']]
    note = '令和8年地価公示（2026年1月1日時点）の住宅地の、市区町村ごとの平均の変動率です。1軒ずつの値段ではありません。'
    srcs = []
    for s in SRC:
        srcs.append((s['src'].split('（')[0], s['url']))
    d = page('関東 地価ランキング', f'住宅地の地価が1年でどれだけ動いたか。{len(rows)}の市区町村を上がり幅の大きい順に（令和8年地価公示）。', '関東', rows,
             [{'k': 'r', 'l': '住宅地'}], groups, None, srcs, old_faq(os.path.join(S, 'chika-kanto.html')), rel, '川口市', note,
             ['東京23区は商業地も', '/chika-tokyo', '東京23区 地価ランキング（住宅地・商業地）'])
    write('chika-kanto.html', '/chika-kanto', f'関東 地価ランキング2026｜{len(rows)}の市区町村の住宅地（令和8年地価公示）｜LIFE NOTE', cfg('/chika-kanto'), d, 'rk',
          f'関東{len(rows)}の市区町村の住宅地の地価の上がり幅ランキング（令和8年地価公示）。上がったのは{up}。うちの街は何位？で探せます。')

    # 東京23区（住宅地・商業地）
    com = {r[0]: (float(r[1]), float(r[2])) for r in csv.reader(open(os.path.join(K, 'tokyo23_shogyo.csv'), encoding='utf-8'))}
    tk = {t['n']: t for t in towns if t['p'] == '東京'}
    rows = []
    for n, c in com.items():
        if n == '区部全域' or n not in tk: continue
        t = tk[n]
        rows.append({'n': n, 's': n, 'id': t['id'], 'p': '東京23区', 'k': t.get('k', ''), 'v': {'r': [t.get('r7'), t['r8']], 'c': list(c)}})
    avg = {'all': {'r': AVG23['r'], 'c': list(com['区部全域'])}}
    rr = sorted(rows, key=lambda r: -r['v']['r'][1]); cc = sorted(rows, key=lambda r: -r['v']['c'][1])
    dn_r = [r for r in rows if r['v']['r'][1] < r['v']['r'][0]]; dn_c = [r for r in rows if r['v']['c'][1] < r['v']['c'][0]]
    pm = lambda v: f'{v:+.1f}%'
    faq = [('東京23区で住宅地の地価がいちばん上がった区は？', f'令和8年地価公示（1月1日時点）では、{rr[0]["n"]}の{pm(rr[0]["v"]["r"][1])}がいちばん大きく、2位は{rr[1]["n"]}（{pm(rr[1]["v"]["r"][1])}）、3位は{rr[2]["n"]}（{pm(rr[2]["v"]["r"][1])}）でした。商業地の1位は{cc[0]["n"]}（{pm(cc[0]["v"]["c"][1])}）です。'),
           ('23区の平均はどれくらい？', f'住宅地の平均は{pm(AVG23["r"][1])}（前の年は{pm(AVG23["r"][0])}）、商業地の平均は{pm(com["区部全域"][1])}（前の年は{pm(com["区部全域"][0])}）です。23区すべてで住宅地・商業地ともプラスでした。' if all(r['v']['r'][1] > 0 and r['v']['c'][1] > 0 for r in rows) else f'住宅地の平均は{pm(AVG23["r"][1])}、商業地の平均は{pm(com["区部全域"][1])}です。'),
           ('前の年より上がり幅が小さくなった区は？', '住宅地では' + ('・'.join(f'{r["n"]}（{pm(r["v"]["r"][0])}→{pm(r["v"]["r"][1])}）' for r in dn_r) or 'ありません') + '。商業地では' + ('・'.join(f'{r["n"]}（{pm(r["v"]["c"][0])}→{pm(r["v"]["c"][1])}）' for r in dn_c) or 'ありません') + '。'),
           ('この数字で、わが家の値段がわかりますか？', 'わかりません。区の中の調査地点の平均の上がり幅で、1軒ずつの値段ではありません。家の値段は、場所・広さ・築年数などで大きく変わります。')]
    note = '東京都財務局「令和8年地価公示 区市町村別用途別対前年変動率表」（2026年1月1日時点）。区の中の調査地点の平均の変動率で、1軒ずつの値段ではありません。'
    t0 = next(s for s in SRC if s['p'] == '東京')
    rel = [['関東 地価ランキング', '/chika-kanto', f'{len(towns)}の市区町村'], ['家と土地の相場', '/fudosan-list', '街ごとの売れた値段'], ['まちランキング', '/ranking', '人口の順位も'], ['いくらで売れる？', '/ikura', '30秒で目安']]
    d = page('東京23区 地価ランキング', '住宅地と商業地の地価が1年でどれだけ動いたか。23区を上がり幅の大きい順に（令和8年地価公示）。', '東京23区', rows,
             [{'k': 'r', 'l': '住宅地'}, {'k': 'c', 'l': '商業地'}], None, avg,
             [('東京都財務局「令和8年地価公示 区市町村別用途別対前年変動率表」', t0['url']), ('同「令和7年地価公示 区市町村別用途別対前年変動率表」', t0['url_r7'])], faq, rel, '世田谷区', note)
    write('chika-tokyo.html', '/chika-tokyo', '東京23区 地価ランキング2026｜住宅地・商業地の上がり幅｜LIFE NOTE', cfg('/chika-kanto'), d, 'rk',
          f'東京23区の住宅地・商業地の地価の上がり幅ランキング（令和8年地価公示）。1位は{rr[0]["n"]}の{pm(rr[0]["v"]["r"][1])}。')
    return ['/chika-kanto', '/chika-tokyo']
