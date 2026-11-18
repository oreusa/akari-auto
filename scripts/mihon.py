"""11/18 関東の見本（月の tools/mihon/build.py と同じ形）：カードに会場・場所の写真を付けるための表 site/assets/mihon.json。
?mihon=1 の人だけに出る（night.js が /assets/mihon.js を読む）。写真は data/venue_photos.json（コモンズから目で選んだ物）。
page.yml で lifenote.py・illumi.py・koyo.py・spot_pages.py のあとに作る。 python3 scripts/mihon.py"""
import os, re, json, html, hashlib, glob

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(R, "site")
FU = ("東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬")
lj = lambda p, d: json.load(open(p, encoding="utf-8")) if os.path.exists(p) else d
VP = lj(os.path.join(R, "data", "venue_photos.json"), {})
AL = lj(os.path.join(R, "data", "venue_alias.json"), {})


def txt(x): return html.unescape(re.sub("<[^>]+>", "", x)).strip()


def venue(m, name):
    # 関東のカードの場所は「市｜会場」か「会場 市」の2つの形
    place = m.split("｜")[-1].strip() if "｜" in m else (m.rsplit(" ", 1)[0].strip() if " " in m else (m or name))
    place = re.sub(r"（[^）]*）|\([^)]*\)|「[^」]*」", "", place).strip()
    place = re.split(r"ほか|、", place)[0].strip() or place
    # 空白は名前の中にもある（ラ チッタデッラ・THE OUTLETS など）→ そのままで当たらない時だけ前の語に切る
    global FULL; FULL = place
    if place not in VP and place not in AL and " " in place: place = place.split(" ")[0]
    return AL.get(place, place)


out = {}
FULL = ""


def add(name, p, s, e, u, m, oid=""):
    key = re.sub(r"\s+", "", name)
    if not key or key in out: return
    o = {"n": name, "u": u, "s": s, "e": e, "p": p}
    if oid: o["id"] = oid
    vn = venue(m, name)
    if vn not in VP:
        # 「A・B」「A〜B」の並びや「◯◯駅周辺」は、写真のある方・駅の名前に寄せる（11/18）
        for c in re.split(r"[・〜～]", vn):
            c = re.sub(r"周辺$|(東口|西口|南口|北口)?(駅前広場|駅前|ペデストリアンデッキ)$", "", c.strip())
            c = re.sub(r"(駅)(東口|西口|南口|北口)$", r"\1", c)
            c = AL.get(c, c)
            for t in (c, c + "駅" if not c.endswith("駅") else c):
                if t in VP: vn = t; break
            if vn in VP: break
    if vn in VP:
        v = VP[vn]; o.update(im=v["img"], cr=v["cr"], cu=v.get("page", ""), vn=re.sub(r"\s*\(.*\)$", "", vn))
        if re.search(r"駅$|市$|町$|村$|区$", o["vn"]): o["vk"] = 1
    else: o["vr"] = FULL if " " in FULL else vn   # 写真の無い会場（調べ用・画面では使わない）
    out[key] = o


# 1) おでかけリスト（div.card.it）。1件ページ /o/ の番号は spot_pages.py と同じ（名前の空白を消して md5 の8文字）
src = open(os.path.join(S, "odekake.html"), encoding="utf-8").read() if os.path.exists(os.path.join(S, "odekake.html")) else ""
for mm in re.finditer(r'<div class="card it"([^>]*)>(.*?)<svg class="arw"', src, re.S):
    a = {k: html.unescape(v) for k, v in re.findall(r'(data-[\w-]+)="([^"]*)"', mm.group(1))}
    b = mm.group(2); p = a.get("data-pref", "")
    if p not in FU: continue
    g = re.search(r'<a class="go" href="([^"]+)"[^>]*>(.*?)</a>', b, re.S)
    if not g: continue
    name = txt(g.group(2).replace("</span><span", "</span> <span")); key = re.sub(r"\s+", "", name)
    m = re.search(r'class="m">(.*?)</div>', b, re.S)
    oid = hashlib.md5(key.encode()).hexdigest()[:8]
    add(name, p, a.get("data-s", ""), a.get("data-e", ""), html.unescape(g.group(1)), txt(m.group(1)) if m else "",
        oid if os.path.exists(os.path.join(S, "o", oid + ".html")) else "")
# 2) イルミ・紅葉（li.it の中の a.cd。名前は .nm・場所は .pl）
for f in sorted(glob.glob(os.path.join(S, "illumination*.html")) + glob.glob(os.path.join(S, "koyo*.html"))):
    s = open(f, encoding="utf-8").read()
    for mm in re.finditer(r'<li class="it[^"]*"([^>]*)>(.*?)</li>', s, re.S):
        a = {k: html.unescape(v) for k, v in re.findall(r'(data-[\w-]+)="([^"]*)"', mm.group(1))}
        b = mm.group(2); t = re.search(r'class="nm">(.*?)</span>', b, re.S); m = re.search(r'class="pl">(.*?)</span>', b, re.S)
        h = re.search(r'<a class="cd" href="([^"]+)"', b)
        if not t or a.get("data-p", "") not in FU: continue
        add(txt(t.group(1)), a.get("data-p", ""), a.get("data-s", ""), a.get("data-e", ""), html.unescape(h.group(1)) if h else "", txt(m.group(1)) if m else "")
# 3) 1件ページ（/o/）に会場・場所の写真。見本の人だけに見える（hidden を mihon.js が外す）。作り直すたびに入れ直す
def esc(x): return html.escape(x, quote=True)
for o in out.values():
    if not o.get("id") or not o.get("im"): continue
    fp = os.path.join(S, "o", o["id"] + ".html"); t = open(fp, encoding="utf-8").read()
    t = re.sub(r'<figure class="mph-k".*?</figure>', "", t, flags=re.S)
    lab = ("場所" if o.get("vk") else "会場") + "：" + o["vn"]
    cr = f'<a href="{esc(o["cu"])}" target="_blank" rel="noopener" style="color:inherit;text-decoration:underline;text-decoration-color:rgba(162,149,138,.4);text-underline-offset:2px">{esc(o["cr"])}</a>' if o.get("cu") else esc(o["cr"])
    fig = (f'<figure class="mph-k" hidden style="margin:18px 0 0;position:relative"><img src="/assets/ph/{o["im"]}" alt="{esc(o["vn"])}" width="1200" height="800" decoding="async" '
           f'style="display:block;width:100%;height:auto;aspect-ratio:3/2;object-fit:cover;border-radius:18px;background:#EFEAE4">'
           f'<i style="position:absolute;left:10px;top:10px;font:700 11px \'Zen Kaku Gothic New\',sans-serif;font-style:normal;color:#fff;background:rgba(30,24,20,.62);border-radius:99px;padding:5px 10px">{esc(lab)}</i>'
           f'<figcaption style="font-size:10.5px;color:#A2958A;margin-top:6px;line-height:1.6">{esc(lab.split("：")[0])}（{esc(o["vn"])}）の写真：{cr}</figcaption></figure>')
    if '<div class="big">' in t:
        t = t.replace('<div class="big">', fig + '<div class="big">', 1); open(fp, "w", encoding="utf-8").write(t)
os.makedirs(os.path.join(S, "assets"), exist_ok=True)
json.dump(out, open(os.path.join(S, "assets", "mihon.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("関東の見本の表", len(out), "件・写真", sum(1 for o in out.values() if o.get("im")))
