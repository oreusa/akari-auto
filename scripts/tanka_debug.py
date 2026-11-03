"""tanka.py の新しい種類が0件・1件になる理由を見る（11/3。ログに出すだけ・何も書かない）。"""
import os, sys, time, collections
sys.path.insert(0, os.path.dirname(__file__))
import lib, tanka  # noqa: E402

only = sys.argv[1:] or [c[0] for c in tanka.CATS if c[0] in tanka.KIND] + ["tp"]
for cat in tanka.CATS:
    key, _, kw, gid, unit, ng, (lo, hi) = cat
    if key not in only:
        continue
    why = collections.Counter(); samp = collections.defaultdict(list); rcs = []
    for page in (1, 2):
        q = {"keyword": kw, "postageFlag": 1, "availability": 1, "sort": "-reviewCount", "hits": 30, "page": page}
        items, err = lib._rakuten_search(q); time.sleep(1.1)
        for it in items or []:
            name = it.get("itemName") or ""; rc = int(it.get("reviewCount") or 0); av = float(it.get("reviewAverage") or 0)
            price = int(it.get("itemPrice") or 0)
            if any(w in name for w in ng): r = "ng:" + next(w for w in ng if w in name)
            elif tanka.MUST.get(key) and tanka.MUST[key] not in name: r = "must"
            else:
                am = tanka.amount(key, name)
                if not am: r = "amount"
                elif not (lo <= price / am[0] <= hi): r = f"range({price/am[0]:.0f})"
                elif rc < 1000 or av < 4.0: r = "review"; rcs.append(rc)
                else: r = "OK"
            why[r.split("(")[0]] += 1
            if len(samp[r.split("(")[0]]) < 6: samp[r.split("(")[0]].append(f"{r} rc={rc} av={av} {price}円 | {name[:110]}")
    print(f"\n=== {key} {dict(why)} review落ちrc={sorted(rcs, reverse=True)[:10]}")
    for k, v in samp.items():
        if k == "OK" or k.startswith("ng"): continue
        for s in v: print("  ", s)

# Yahoo! の鍵が効くか（11/3 オーナーが鍵を入れた）。鍵そのものは出さない
import json, urllib.parse, urllib.request  # noqa: E402
ap = os.environ.get("YAHOO_APP_ID", "").strip()
print("\n=== yahoo 鍵:", "あり" if ap else "なし", len(ap))
if ap:
    for cat in tanka.CATS[:3] + [c for c in tanka.CATS if c[0] in ("detergent", "diaper")]:
        try:
            q = urllib.parse.urlencode({"appid": ap, "query": cat[2], "results": 50, "sort": "-review_count", "shipping": "free", "in_stock": "true"})
            with urllib.request.urlopen("https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch?" + q, timeout=20) as r:
                hits = json.load(r).get("hits") or []
            rows = tanka.yahoo_rows(cat)
            print(cat[0], "hits", len(hits), "ok", len(rows), [(x["per"], x["amt"], x["rc"]) for x in rows])
            for it in hits[:4]:
                rv = it.get("review") or {}
                print("   ", rv.get("count"), rv.get("rate"), it.get("price"), (it.get("name") or "")[:80], "| amt", tanka.amount(cat[0], it.get("name") or ""))
        except Exception as e:
            print(cat[0], "ERR", str(e)[:200])
        time.sleep(1.2)
