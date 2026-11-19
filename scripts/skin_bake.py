"""11/19 21:50 owner「他も変わってなかったりあるよまだ」
Workers の無料の上限で functions（_middleware.js の skin()）が止まると、ページがそのまま出て古い頭・バーに戻っていた。
→ 公開する前に、全部のページの <head> に新しい土台の 頭・下のバー・夜空の読み込みを書き込んでおく。
middleware も同じ物を入れるが、skin.js は2回目を読まない（window.__sk）ので2重にならない。
"""
import pathlib, sys
root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "site")
SKIN = ('<script>document.documentElement.classList.add("sk");try{if(localStorage.getItem("usagi_theme")==="night")'
        'document.documentElement.classList.add("nt")}catch(e){}</script><link rel="stylesheet" href="/shin/skin.css">'
        '<script src="/shin/skin.js" defer></script>')
n = 0
for f in root.rglob("*.html"):
    if "shin" in f.relative_to(root).parts[:1]:
        continue
    t = f.read_text(encoding="utf-8", errors="ignore")
    if 'href="/shin/skin.css"' in t or "/shin/shin.css" in t or "</head>" not in t:  # 新しい土台のページ（shin_kanto.py）にはかぶせない
        continue
    f.write_text(t.replace("</head>", SKIN + "</head>", 1), encoding="utf-8"); n += 1
print("skin_bake: 頭とバーを書き込み", n, "枚")
