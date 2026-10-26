"""楽天の売れ筋を毎晩取って notes/ranking.md に書く（夜の回が商品を選ぶ前に読む）。

10/26 オーナー「レビュー高いけど人気ないとか考えないと1円も生まれない」。
ランキングAPIが使えないときは、同じジャンルをレビュー件数の多い順で取る（代わり）。
"""
import json
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(__file__))
import lib  # noqa: E402

# 主婦さんが買う物のジャンル（楽天のジャンル番号）
GENRES = [
    ("総合", ""),
    ("日用品雑貨", "215783"),
    ("食品", "100227"),
    ("水・ソフトドリンク", "100316"),
    ("キッチン用品", "558944"),
    ("インテリア・寝具・収納", "100804"),
    ("家電", "562637"),
    ("美容・コスメ", "100939"),
    ("ダイエット・健康", "100938"),
    ("キッズ・ベビー", "100533"),
    ("ペット", "101213"),
]
RANKING_URLS = [
    "https://openapi.rakuten.co.jp/ichibaranking/api/IchibaItem/Ranking/20220601",
    "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Ranking/20220601",
]
TOP = 30


def call(url, params):
    env = lib.rakuten_env()
    base = {"format": "json", "formatVersion": 2, "applicationId": env["RAKUTEN_APP_ID"],
            "accessKey": env["RAKUTEN_ACCESS_KEY"], "affiliateId": env["RAKUTEN_AFFILIATE_ID"]}
    base.update({k: v for k, v in params.items() if v != ""})
    origin = os.environ.get("RAKUTEN_ORIGIN") or "https://github.com"
    r = lib.http("GET", url + "?" + urllib.parse.urlencode(base),
                 headers={"Origin": origin, "Referer": origin + "/"})
    if not r or r[0] != 200:
        return None, f"{r[0] if r else 0}: {(r[1] if r else '')[:120]}"
    items = json.loads(r[1]).get("Items") or []
    return [it.get("Item", it) for it in items], ""


def fetch(genre):
    errs = []
    for u in RANKING_URLS:
        items, err = call(u, {"genreId": genre})
        if items:
            return items, "ランキング", ""
        errs.append(err)
    # 代わり：レビュー件数の多い順（ジャンルが要る）
    items, err = call(lib.RAKUTEN_ITEM_URL, {"genreId": genre or "0", "sort": "-reviewCount", "hits": TOP,
                                              "availability": 1})
    if items:
        return items, "レビュー件数順（ランキングAPIが使えなかった）", " / ".join(errs)
    return [], "", " / ".join(errs + [err])


def mark(it):
    rc, ra, p = int(it.get("reviewCount") or 0), float(it.get("reviewAverage") or 0), int(it.get("itemPrice") or 0)
    ok = rc >= 1000 and ra >= 4.0
    if ok and 1000 <= p <= 5000:
        return "◎"
    return "○" if ok else "×"


def main():
    now = lib.now_jst()
    out = ["# 楽天の売れ筋（毎晩 scripts/ranking.py が作る）", "",
           f"取った時刻：{now:%Y-%m-%d %H:%M}（日本時間）",
           "夜の回はPR・HP・ROOMの商品をまずここの◎（レビュー1,000件以上・★4.0以上・1,000〜5,000円）から選ぶ。"
           "○は条件を満たすが値段帯の外。×は使わない。順位が高い＝いま人が買っている。", ""]
    seen = set()
    for name, gid in GENRES:
        items, src, err = fetch(gid)
        out.append(f"## {name}（{src or '取れなかった'}）")
        if err and not items:
            out.append(f"取れなかった理由：{err}")
        out.append("")
        if items:
            out.append("順位｜印｜商品名｜税込｜レビュー｜★｜URL")
        for n, it in enumerate(items[:TOP], 1):
            url = lib._plain_url(it).rstrip("/") + "/"
            code = it.get("itemCode", url)
            dup = "（上と同じ）" if code in seen else ""
            seen.add(code)
            nm = (it.get("itemName") or "").replace("｜", " ").replace("\n", " ")[:45]
            out.append(f"{it.get('rank') or n}｜{mark(it)}｜{nm}{dup}｜{int(it.get('itemPrice') or 0):,}円｜"
                       f"{int(it.get('reviewCount') or 0):,}｜{float(it.get('reviewAverage') or 0):.2f}｜{url}")
        out.append("")
    p = lib.path("notes", "ranking.md")
    with open(p, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out[:40]))


if __name__ == "__main__":
    main()
