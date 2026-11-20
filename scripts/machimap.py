"""11/20 owner「同じ街の相場・実家・解体を1つにまとめる」→ 街のページの上のタブ（skin.js townTabs）が使う表を作る。
python3 tools/shin/machimap.py [サイトの場所]   （関西＝links・関東＝akari-auto/site。同じファイルを akari scripts/machimap.py に写している）
出す物：<サイト>/shin/machi.json = {"t":{街id:[街の名前, 実家ページあり(1/0), 解体の市slug or ""]}, "k":{解体の市slug:[市の名前,[街id…]]}}"""
import os, re, sys, json
S = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'links')
T = lambda p: re.search(r'<title>([^<｜|]*)', open(p, encoding='utf-8').read())
kai = {}
for f in sorted(os.listdir(S)):
    m = re.match(r'kaitai-([a-z]+)\.html$', f)
    if not m or m.group(1) == 'ranking': continue
    t = T(os.path.join(S, f)); n = re.match(r'(.+?[市区町村])の', t.group(1)) if t else None
    if n: kai[m.group(1)] = n.group(1)
tw, ks = {}, {}
for f in sorted(os.listdir(os.path.join(S, 'machi'))):
    m = re.match(r'([a-z]+-\d+)\.html$', f)
    if not m: continue
    i = m.group(1); t = T(os.path.join(S, 'machi', f))
    if not t: continue
    name = re.split(r'の(地価|実家)', t.group(1))[0].strip()
    jk = os.path.exists(os.path.join(S, 'jikka', f))
    k = ''
    for p in ([os.path.join(S, 'jikka', f)] if jk else []) + [os.path.join(S, 'machi', f)]:
        h = re.search(r'href="/kaitai-([a-z]+)"', open(p, encoding='utf-8').read())
        if h and h.group(1) in kai: k = h.group(1); break
    if not k:  # 名前の頭で当てる（例：千葉市中央区 → 千葉市）
        best = max((c for c, n in kai.items() if name.startswith(n)), key=lambda c: len(kai[c]), default='')
        k = best
    tw[i] = [name, 1 if jk else 0, k]
    if k: ks.setdefault(k, [kai[k], []])[1].append(i)
json.dump({'t': tw, 'k': ks}, open(os.path.join(S, 'shin', 'machi.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('machi.json', len(tw), '街', sum(1 for v in tw.values() if v[2]), '街に解体の市', len(ks), '/', len(kai), '市')
