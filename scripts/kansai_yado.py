"""月（関西おでかけリスト）のカードごとに、近くの宿を楽天トラベルで探す（10/31 オーナー「楽天は燈のIDを2人で使う」）。

月の地図の場所（geo.json）を読む → 楽天トラベル SimpleHotelSearch（緯度経度・半径3km）で近い順に3つ
→ site/kansai-yado.json（月の試しのページが読む）。覚え data/kansai-yado.json、7日たった所だけ調べ直す。
失敗しても燈のページには関係ない（page.yml で || true）。
"""
import json, math, time, urllib.parse, urllib.request
from datetime import date
from lib import http, rakuten_env, load_json, save_json, path

GEO = "https://usagi-odekake.usagi-fudosan.workers.dev/townnotes/geo.json"
API = "https://openapi.rakuten.co.jp/engine/api/Travel/SimpleHotelSearch/20170426"
MEMO = path("data", "kansai-yado.json")
OUT = path("site", "kansai-yado.json")
MAX_CALLS = 60   # 1回の実行で調べる数（楽天は1秒1回まで）


def dist(a, b, c, d):
    r = math.pi / 180
    x = (d - b) * r * math.cos((a + c) / 2 * r)
    return 6371 * math.hypot(x, (c - a) * r)


def search(env, lat, lon, origin):
    q = {"format": "json", "formatVersion": 2, "applicationId": env["RAKUTEN_APP_ID"],
         "accessKey": env["RAKUTEN_ACCESS_KEY"], "affiliateId": env["RAKUTEN_AFFILIATE_ID"],
         "latitude": lat, "longitude": lon, "datumType": 1, "searchRadius": 3, "hits": 10}
    for wait in (2, 4, 0):
        st, txt, _ = http("GET", API + "?" + urllib.parse.urlencode(q),
                          headers={"Origin": origin, "Referer": origin + "/"})
        if st != 429 or not wait:
            break
        time.sleep(wait)
    if st == 404:
        return []          # 3km 以内に宿がない
    if st != 200:
        raise RuntimeError(f"楽天トラベル {st}: {(txt or '')[:150]}")
    hs = []
    for h in json.loads(txt).get("hotels") or []:
        b = None
        for part in (h if isinstance(h, list) else [h]):
            if isinstance(part, dict) and "hotelBasicInfo" in part:
                b = part["hotelBasicInfo"]
            elif isinstance(part, dict) and "hotelNo" in part:
                b = part
        if not b or not b.get("latitude"):
            continue
        km = dist(lat, lon, float(b["latitude"]), float(b["longitude"]))
        hs.append({"n": b.get("hotelName", ""), "u": b.get("hotelInformationUrl", ""),
                   "km": round(km, 1), "r": b.get("reviewAverage"), "min": b.get("hotelMinCharge")})
    hs.sort(key=lambda x: x["km"])
    return [x for x in hs if x["u"]][:3]


def main():
    import os
    env = rakuten_env()
    origin = os.environ.get("RAKUTEN_ORIGIN") or "https://github.com"
    with urllib.request.urlopen(GEO, timeout=30) as r:
        geo = json.load(r)
    memo = load_json(MEMO, {}) or {}
    today = date.today()
    calls = 0
    for name, v in geo.items():
        lat, lon = float(v[0]), float(v[1])
        m = memo.get(name)
        fresh = m and m.get("ll") == [lat, lon] and (today - date.fromisoformat(m["t"])).days < 7
        if fresh or calls >= MAX_CALLS:
            continue
        try:
            memo[name] = {"t": today.isoformat(), "ll": [lat, lon], "h": search(env, lat, lon, origin)}
        except Exception as e:
            print("×", name, e)
            break
        calls += 1
        time.sleep(1.1)
    memo = {k: v for k, v in memo.items() if k in geo}
    save_json(MEMO, memo)
    out = {k: v["h"] for k, v in memo.items() if v["h"]}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"関西の宿: 調べた {calls} / 宿あり {len(out)} / 場所 {len(geo)}")


if __name__ == "__main__":
    main()
