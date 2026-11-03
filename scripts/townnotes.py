"""関東おでかけリストの地図（site/townnotes/map.js。作り方は月の usagi-fudosan-media tools/townnotes/build_akari.py）。
1) カードの場所を緯度・経度にする  2) 地図つきの試作ページ site/townnotes/index.html を作る  3) 本番の / にも地図を入れる（live()）
page.py のあとに動かす（GitHub Actions。作業環境からは地図の検索サービスにつなげないため）。
- 読む: site/index.html のカード（「地図」ボタンの探す言葉）
- 覚え: data/townnotes-geo.json {探す言葉: [lat, lon, どれで取れたか]}（一度調べた場所は二度と調べない）
- 書く: site/townnotes/geo.json {カード名: [lat, lon, どれで取れたか]}（地図が読む）
取れなかったカードは地図にピンを出さないだけ（リストはそのまま）。"""
import html, json, os, re, sys, time, urllib.parse, urllib.request

SRC = 'site/index.html'
KOYO = 'site/koyo.html'  # 11/2 紅葉ライトアップのページにも地図（オーナー「紅葉、地図動かない」）
ILLUMI = 'site/illumination.html'  # 関東イルミネーションのページ（scripts/illumi.py）。同じ geo.json にピンの場所を足す
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


def illumi_cards(h):
    """イルミのページのカード（li.it の data-p が都県、.nm が名前、a.mp の query が探す言葉）"""
    # 11/2 紅葉のカード（class="it ky"・style が先の物）も読む
    for m in re.finditer(r'<li\b([^>]*\bclass="it[ "][^>]*)>(.*?)</li>', h, re.S):
        dp = re.search(r'data-p="([^"]*)"', m.group(1))
        if not dp:
            continue
        pref, body = html.unescape(dp.group(1)), m.group(2)
        t = re.search(r'<span class="nm">(.*?)</span>', body, re.S)
        if not t:
            continue
        name = text(t.group(1))
        q = re.search(r'class="mp" href="[^"]*?query=([^"&]*)', body)
        place = urllib.parse.unquote(html.unescape(q.group(1))) if q else ''
        yield re.sub(r'\s+', '', name), pref, place.strip(), name.strip()


def all_cards():
    yield from cards(open(SRC, encoding='utf-8').read())
    if os.path.exists(ILLUMI):
        yield from illumi_cards(open(ILLUMI, encoding='utf-8').read())
    if os.path.exists(KOYO):
        yield from illumi_cards(open(KOYO, encoding='utf-8').read())


def main():
    cache = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}
    out, new = {}, 0
    # 11/2 新しい場所が一度に多いと調べるのに10分を超え、公開まで止まった → 1回に調べるのは4分まで。残りは次の回（調べた分は保存されて続きから）
    stop = time.time() + 240
    for k, pref, place, name in all_cards():
        if k in out:
            continue
        ck = pref + '｜' + (place or name)
        today = time.strftime('%Y-%m-%d')
        # 11/3 月：取れなかった場所を毎日調べ直すと1回4分かかり、燈の GitHub の無料枠（月2,000分）を使い切る → 7日に1回だけ調べ直す
        if ck in cache and cache[ck][0] is None and (cache[ck] + [''])[3] <= time.strftime('%Y-%m-%d', time.gmtime(time.time() - 7 * 86400)):
            del cache[ck]
        if ck not in cache and time.time() > stop:
            out[k] = [None, None, 'later']
            continue
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
    # 11/1 試作は役目を終えた（地図は本番に入った）。古い見た目を人目に出さないよう、本番の / へ送る
    open('site/townnotes/index.html', 'w', encoding='utf-8').write('<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0;url=/"><link rel="canonical" href="/"><title>関東おでかけリスト</title><script>location.replace("/")</script></head><body></body></html>')


def live():
    """本番のページ（/）に地図を入れる（10/29 オーナー「本番にして燈にバトンタッチ」）。
    外すときはここを呼ばないだけ。map.js が変わるたびに ?v= が変わるので、スマホに古い地図が残らない"""
    h = open(SRC, encoding='utf-8').read()
    if '/townnotes/map.js' in h:
        return
    v = __import__('hashlib').sha1(open('site/townnotes/map.js', 'rb').read()).hexdigest()[:8]
    h = h.replace('</body>', '<script src="/townnotes/map.js?v=' + v + '" defer></script></body>', 1)
    assert '/townnotes/map.js?v=' in h
    open(SRC, 'w', encoding='utf-8').write(h)


def live_illumi():
    """イルミのページにも地図（10/31 オーナー「燈にも」）。本体は同じで、ページとのつなぎだけ違う map-illumi.js"""
    js = 'site/townnotes/map-illumi.js'
    if not os.path.exists(js):
        return
    v = __import__('hashlib').sha1(open(js, 'rb').read()).hexdigest()[:8]
    # 11/2 紅葉のページにも同じ地図（月の /koyo と同じ）。入っていても ?v= は今の中身にそろえる
    for f in (ILLUMI, KOYO):
        if not os.path.exists(f):
            continue
        h = open(f, encoding='utf-8').read()
        if '/townnotes/map-illumi.js' in h:
            h = re.sub(r'/townnotes/map-illumi\.js\?v=[0-9a-f]+', '/townnotes/map-illumi.js?v=' + v, h)
        else:
            h = h.replace('</body>', '<script src="/townnotes/map-illumi.js?v=' + v + '" defer></script></body>', 1)
        open(f, 'w', encoding='utf-8').write(h)


if __name__ == '__main__':
    try:
        main()
        preview()
        live()
        live_illumi()
    except Exception as e:  # 地図の場所が取れなくても、ページの公開は止めない
        print('townnotes_geo: しっぱい（ページはそのまま公開）', e)
        sys.exit(0)
