"""関東おでかけリストのおでかけ1件ごとのページ（/o/xxxxxxxx）と、都県ごとのページ（/odekake-tokyo など）を作る。
11/4 オーナー（月のスレッド）「LIFEもそうだけど、色んな記事ある中で検索なんでも引っかかって欲しい」→ 月の /o/ と同じ形。
中身はリストのカードに書いてある事実だけ（日程・都県・無料・公式リンク・地図・近くの宿）。page.yml で lifenote.py のあとに毎回作り直す。
python3 scripts/spot_pages.py"""
import os, re, json, html, hashlib, glob, datetime, urllib.parse, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(R, "site")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spot_map  # 11/4 場所の地図（LIFE NOTE の地図と同じ絵）
BASE = os.environ.get("LIFE_BASE") or "https://usagi-life-notes.pages.dev"
# 共通の部品の番号は lifenote.py と同じ物を使う
VER = {"menu.js": 13, "v2sub.js": 8, "night.js": 13}
_m = re.search(r"VER = (\{[^}]*\})", open(os.path.join(R, "scripts", "lifenote.py"), encoding="utf-8").read())
if _m: VER.update(json.loads(_m.group(1)))
FU = {"東京": "東京都", "神奈川": "神奈川県", "埼玉": "埼玉県", "千葉": "千葉県", "茨城": "茨城県", "栃木": "栃木県", "群馬": "群馬県"}
SLUG = {"東京": "tokyo", "神奈川": "kanagawa", "埼玉": "saitama", "千葉": "chiba", "茨城": "ibaraki", "栃木": "tochigi", "群馬": "gunma"}
W = "月火水木金土日"
JST = datetime.timezone(datetime.timedelta(hours=9))
D0 = datetime.datetime.now(JST).date()
TODAY = D0.isoformat()
UPD = f"{D0.year}年{D0.month}月{D0.day}日"
CSS = open(os.path.join(R, "scripts", "spot_base.css"), encoding="utf-8").read()
CSS += """.act{display:grid;gap:8px;margin:22px 0 0}.act a{display:block;text-align:center;text-decoration:none;padding:13px;font-size:14px;font-weight:700;border-radius:12px}
.act .o{background:#3A2F28;color:#fff}.act .g{border:1px solid #D5D8DD;color:#2B2622;background:#fff}
.lead{font-size:14px;line-height:2;color:#3A3330;margin:22px 0 0}
.yl{list-style:none;margin:0;padding:0}.yl li{border-bottom:1px solid #ECECEC}.yl a{display:flex;justify-content:space-between;gap:10px;padding:12px 2px;text-decoration:none;color:#2B2622;font-size:13.5px;font-weight:700}
.yl a span{font-size:11.5px;color:#8C7B6E;font-weight:500;white-space:nowrap}.wrap{padding-bottom:120px}
.pn{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:28px 0 0}.pn a{font-size:13px;padding:6px 12px;border:1px solid #DCDFE4;border-radius:99px;color:#3a3330;text-decoration:none;background:#fff}
.pn a[aria-current]{background:#2B2622;color:#fff;border-color:#2B2622}
.tmap{margin:14px 0 0;border-radius:18px;overflow:hidden;box-shadow:0 1px 2px rgba(43,38,34,.05),0 6px 18px rgba(43,38,34,.06);background:#fff}
.tmap svg{display:block;width:100%;height:auto}.tmap p{margin:0;padding:10px 14px 12px;text-align:center;font-size:11.5px;letter-spacing:.06em;color:#8C7B6E}""" + spot_map.night_css()


def e(x): return html.escape(x, quote=True)
def txt(x): return html.unescape(re.sub("<[^>]+>", "", x)).strip()
def jd(d):
    d = datetime.date.fromisoformat(d); return f"{d.month}月{d.day}日（{W[d.weekday()]}）"


src = open(os.path.join(S, "odekake.html"), encoding="utf-8").read()
yp = os.path.join(S, "kanto-yado.json")
if not os.path.exists(yp): yp = os.path.join(R, "data", "kanto-yado.json")
Y = {}
if os.path.exists(yp):
    for k, v in json.load(open(yp, encoding="utf-8")).items():
        Y[re.sub(r"\s+", "", k)] = v.get("h", []) if isinstance(v, dict) else v

spots, seen = [], set()
for m in re.finditer(r'<div class="card it"([^>]*)>(.*?)<svg class="arw"', src, re.S):
    a = {k: html.unescape(v) for k, v in re.findall(r'(data-[\w-]+)="([^"]*)"', m.group(1))}
    b = m.group(2); p = a.get("data-pref", "")
    if p not in FU: continue
    g = re.search(r'<a class="go" href="([^"]+)"[^>]*>(.*?)</a>', b, re.S)
    if not g: continue
    name = txt(g.group(2).replace("</span><span", "</span> <span")); key = re.sub(r"\s+", "", name)
    st, en = a.get("data-s", ""), a.get("data-e", "")
    if en and en < TODAY or key in seen: continue
    seen.add(key)
    w = re.search(r'class="when">(.*?)</span>', b, re.S)
    mp = re.search(r'class="mp" href="([^"]+)"', b)
    q = urllib.parse.unquote(html.unescape(mp.group(1)).split("query=", 1)[1]) if mp else ""
    place = re.sub(r"\s*(東京|神奈川|埼玉|千葉|茨城|栃木|群馬)(都|県)?$", "", q).strip()
    spots.append(dict(name=name, key=key, pref=p, st=st, en=en, url=html.unescape(g.group(1)), when=txt(w.group(1)) if w else "",
                      free="無料" in b[:600], q=q, place=place, id=hashlib.md5(key.encode()).hexdigest()[:8],
                      pc=re.search(r"--pc:(#[0-9A-Fa-f]{6})", m.group(1)).group(1) if "--pc:" in m.group(1) else "#A07E66"))


def head(title, desc, canon, ld, pc):
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{canon}">
<meta property="og:type" content="article"><meta property="og:url" content="{canon}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta name="twitter:card" content="summary"><link rel="apple-touch-icon" href="/assets/icon-180.png"><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#FFFFFF">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Jost:wght@300..600&family=Shippori+Mincho:wght@500;600;700&family=Zen+Kaku+Gothic+New:wght@500;700&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")}</script><style>{CSS}</style>
<script src="/assets/night.js?v={VER['night.js']}"></script><script src="/assets/menu.js?v={VER['menu.js']}" defer></script><script src="/assets/v2sub.js?v={VER['v2sub.js']}" defer></script></head>
<body style="--pc:{pc}"><div class="wrap">"""


def card(o):
    d = (jd(o["st"]) + ("〜" + jd(o["en"]) if o["en"] and o["en"] != o["st"] else "")) if o["st"] else o["when"]
    return f'<a class="fc" href="/o/{o["id"]}" style="border-left-color:{o["pc"]}"><small>{e(o["pref"])}{"｜" + e(o["place"]) if o["place"] else ""}{"｜無料" if o["free"] else ""}</small><b>{e(o["name"])}</b><span>{e(d)}</span></a>'


def prefnav(cur=""):
    return '<nav class="pn" aria-label="都県ごとに見る"><a href="/odekake">関東すべて</a>' + "".join(
        f'<a href="/odekake-{SLUG[q]}"{" aria-current=page" if q == cur else ""}>{q}</a>' for q in FU if any(o["pref"] == q for o in spots)) + "</nav>"


os.makedirs(os.path.join(S, "o"), exist_ok=True)
for f in glob.glob(os.path.join(S, "o", "*.html")): os.remove(f)
urls = []
for sp in spots:
    p, fu, nm, pc = sp["pref"], FU[sp["pref"]], sp["name"], sp["pc"]; yr = (sp["st"] or TODAY)[:4]
    when = (jd(sp["st"]) + ("〜" + jd(sp["en"]) if sp["en"] and sp["en"] != sp["st"] else "")) if sp["st"] else sp["when"] or "公式ページで"
    stat = ""
    if sp["st"] and sp["st"] > TODAY: stat = f"あと{(datetime.date.fromisoformat(sp['st']) - D0).days}日ではじまります"
    elif sp["en"]:
        left = (datetime.date.fromisoformat(sp["en"]) - D0).days; stat = "きょうまで" if left == 0 else f"開催中・あと{left}日"
    elif sp["st"]: stat = "開催中"
    where = fu + ("の" + sp["place"] if sp["place"] else "")
    lead = f"{nm}は、{where}で" + (f"、{jd(sp['st'])}から{jd(sp['en'])}まで開かれます。" if sp["st"] and sp["en"] and sp["en"] != sp["st"] else (f"、{jd(sp['st'])}に開かれます。" if sp["st"] else "楽しめます。"))
    if sp["free"]: lead += "入場は無料です。"
    title = f"{nm if yr in nm else nm + " " + yr}｜日程・場所・{'入場無料' if sp['free'] else 'アクセス'}（{fu}）｜LIFE NOTE"
    desc = f"{nm}（{where}）の{yr}年の日程は{when}。{'入場無料。' if sp['free'] else ''}公式ページ、地図、近くの宿をまとめました。{UPD}確認。"
    canon = f"{BASE}/o/{sp['id']}"
    ev = {"@type": "Event", "name": nm, "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode", "eventStatus": "https://schema.org/EventScheduled",
          "location": {"@type": "Place", "name": sp["place"] or fu, "address": {"@type": "PostalAddress", "addressRegion": fu, "addressCountry": "JP"}}, "url": sp["url"]}
    if sp["st"]: ev["startDate"] = sp["st"]
    if sp["en"]: ev["endDate"] = sp["en"]
    if sp["free"]: ev["isAccessibleForFree"] = True
    bc = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "関東おでかけリスト", "item": BASE + "/odekake"},
        {"@type": "ListItem", "position": 2, "name": f"{p}おでかけリスト", "item": f"{BASE}/odekake-{SLUG[p]}"},
        {"@type": "ListItem", "position": 3, "name": nm, "item": canon}]}
    big = f'<div class="w"><span>日程</span><b>{e(when)}</b></div>'
    big += f'<div><span>いまは</span><b style="color:{pc};font-size:15px;font-family:\'Zen Kaku Gothic New\';font-weight:700">{e(stat or "公式ページで")}</b></div>'
    big += f'<div><span>入場</span><b style="color:#2B2622;font-size:15px;font-family:\'Zen Kaku Gothic New\';font-weight:700">{"無料" if sp["free"] else "公式ページで"}</b></div>'
    big += f'<div class="w"><span>場所</span><b>{e(where)}</b></div>'
    act = f'<a class="o" href="{e(sp["url"])}" target="_blank" rel="noopener">公式ページで最新の情報を見る</a>'
    if sp["q"]: act += f'<a class="g" href="https://www.google.com/maps/search/?api=1&amp;query={e(urllib.parse.quote(sp["q"]))}" target="_blank" rel="noopener">地図で場所を見る</a>'
    yh, ads = "", False
    if Y.get(sp["key"]):
        ads = True
        li = "".join(f'<li><a href="{e(h["u"])}" target="_blank" rel="noopener sponsored">{e(h["n"])}<span>{"すぐそば" if h.get("km", 1) < 0.1 else str(h.get("km")) + "km"}{"・★" + str(h["r"]) if h.get("r") else ""}{"・" + format(int(h["min"]), ",") + "円〜" if h.get("min") else ""}</span></a></li>' for h in Y[sp["key"]][:3])
        yh = f'<h2>近くの宿</h2><p class="cap">楽天トラベルの評価の高い宿を、ここからの近さで選びました（PR）</p><ul class="yl">{li}</ul>'
    near = [o for o in spots if o is not sp and o["pref"] == p][:6]
    lbl = sp["place"].split(" ")[0] if sp["place"] else nm
    lbl = lbl if len(lbl) < 16 else nm
    try:
        msvg = spot_map.render(p, sp["q"], "", lbl) if sp["q"] else ""
    except Exception:
        msvg = ""
    mapd = f'<div class="tmap">{msvg}<p>{e(lbl)}の場所（{e(fu)}）</p></div>' if msvg and "<circle" in msvg else ""
    page = head(title, desc, canon, {"@context": "https://schema.org", "@graph": [ev, bc]}, pc)
    page += f"""<div class="head"><img src="/logo-s.png" width="60" height="60" alt="LIFE NOTE のロゴ"><div class="en">{SLUG[p].upper()} ─ ODEKAKE</div>
<h1>{e(nm)}<span>{yr} 日程・場所</span></h1><p class="sub">{e(where)}</p><div class="upd">{UPD} 確認</div></div>
<div class="big">{big}</div>{mapd}<p class="lead">{e(lead)}</p><div class="act">{act}</div>{yh}
<h2>{e(p)}のほかのおでかけ</h2>{"".join(card(o) for o in near)}{prefnav(p)}
<a class="back" href="/odekake-{SLUG[p]}">{e(p)}おでかけリストへ</a><a class="back" href="/odekake" style="margin-top:14px">関東おでかけリストへ</a>
<div class="note">日程や料金は変わることがあります。出かける前に、必ず公式ページで確かめてください。{"<br>「近くの宿」のリンクは広告です。" if ads else ""}</div>
<div class="ft">LIFE NOTE ─ 関東おでかけリスト</div></div></body></html>
"""
    open(os.path.join(S, "o", sp["id"] + ".html"), "w", encoding="utf-8").write(page)
    urls.append(canon)

# 都県ごとのページ（「東京 イベント 今週末」などで探す人向け）
for p, fu in FU.items():
    es = sorted([o for o in spots if o["pref"] == p], key=lambda o: (o["en"] or "9999", o["st"]))
    if not es: continue
    pc = es[0]["pc"]; nowc = sum(1 for o in es if not o["st"] or o["st"] <= TODAY); free = sum(1 for o in es if o["free"])
    title = f"{p}のおでかけ・イベント一覧｜開催中・今週末・これから（{fu}）｜LIFE NOTE"
    names = "、".join(o["name"] for o in es[:4])
    desc = f"{fu}で開催中・これからのイベントとおでかけ先{len(es)}件（入場無料{free}件）を、日程・場所・公式ページつきで一覧にしました。{names}など。{UPD}更新。"
    canon = f"{BASE}/odekake-{SLUG[p]}"
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": f"{p}のおでかけリスト",
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{BASE}/o/{o['id']}", "name": o["name"]} for i, o in enumerate(es)]}
    now = [o for o in es if not o["st"] or o["st"] <= TODAY]; later = [o for o in es if o["st"] and o["st"] > TODAY]
    body = (f'<h2>開催中</h2>{"".join(card(o) for o in now)}' if now else "") + (f'<h2>これから</h2>{"".join(card(o) for o in later)}' if later else "")
    page = head(title, desc, canon, ld, pc) + f"""<div class="head"><img src="/logo-s.png" width="60" height="60" alt="LIFE NOTE のロゴ"><div class="en">{SLUG[p].upper()} ─ ODEKAKE</div>
<h1>{e(p)}おでかけリスト<span>開催中 {nowc}件・これから {len(es) - nowc}件</span></h1><p class="sub">{e(fu)}のイベントとおでかけ先を、<br>終わる日が近い順に並べました。</p><div class="upd">{UPD}更新</div></div>
{body}{prefnav(p)}<a class="back" href="/odekake">関東おでかけリストへ</a>
<div class="note">日程や料金は変わることがあります。出かける前に、必ず公式ページで確かめてください。</div>
<div class="ft">LIFE NOTE ─ 関東おでかけリスト</div></div></body></html>
"""
    open(os.path.join(S, f"odekake-{SLUG[p]}.html"), "w", encoding="utf-8").write(page)
    urls.insert(0, canon)

sm = os.path.join(S, "sitemap.xml")
if os.path.exists(sm):
    x = open(sm, encoding="utf-8").read()
    x = re.sub(r"<url><loc>[^<]*/(?:o/[0-9a-f]{8}|odekake-[a-z]+)</loc>.*?</url>\s*", "", x)
    add = "".join(f"<url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls)
    open(sm, "w", encoding="utf-8").write(x.replace("</urlset>", add + "</urlset>", 1))
print("spot pages", len(spots), "/ pref pages", sum(1 for u in urls if "/odekake-" in u))
