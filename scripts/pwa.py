"""ホーム画面に置けるように（PWA）。月の TOWN NOTE と同じ形（11/2 オーナー「アプリできるようにできてるよな？」「town、LIFEどっちも必ず」）。
site の全ページの head に manifest・アイコン・theme-color を入れ、/sw.js を登録する。page.yml の最後（lifenote.py のあと）に動かす。"""
import glob, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAGS = ('<link rel="apple-touch-icon" href="/assets/icon-180.png">\n<link rel="manifest" href="/manifest.webmanifest">\n'
        '<meta name="theme-color" content="#FFFFFF">\n')
SW = ('<script>if("serviceWorker" in navigator&&location.protocol==="https:")window.addEventListener("load",function(){'
      'navigator.serviceWorker.register("/sw.js").catch(function(){});});</script>\n')
n = 0
for f in glob.glob(os.path.join(ROOT, "site", "**", "*.html"), recursive=True):
    h = open(f, encoding="utf-8").read()
    if "</head>" not in h or 'rel="manifest"' in h:
        continue
    h = h.replace("</head>", TAGS + SW + "</head>", 1)
    open(f, "w", encoding="utf-8").write(h); n += 1
print("PWA", n, "pages")
