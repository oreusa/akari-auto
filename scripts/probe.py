"""調べ用：機械（GitHub）から各ページが開けるかを見る。投稿はしない。"""
import re, sys, urllib.request
UAS = {"bot": "akari-auto/1.0", "browser": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}
for url in sys.argv[1:]:
    for name, ua in UAS.items():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Language": "ja-JP,ja;q=0.9", "Accept": "text/html"})
            with urllib.request.urlopen(req, timeout=20) as r:
                body = r.read().decode("utf-8", "replace")
                t = re.search(r"<title[^>]*>(.*?)</title>", body, re.S)
                flags = [w for w in ("captcha", "ロボット", "在庫あり", "現在お取り扱いできません", "有効なページではありません", "カートに入れる", "終了") if w in body]
                print(f"{name} {r.status} {r.geturl()[:80]} | {(t.group(1).strip() if t else '')[:60]} | {flags} | {len(body)}")
        except Exception as e:
            print(f"{name} ERR {url[:80]} {str(e)[:100]}")
