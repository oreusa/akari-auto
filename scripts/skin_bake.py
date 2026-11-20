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
# 11/20 19:54 owner「月のおすすめで」→ 見た目 D（オーロラとガラス＋箱並べ・site/shin/look.css）を全部のページの頭に（関西は _middleware.js の LOOK）。
# ?look=0 で前の見た目。戻す時は LOOK を "" にする。
LOOK = '<script>try{var v=localStorage.getItem("tn_lk2")||"f",m=location.search.match(/[?&]look=([abcdef0])/);if(m){v=m[1];localStorage.setItem("tn_lk2",v)}if(v!=="0"){var h=document.documentElement;h.classList.add("lk","lk-"+v);if(v==="d"||v==="e"||v==="f")h.classList.add("lk-a","lk-d");if(v==="f")h.classList.add("lk-e")}}catch(e){}</script><link rel="stylesheet" href="/shin/look.css?v=21" id="lkcss"><script src="/shin/look.js?v=21" defer></script>'
m = 0
for f in root.rglob("*.html"):
    t = f.read_text(encoding="utf-8", errors="ignore")
    if 'id="lkcss"' in t or "</head>" not in t:
        continue
    f.write_text(t.replace("</head>", LOOK + "</head>", 1), encoding="utf-8"); m += 1
print("skin_bake: 見た目 D を書き込み", m, "枚")
