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


# 11/20 関西の1件ページと同じに：時間・料金・駐車場の行。中身は data/page-spots.json の note（集め係と夜の回が公式ページで確かめて書いた文）だけ。
# note を「。」と「、」で切り、時刻のある所＝時間、円・無料＝料金、駐車場＝駐車場、休み・予約など＝メモ。終わった日だけの話（11/3は無料 など）と「公式で確認」は出さない
_TM = re.compile(r"\d{1,2}:\d\d|\d{1,2}時(?!間)|日没|終日|24時間")
_YEN = re.compile(r"\d[\d,]*円")
_PR = re.compile(r"\d[\d,]*円|無料")
_NT = re.compile(r"休み|休館|休園|休室|予約|日時指定|先着|要ります|変わります|中止|整理券|駅から|歩いて")
def _chunks(t):
    out, cur, d = [], "", 0
    for ch in t:
        if ch in "（(": d += 1
        if ch in "）)": d -= 1
        if ch == "、" and d == 0: out.append(cur); cur = ""
        else: cur += ch
    out.append(cur)
    return [c.strip() for c in out if c.strip()]
def more_of(note):
    T, P, K, N = [], [], [], []
    for sg in [x.strip() for x in (note or "").split("。") if x.strip()]:
        sg = re.sub(r"^[^｜]{1,14}｜", "", sg)
        for c in _chunks(sg):
            if re.match(r"^\d{1,2}/\d{1,2}[・\d]*は", c) or "公式で確認" in c or ("点灯式" in c and "〜" not in c): continue
            if c.startswith("駐車場"): K.append(c.replace("駐車場は", "", 1)); continue
            if _NT.search(c) and not _PR.search(c): N.append(c)
            elif _YEN.search(c) and not re.search(r"\d:\d\d〜", c): P.append(c)
            elif _TM.search(c): T.append(c)
            elif _PR.search(c): P.append(c)
    mo = {}
    if T: mo["time"] = "、".join(T)
    if P: mo["price"] = "、".join(P)
    if K: mo["park"] = "、".join(K)
    if N: mo["note"] = "。".join(N) + "。"
    return mo
MORE = {}
try:
    for _it in json.load(open(os.path.join(R, "data", "page-spots.json"), encoding="utf-8")).get("items", []):
        _m = more_of(_it.get("note", ""))
        if _m: MORE[re.sub(r"\s+", "", _it.get("title", ""))] = _m
except Exception as _x:
    print("page-spots の note を読めなかった", _x)


def e(x): return html.escape(x, quote=True)
def txt(x): return html.unescape(re.sub("<[^>]+>", "", x)).strip()
def jd(d):
    d = datetime.date.fromisoformat(d); return f"{d.month}月{d.day}日（{W[d.weekday()]}）"


src = open(os.path.join(S, "odekake.html"), encoding="utf-8").read()
yp = os.path.join(S, "kanto-yado-all.json")  # 11/21 街なかの宿も入れた版（1件ページだけ）
if not os.path.exists(yp): yp = os.path.join(S, "kanto-yado.json")
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
    _on = re.search(r"（([^（）]*のみ開館)）", txt(w.group(1)) if w else "")  # 11/9 夜#155：休館の曜日（例：木〜日・祝のみ開館）を1件ページと都県ページにも
    spots.append(dict(name=name, key=key, pref=p, st=st, en=en, url=html.unescape(g.group(1)), when=txt(w.group(1)) if w else "", opn=_on.group(1) if _on else "",
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
    if o.get("opn") and o["opn"] not in d: d += f"（{o['opn']}）"
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
    if sp.get("opn") and sp["opn"] not in when: when += f"（{sp['opn']}）"
    stat = ""
    if sp["st"] and sp["st"] > TODAY: stat = f"あと{(datetime.date.fromisoformat(sp['st']) - D0).days}日ではじまります"
    elif sp["en"]:
        left = (datetime.date.fromisoformat(sp["en"]) - D0).days; stat = "きょうまで" if left == 0 else f"開催中・あと{left}日"
    elif sp["st"]: stat = "開催中"
    # 11/20 「千葉県のマザー牧場 千葉県富津市」のように県名が2回出ていた → 「千葉県富津市のマザー牧場」
    _pl = sp["place"]; _ct = ""
    _mm = re.search(r"\s+(?:" + re.escape(fu) + r")?(\S+[市区町村])$", _pl)
    if _mm: _ct, _pl = _mm.group(1), _pl[:_mm.start()].strip()
    where = fu + _ct + ("の" + _pl if _pl else "")
    lead = f"{nm}は、{where}で" + (f"、{jd(sp['st'])}から{jd(sp['en'])}まで開かれます。" if sp["st"] and sp["en"] and sp["en"] != sp["st"] else (f"、{jd(sp['st'])}に開かれます。" if sp["st"] else "楽しめます。"))
    if sp["free"]: lead += "入場は無料です。"
    mo = MORE.get(sp["key"], {})
    if sp["free"] and mo.get("price") and not _YEN.search(mo["price"]): mo = {k: v for k, v in mo.items() if k != "price"}  # 「入場無料」だけなら上の「入場：無料」で分かる
    has = [x for x, k in (("時間", "time"), ("料金", "price"), ("駐車場", "park")) if mo.get(k)]
    if mo.get("time"): lead += f"時間は{mo['time'].rstrip('。')}です。"
    if mo.get("price"): lead += f"料金は{mo['price'].rstrip('。')}です。"
    if mo.get("park"): lead += f"駐車場は{mo['park'].rstrip('。')}です。"
    if mo.get("note"): lead += mo["note"]
    title = f"{nm if yr in nm else nm + " " + yr}｜{'・'.join(has) + '・' if has else ''}日程・場所{'' if len(has) > 1 else ('・入場無料' if sp['free'] else '・アクセス')}（{fu}）｜LIFE NOTE"
    desc = f"{nm}（{where}）の{yr}年の日程は{when}。{'入場無料。' if sp['free'] else ''}{('時間は' + mo['time'] + '。') if mo.get('time') else ''}{('料金は' + mo['price'] + '。') if mo.get('price') else ''}公式ページ、地図、近くの宿をまとめました。{UPD}確認。"
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
    # 11/9 全文点検：「いまは／公式ページで」は意味が通らない → 開催の状態が分かる時だけ出す
    if stat: big += f'<div><span>いまは</span><b style="color:{pc};font-size:15px;font-family:\'Zen Kaku Gothic New\';font-weight:700">{e(stat)}</b></div>'
    # 11/20 料金が分かる時は「入場：公式で確認」を出さない（下の「料金」の行で分かる）。関西と同じ
    if sp["free"] or not mo.get("price"): big += f'<div><span>入場</span><b style="color:#2B2622;font-size:15px;font-family:\'Zen Kaku Gothic New\';font-weight:700">{"無料" if sp["free"] else "公式で確認"}</b></div>'
    for lb, k in (("時間", "time"), ("料金", "price"), ("駐車場", "park")):
        if mo.get(k): big += f'<div class="w"><span>{lb}</span><b style="font-size:15px;font-family:\'Zen Kaku Gothic New\';font-weight:700;line-height:1.7">{e(mo[k])}</b></div>'
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
<h1>{e(nm)}<span>{"" if yr in nm else yr + " "}日程・場所</span></h1><p class="sub">{e(where)}</p><div class="upd">{UPD} 確認</div></div>
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
    # 11/12 燈：検索で多い「栃木 イベント 11月」「今週末」の言葉を題の前に（台帳の指令 hp）
    title = f"{p}のイベント{D0.month}月・今週末｜開催中{nowc}件・無料{free}件のおでかけ一覧（{fu}）｜LIFE NOTE"
    names = "、".join(o["name"] for o in es[:4])
    desc = f"{fu}の{D0.month}月のイベント・今週末のおでかけ。開催中・これからの{len(es)}件（入場無料{free}件）を、日程・場所・公式ページつきで一覧にしました。{names}など。{UPD}更新。"
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

# 11/8 月のスレッド オーナー「本気でやれよ」（Google にまだ載っていない）→ 関東おでかけリスト（/odekake）から都県ページへのリンクが無かった。
# 一番下に「都県ごとに見る」を足して、/odekake → /odekake-tokyo など → /o/ と Google がたどれるようにする（月の /odekake と同じ）。
op = os.path.join(S, "odekake.html")
h = open(op, encoding="utf-8").read()
if "<!--pn-->" not in h:
    nav = ('<!--pn--><style>.prefnav{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:28px 0 8px}.prefnav .plh{width:100%;text-align:center;font-size:12px;letter-spacing:.2em;color:#8a8f98;margin-bottom:4px}.prefnav a{font-size:13px;padding:6px 12px;border:1px solid #DCDFE4;border-radius:99px;color:#3a3330;text-decoration:none;background:#fff}</style>'
           '<nav class="prefnav" aria-label="都県ごとに見る"><div class="plh">都県ごとに見る</div>' +
           "".join(f'<a href="/odekake-{SLUG[q]}">{q}</a>' for q in FU if any(o["pref"] == q for o in spots)) + '</nav><!--/pn-->')
    for anchor in ("出かける前に、必ず公式ページで", '<div class="sns">', "</body>"):
        if anchor in h:
            h = h.replace(anchor, nav + anchor, 1); break
    open(op, "w", encoding="utf-8").write(h)
    print("odekake.html: 都県ごとに見る を足した")
