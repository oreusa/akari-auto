#!/usr/bin/env python3
"""関東の実家・空き家の3問診断（site/jikka/shindan/index.html）。11/11 オーナー「反映頼む」。
月（関西）の tools/shindan/tpl.html と同じ物（scripts/shindan_tpl.html に写し）を、関東の言葉に置きかえて作る。
関東は「売れた値段」の公式の数字が無いので、かわりに地価公示（住宅地の前年比と都県内の順位）を出す。
fudosan_kanto.py の後に動かす（site/assets/towns.json を読む）。"""
import json, os, re
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(R, "site")
BASE = os.environ.get("LIFE_BASE") or "https://usagi-life-notes.pages.dev"
towns = json.load(open(os.path.join(S, "assets", "towns.json"), encoding="utf-8"))
towns = towns.get("towns", towns) if isinstance(towns, dict) else towns
D = [{"i": t["id"], "p": t["p"], "n": t["n"], "k": t.get("k", ""), "r": t.get("r8"), "rk": t.get("rk"), "of": t.get("of")}
     for t in towns if os.path.exists(os.path.join(S, "jikka", t["id"] + ".html"))]
h = open(os.path.join(R, "scripts", "shindan_tpl.html"), encoding="utf-8").read()
PRICE = ('function price(t){if(t.r==null)return "<p class=\'src\'>この街は、地価公示の住宅地の数字がありません。査定でお家ごとの値段をお調べできます。</p>";'
         'return "<div class=\'pr2\'><div><span>住宅地の地価（前の年とくらべて）</span><b>"+(t.r>0?"+":"")+t.r.toFixed(1)+"<small>%</small></b><em>令和8年 地価公示</em></div>"'
         '+(t.rk?"<div><span>"+E(t.p)+"での順位（上がり幅）</span><b>"+t.rk+"<small>位／"+t.of+"</small></b><em>市区町村の中で</em></div>":"")+"</div>'
         '<p class=\'src\'>出典：国土交通省 地価公示（令和8年・住宅地の平均変動率）。土地の動きの目安で、お家ごとの値段は広さ・古さで変わります。'
         '<a style=\'color:inherit\' href=\'/machi/"+t.i+"\' data-k=\'診断｜街の地価｜"+E(t.n)+"\'>"+E(t.n)+"の地価をくわしく</a></p>"}')
a, b = h.index("function price(t){"), h.index("function result(){")
h = h[:a] + PRICE + "\n" + h[b:]
def rep(x, y, n=None):
    global h
    assert x in h, x
    h = h.replace(x, y) if n is None else h.replace(x, y, n)
rep("https://townnote.pages.dev/assets/ogp.png", BASE + "/og-v10.png")
rep("https://townnote.pages.dev", BASE)
rep("TOWN NOTE", "LIFE NOTE")
rep('<link rel="icon" href="/assets/ogp.png"><link rel="apple-touch-icon" href="/assets/icon-180.png">', '<link rel="icon" href="/logo.png"><link rel="apple-touch-icon" href="/assets/icon-180.png">')
rep('/assets/logo-s.png?v=2', '/logo-s.png')
rep("関西のお家が対象です", "関東のお家が対象です")
rep("その街で売れた値段が分かります", "その街の地価の動きが分かります")
rep('placeholder="例：ひらかた、西宮"', 'placeholder="例：はちおうじ、川口"')
rep('var PF=["大阪","京都","兵庫","奈良","滋賀","和歌山"];', "var PF=" + json.dumps(list(dict.fromkeys(t["p"] for t in D)), ensure_ascii=False) + ";")
rep("上の数字が、この街で実際に売れた平均です。", "上の数字が、この街の土地の値段の動きです。")
rep("<p class='mk'>SOLD</p><h3>\"+E(t.n)+\"で、売れた値段</h3>", "<p class='mk'>LAND PRICE</p><h3>\"+E(t.n)+\"の、地価の動き</h3>")
# 見た目の道具の版は、ほかのページ（一覧）と同じにそろえる
jl = open(os.path.join(S, "jikka", "index.html"), encoding="utf-8").read()
for f in ("night.js", "menu.js", "v2sub.js"):
    m = re.search(r'/assets/' + re.escape(f) + r'\?v=(\d+)', jl)
    if m:
        h = re.sub(r'/assets/' + re.escape(f) + r'\?v=\d+', f"/assets/{f}?v={m.group(1)}", h)
# 11/13 関東はアフィリエイトが本来（オーナー 11/9）。A8 の提携済み2つ（汐 11/13）：査定＝ざっくりAI査定＋、片付け＝ぽいみつ。ほかは申し込みのまま。
rep("<a class='cta\"+(i?\"\":\" b1\")+\"' href='/moushikomi?\"+(/片付け|解体/.test(w)?\"lite=1&amp;\":\"\")+\"machi=\"+t.i+(w?\"&amp;want=\"+encodeURIComponent(w):\"\")+\"' data-k=",
    "<a class='cta\"+(i?\"\":\" b1\")+\"' href='\"+(AF[w]?\"https://px.a8.net/svt/ejp?a8mat=\"+AF[w][0]+\"' rel='nofollow sponsored noopener' target='_blank\":\"/moushikomi?\"+(/片付け|解体/.test(w)?\"lite=1&amp;\":\"\")+\"machi=\"+t.i+(w?\"&amp;want=\"+encodeURIComponent(w):\"\"))+\"' data-k=")
rep("function result(){", 'var AF={"査定してほしい":["4BGH3I+E2NY4I+5Y9M+5YJRM","www14"],"片付け・遺品整理の見積り":["4BGK80+84BWCI+5Y1K+5YZ76","www16"]};function result(){', 1)
rep('"査定してほしい":"無料で査定を頼む"', '"査定してほしい":"いくらで売れそうか、AIで見る（ざっくりAI査定＋）"')
rep('"片付け・遺品整理の見積り":"片付けの見積りを頼む"', '"片付け・遺品整理の見積り":"片付け・不用品回収の見積りをくらべる（ぽいみつ）"')
rep("1社に決めていない窓口です。内容に合わせて複数の会社をご紹介でき、見積りをくらべてから決められます。", "どれも無料です。見積りや査定をくらべてから決められます。")
rep("<h1>実家・空き家の3問診断</h1>", "<h1>実家・空き家の3問診断</h1><p style='font-size:11px;color:#8C7B6E;margin:4px 0 0'>このページには広告（PR）を含みます</p>")
rep("<p class='nt'>この診断は、", "<p class='nt'>このページのリンクの一部は広告（PR）です。この診断は、")
assert "売れた" not in h and "関西" not in h and "townnote" not in h and "レインズ" not in h, "関西の言葉が残っている"
h = h.replace("__DATA__", json.dumps(D, ensure_ascii=False, separators=(",", ":")))
os.makedirs(os.path.join(S, "jikka", "shindan"), exist_ok=True)
open(os.path.join(S, "jikka", "shindan", "index.html"), "w", encoding="utf-8").write(h)
sm = os.path.join(S, "sitemap.xml")
if os.path.exists(sm):
    x = open(sm, encoding="utf-8").read()
    u = f"{BASE}/jikka/shindan/"
    if u + "<" not in x:
        open(sm, "w", encoding="utf-8").write(x.replace("</urlset>", f"<url><loc>{u}</loc></url></urlset>", 1))
print("関東の3問診断:", len(D), "街")
