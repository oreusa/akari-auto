"""関東おでかけリストの地図（site/townnotes/map.js。作り方は月の usagi-fudosan-media tools/townnotes/build_akari.py）。
1) カードの場所を緯度・経度にする  2) 地図つきの試作ページ site/townnotes/index.html を作る（本番の / は変えない）
page.py のあとに動かす（GitHub Actions。作業環境からは地図の検索サービスにつなげないため）。
- 読む: site/index.html のカード（「地図」ボタンの探す言葉）
- 覚え: data/townnotes-geo.json {探す言葉: [lat, lon, どれで取れたか]}（一度調べた場所は二度と調べない）
- 書く: site/townnotes/geo.json {カード名: [lat, lon, どれで取れたか]}（地図が読む）
取れなかったカードは地図にピンを出さないだけ（リストはそのまま）。"""
import html, json, os, re, sys, time, urllib.parse, urllib.request

SRC = 'site/index.html'
CACHE = 'data/townnotes-geo.json'
OUT = 'site/townnotes/geo.json'
# 都県の大まかな範囲（南, 北, 西, 東）。外れた答えは使わない
BOX = {'東京': (35.48, 35.92, 138.92, 139.93), '神奈川': (35.12, 35.68, 138.91, 139.80), '埼玉': (35.75, 36.29, 138.71, 139.91),
       '千葉': (34.89, 36.11, 139.73, 140.88), '茨城': (35.73, 36.96, 139.68, 140.86), '栃木': (36.19, 37.16, 139.32, 140.30),
       '群馬': (35.98, 37.06, 138.39, 139.68), '': (34.89, 37.16, 138.39, 140.88)}
FULL = {'東京': '東京都', '神奈川': '神奈川県', '埼玉': '埼玉県', '千葉': '千葉県', '茨城': '茨城県', '栃木': '栃木県', '群馬': '群馬県'}
UA = {'User-Agent': 'usagi-life-notes-map/0.1 (github.com/oreusa/akari-auto)'}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        return json.load(r)


def nomi(q):
    time.sleep(1.1)  # 決まり：1秒に1回まで
    try:
        r = get('https://nominatim.openstreetmap.org/search?format=json&limit=3&countrycodes=jp&q=' + urllib.parse.quote(q))
    except Exception as e:
        print('nominatim err', q, e)
        return []
    return [(float(x['lat']), float(x['lon'])) for x in r]


def photon(q):
    """名前でさがす（店・施設の名前に強い）"""
    time.sleep(0.5)
    try:
        r = get('https://photon.komoot.io/api/?limit=3&q=' + urllib.parse.quote(q))
    except Exception as e:
        print('photon err', q, e)
        return []
    return [(f['geometry']['coordinates'][1], f['geometry']['coordinates'][0]) for f in r.get('features', [])]


def gsi(q):
    try:
        r = get('https://msearch.gsi.go.jp/address-search/AddressSearch?q=' + urllib.parse.quote(q))
    except Exception as e:
        print('gsi err', q, e)
        return []
    return [(x['geometry']['coordinates'][1], x['geometry']['coordinates'][0]) for x in r[:3]]


def inside(p, ll):
    b = BOX.get(p)
    return b and b[0] <= ll[0] <= b[1] and b[2] <= ll[1] <= b[3]


def text(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s))


def cards(h):
    """(カード名の鍵, 都県, 探す言葉, 名前)。鍵は地図の key()（.t の文字から空白を抜いた物）と同じ"""
    for m in re.finditer(r'<div class="card it" data-pref="([^"]*)"[^>]*>(.*?)<svg class="arw"', h, re.S):
        pref, body = html.unescape(m.group(1)), m.group(2)
        t = re.search(r'<div class="t">(.*?)</div>', body, re.S)
        if not t:
            continue
        name = text(t.group(1))
        k = re.sub(r'\s+', '', name)
        q = re.search(r'class="mp" href="[^"]*?query=([^"&]*)', body)
        place = urllib.parse.unquote(html.unescape(q.group(1))) if q else ''
        yield k, pref, place.strip(), name.strip()


def main():
    h = open(SRC, encoding='utf-8').read()
    cache = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}
    out, new = {}, 0
    for k, pref, place, name in cards(h):
        if k in out:
            continue
        ck = pref + '｜' + (place or name)
        today = time.strftime('%Y-%m-%d')
        if ck in cache and cache[ck][0] is None and (cache[ck] + [''])[3] != today:
            del cache[ck]  # 取れなかった場所は1日1回だけ調べなおす
        if ck not in cache:
            got = None
            base = place.replace(' ' + pref, '').strip() if place else ''
            tries = [('place', nomi, place), ('place', gsi, base), ('place', photon, base), ('name', nomi, (name + ' ' + FULL.get(pref, '')).strip()),
                     ('place', nomi, (base + ' ' + FULL.get(pref, '')).strip() if base else ''), ('place', photon, base.split(' ')[0] if base else '')]
            for kind, fn, q in tries:
                if not q:
                    continue
                ll = next((x for x in fn(q) if inside(pref, x)), None)
                if ll:
                    got = [round(ll[0], 5), round(ll[1], 5), kind]
                    break
            cache[ck] = got or [None, None, 'none', today]
            new += 1
            print(ck, cache[ck])
        out[k] = cache[ck][:3]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    json.dump(cache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)
    ok = sum(1 for v in out.values() if v[0] is not None)
    print(f'地図の場所: {ok}/{len(out)} 件（新しく調べた {new} 件）')


def preview():
    """試作ページ：本番と同じ中身に地図を足しただけ。/townnotes/ で見られる（数えない・検索に出さない）"""
    h = open(SRC, encoding='utf-8').read()
    h = re.sub(r'(src|href)="(?!https?:|#|/|data:|mailto:)([^"]+)"', r'\1="../\2"', h)
    h = h.replace('if(!a||!navigator.sendBeacon)return;', 'return;')  # 試作で押しても数えない
    h = re.sub(r'<title>([^<]*)</title>', r'<title>\1（地図つき試作）</title><meta name="robots" content="noindex">', h, 1)
    v = __import__('hashlib').sha1(open('site/townnotes/map.js', 'rb').read()).hexdigest()[:8]
    badge = ('<div style="position:fixed;top:8px;left:8px;z-index:50;font-family:Jost,sans-serif;font-size:10px;letter-spacing:.2em;'
             'background:#2B2622;color:#fff;padding:2px 8px;pointer-events:none">PROTOTYPE</div>')
    h = h.replace('</body>', badge + '<script src="map.js?v=' + v + '" defer></script></body>', 1)
    assert 'src="map.js?v=' in h
    open('site/townnotes/index.html', 'w', encoding='utf-8').write(h)


if __name__ == '__main__':
    try:
        main()
        preview()
    except Exception as e:  # 地図の場所が取れなくても、ページの公開は止めない
        print('townnotes_geo: しっぱい（ページはそのまま公開）', e)
        sys.exit(0)
