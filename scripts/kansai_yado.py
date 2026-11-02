"""月（関西おでかけリスト）のカードごとに、近くの宿を楽天トラベルで探す（10/31 オーナー「楽天は燈のIDを2人で使う」）。

月の地図の場所（geo.json）を読む → 楽天トラベル SimpleHotelSearch（緯度経度・半径3km）で近い順に3つ
→ site/kansai-yado.json（月の試しのページが読む）。覚え data/kansai-yado.json、7日たった所だけ調べ直す。
失敗しても燈のページには関係ない（page.yml で || true）。
"""
import json, math, re, time, unicodedata, urllib.parse, urllib.request
from datetime import date
# 10/31 宿の名前のうしろの「<淡路島>」「 ^」は楽天の付け足しなので消す（ページで見にくい）
def hname(n):
    return re.sub(r"\s*(<[^<>]*>|\^)\s*$", "", unicodedata.normalize("NFKC", n or "")).strip()
from lib import BROWSER_UA, http, rakuten_env, load_json, save_json, path

GEO = "https://usagi-odekake.usagi-fudosan.workers.dev/townnotes/geo.json"
API = "https://openapi.rakuten.co.jp/engine/api/Travel/SimpleHotelSearch/20170426"
VER = 2         # 選び方を変えたら上げる（覚えを全部調べ直す）
# 泊まりがけで行く場所だけに付ける：大きな街の真ん中から20km以上（10/31 月）
# 10/31 オーナー「燈のも変えるよね？」→ 燈の関東も同じ形（東京駅・新宿・横浜から25km以上）
REGIONS = {
    "kansai": {"name": "関西", "geo": GEO, "centers": [(34.7025, 135.4959), (34.6659, 135.5013), (34.9858, 135.7588), (34.6951, 135.1979)], "far": 20},
    "kanto": {"name": "関東", "geo": path("site", "townnotes", "geo.json"), "centers": [(35.6812, 139.7671), (35.6896, 139.7006), (35.4658, 139.6223)], "far": 25},
}
CENTERS, FAR_KM = REGIONS["kansai"]["centers"], 20
MAX_CALLS = 150   # 1回の実行で調べる数（楽天は1秒1回まで）


def dist(a, b, c, d):
    r = math.pi / 180
    x = (d - b) * r * math.cos((a + c) / 2 * r)
    return 6371 * math.hypot(x, (c - a) * r)


def far(ll):
    return min(dist(ll[0], ll[1], a, b) for a, b in CENTERS) >= FAR_KM


def search(env, lat, lon, origin, keep=False):
    q = {"format": "json", "formatVersion": 2, "applicationId": env["RAKUTEN_APP_ID"],
         "accessKey": env["RAKUTEN_ACCESS_KEY"], "affiliateId": env["RAKUTEN_AFFILIATE_ID"],
         "latitude": lat, "longitude": lon, "datumType": 1, "searchRadius": 3, "hits": 30}
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
        hs.append({"n": hname(b.get("hotelName", "")), "u": b.get("hotelInformationUrl", ""),
                   "km": round(km, 1), "r": b.get("reviewAverage"), "rc": b.get("reviewCount"),
                   "min": b.get("hotelMinCharge"), "_ll": (float(b["latitude"]), float(b["longitude"]))})
    # 10/31 オーナー「改善したい所ない？」→ 民泊・評価なしを外し、評価の高い順（同じなら近い順）
    ok = [x for x in hs if x["u"] and "民泊" not in x["n"] and (x["r"] or 0) >= 3.5 and (x["rc"] or 0) >= 10 and x["min"]]
    ok.sort(key=lambda x: (-float(x["r"]), x["km"]))
    if not keep:
        for x in ok:
            x.pop("_ll", None)
    return ok[:3] if not keep else ok


def search_wide(env, lat, lon, origin):
    """11/2 オーナー「全部」（案2）: 3km に良い宿がない遠い会場（貴志川・馬見・ハーベストの丘など）は、
    まわり4方向（約4km先）でも探して、会場から8km以内の宿を出す。km は会場からの近さ。"""
    hs = search(env, lat, lon, origin)
    if hs:
        return hs
    seen, out = set(), []
    dl = 4 / 111
    for a, b in ((dl, 0), (-dl, 0), (0, dl / math.cos(lat * math.pi / 180)), (0, -dl / math.cos(lat * math.pi / 180))):
        time.sleep(1.1)
        for x in search(env, lat + a, lon + b, origin, keep=True):
            if x["u"] in seen:
                continue
            seen.add(x["u"])
            x = dict(x)
            x["km"] = round(dist(lat, lon, *x["_ll"]), 1)
            out.append(x)
    out = [x for x in out if x["km"] <= 8]
    out.sort(key=lambda x: (-float(x["r"]), x["km"]))
    for x in out:
        x.pop("_ll", None)
    return out[:3]



def main(region="kansai"):
    import os
    global CENTERS, FAR_KM
    R = REGIONS[region]
    CENTERS, FAR_KM = R["centers"], R["far"]
    MEMO, OUT = path("data", f"{region}-yado.json"), path("site", f"{region}-yado.json")
    env = rakuten_env()
    origin = os.environ.get("RAKUTEN_ORIGIN") or "https://github.com"
    if R["geo"].startswith("http"):
        st, txt, _ = http("GET", R["geo"], headers={"User-Agent": BROWSER_UA})  # 普通の名乗りだと Cloudflare が 403
        if st != 200:
            raise RuntimeError(f"geo.json が読めない {st}")
        geo = json.loads(txt)
    else:
        geo = load_json(R["geo"], {}) or {}
    geo = {k: v for k, v in geo.items() if v and v[0] is not None}
    memo = load_json(MEMO, {}) or {}
    today = date.today()
    calls = 0
    for name, v in geo.items():
        lat, lon = float(v[0]), float(v[1])
        m = memo.get(name)
        if m and m.get("h"):
            for x in m["h"]:
                x["n"] = hname(x["n"])
        fresh = m and (m.get("h") or m.get("w")) and m.get("v") == VER and m.get("ll") == [lat, lon] and (today - date.fromisoformat(m["t"])).days < 7
        if fresh or calls >= MAX_CALLS or not far([lat, lon]):  # 街なかは調べない（楽天の呼び出しを減らす）
            continue
        try:
            memo[name] = {"v": VER, "t": today.isoformat(), "ll": [lat, lon], "w": 1, "h": search_wide(env, lat, lon, origin)}
        except Exception as e:
            print("×", name, e)
            break
        calls += 1
        time.sleep(1.1)
    memo = {k: v for k, v in memo.items() if k in geo and far(v["ll"])}
    save_json(MEMO, memo)
    out = {k: v["h"] for k, v in memo.items() if v["h"] and far(v["ll"])}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{R['name']}の宿: 調べた {calls} / 宿あり {len(out)} / 場所 {len(geo)}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else "kansai")
