"""楽天の検索で keyword が効いているかを確かめる（一回きりの試し。tanka-test.yml から）。"""
import os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
import lib
for q in [{"keyword": "炭酸水", "hits": 5}, {"keyword": "炭酸水", "genreId": "100316", "hits": 5, "sort": "-reviewCount"},
          {"keyword": "トイレットペーパー", "hits": 5, "sort": "-reviewCount", "postageFlag": 1},
          {"keyword": "米 10kg", "hits": 5, "sort": "-reviewCount", "postageFlag": 1}]:
    items, err = lib._rakuten_search(q)
    print(q, err)
    for it in items or []:
        print("   ", it.get("itemPrice"), (it.get("itemName") or "")[:60])
    time.sleep(1.2)
