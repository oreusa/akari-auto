# 強いページだけのサイトマップ（11/12）。全部入りの sitemap.xml はそのまま残す。
# 似た形で数の多いページ（街・実家・スポット1件ずつ）を外し、入口・まとめ・市の補助・ランキングを先に Google へ見せる。
# 使い方: python3 tools/seo/sitemap_main.py <sitemap.xml> <出力> [外す頭 ...]
import re, sys
src, out = sys.argv[1], sys.argv[2]
skip = tuple(sys.argv[3:]) or ("machi/", "jikka/", "o/")
s = open(src, encoding="utf-8").read()
urls = re.findall(r"<url>.*?</url>", s, flags=re.S)
def path(u):
    m = re.search(r"<loc>https?://[^/]+/([^<]*)</loc>", u)
    return m.group(1) if m else ""
keep = [u for u in urls if not path(u).startswith(skip)]
# 並び：入口 → ランキング → 市の補助 → そのほか
def rank(u):
    p = path(u)
    return 0 if p == "" else 1 if "ranking" in p else 2 if p.startswith("kaitai") else 3
keep.sort(key=rank)
open(out, "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(keep) + "\n</urlset>\n")
print("sitemap-main:", len(keep), "/", len(urls))
