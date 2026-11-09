"""泊まりで行くおでかけ（10/31 オーナー「三本線…旅行先とかのあれも色々作れる…燈の方も」。月の tools/tomari/build.py と同じ形）。
遠くのおでかけ（近くの宿がある物）と、楽天トラベルの評価の高い宿3軒を1ページに → site/tomari.html（/tomari）。
元：site/index.html のおでかけカード、site/illumination.html のカード、site/kanto-yado.json（scripts/kansai_yado.py kanto）。
page.yml で kansai_yado.py のあとに動かす。失敗しても燈のHPは出す（|| true）。"""
import urllib.parse
import hashlib, html, json, os, re, sys
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))
from page import KANTO_ORDER, PREF_COLOR  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
BASE = "https://usagi-life-notes.pages.dev"
WD = "月火水木金土日"
E = html.escape


def txt(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def grab(pat, s):
    m = re.search(pat, s, re.S)
    return m.group(1) if m else ""


def md(x):
    d = date.fromisoformat(x)
    return f"{d.month}/{d.day}（{WD[d.weekday()]}）"


def load_cards(Y):
    cards = {}
    s = open(os.path.join(SITE, "index.html"), encoding="utf-8").read()
    for m in re.finditer(r'<div class="card it"([^>]*)>(.*?)<svg class="arw"', s, re.S):
        a, body = m.group(1), m.group(2)
        t = txt(grab(r'<div class="t">(.*?)</div>', body))
        k = re.sub(r"\s+", "", t)
        if not t or k not in Y or k in cards:
            continue
        cards[k] = dict(t=t, p=html.unescape(grab(r'data-pref="([^"]*)"', a)), s=grab(r'data-s="([^"]*)"', a), e=grab(r'data-e="([^"]*)"', a),
                        d=txt(grab(r'<span class="when">(.*?)</span>', body)), m="", free=grab(r'data-free="(\d)"', a) == "1",
                        href=html.unescape(grab(r'<a class="go" href="([^"]*)"', body)), mp=html.unescape(grab(r'<a class="mp" href="([^"]*)"', body)))
        # 11/1 月と同じく、カードに「都県｜場所」を出す（場所は地図のリンクの検索の言葉から）
        q = urllib.parse.parse_qs(urllib.parse.urlparse(cards[k]["mp"]).query).get("query", [""])[0].strip()
        pf = cards[k]["p"]
        if q.endswith(" " + pf):
            q = q[: -len(pf) - 1].strip()
        if q and q != pf:
            cards[k]["m"] = f"{pf}｜{q}" if pf else q
    p = os.path.join(SITE, "illumination.html")
    if os.path.exists(p):
        s = open(p, encoding="utf-8").read()
        for m in re.finditer(r'<li class="it"([^>]*)>(.*?)</li>', s, re.S):
            a, body = m.group(1), m.group(2)
            t = txt(grab(r'<span class="nm">(.*?)</span>', body))
            k = re.sub(r"\s+", "", t)
            if not t or k not in Y or k in cards:
                continue
            cards[k] = dict(t=t, p=html.unescape(grab(r'data-p="([^"]*)"', a)), s=grab(r'data-s="([^"]*)"', a), e=grab(r'data-e="([^"]*)"', a),
                            d=txt(grab(r'<span class="dt">(.*?)</span>', body)), m=txt(grab(r'<span class="pl">(.*?)</span>', body)),
                            free="無料" in txt(grab(r'<span class="bd">(.*?)</span></span>', body) or body[:400]),
                            href=html.unescape(grab(r'<a class="cd" href="([^"]*)"', body)), mp=html.unescape(grab(r'<a class="mp" href="([^"]*)"', body)))
    return cards


def sat_for(c, today):
    """11/7 売上の調査 B1/C1：宿のリンクに泊まる日を付ける。次の土曜（おでかけが始まる前ならその後の最初の土曜）"""
    d = today + timedelta(days=(5 - today.weekday()) % 7)
    # 11/8 売上の調査 B1：日曜に「この週末」を見た人が来週の土曜へ送られていた。日曜は、その日に開いていれば今夜（日→月）にする
    if today.weekday() == 6 and (not c.get("s") or c["s"] <= today.isoformat()) and (not c.get("e") or c["e"] >= today.isoformat()):
        return today
    if c.get("s") and c["s"] > d.isoformat():
        s = date.fromisoformat(c["s"])
        d = s + timedelta(days=(5 - s.weekday()) % 7)
    if c.get("e") and c["e"] < d.isoformat():
        return None
    return d


def dated(u, d):
    """楽天トラベルの宿の広告リンク（pc=…f_no=番号）を、同じ広告のまま日付つきのプラン一覧に替える。だめなら元のまま"""
    if not d or not DATED_OK:
        return u
    pu = urllib.parse.urlparse(u)
    q = urllib.parse.parse_qs(pu.query)
    no = urllib.parse.parse_qs(urllib.parse.urlparse(q.get("pc", [""])[0]).query).get("f_no", [""])[0]
    if "hb.afl.rakuten.co.jp" not in pu.netloc or not no.isdigit():
        return u
    n = d + timedelta(days=1)
    tgt = (f"https://hotel.travel.rakuten.co.jp/hotelinfo/plan/{no}?f_nen1={d.year}&f_tuki1={d.month}&f_hi1={d.day}"
           f"&f_nen2={n.year}&f_tuki2={n.month}&f_hi2={n.day}&f_heya_su=1&f_otona_su=2")
    return u.split("?")[0] + "?pc=" + urllib.parse.quote(tgt, safe="")


def check_dated():
    """日付つきのプラン一覧が開くかを1回だけ確かめる（開かなければ今までの形のリンクのまま）"""
    import urllib.request
    d = date.today() + timedelta(days=14)
    url = f"https://hotel.travel.rakuten.co.jp/hotelinfo/plan/13449?f_nen1={d.year}&f_tuki1={d.month}&f_hi1={d.day}&f_heya_su=1&f_otona_su=2"
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=15)
        ok = r.status == 200 and "/hotelinfo/plan/13449" in r.geturl()
    except Exception as e:  # noqa: BLE001
        print("日付つきの宿リンク：確かめられない", e)
        return False
    print("日付つきの宿リンク：", "使う" if ok else "使わない", r.geturl()[:120])
    return ok


DATED_OK = False


def hotel(c, h):
    km = "すぐそば" if (h.get("km") or 9) < 0.1 else f"ここから{h['km']}km"
    rv = f"★{float(h['r']):.2f}".rstrip("0").rstrip(".") if h.get("r") else ""
    rc = f"（{int(h['rc']):,}件）" if h.get("rc") else ""
    pr = f"{int(h['min']):,}円〜" if h.get("min") else ""
    d = c.get("sat")
    u = dated(h["u"], d)
    lab = f"{d.month}/{d.day}（{WD[d.weekday()]}）の空室" if d and u != h["u"] else "空室を見る"
    return (f'<li><a href="{E(u)}" target="_blank" rel="noopener sponsored" data-y="宿｜{E(c["t"][:16])}｜{E(h["n"])}">'
            f'<span class="hn">{E(h["n"])}</span><span class="hm"><b>{rv}</b>{rc}・{km}</span><span class="hp"><span class="hy">{pr}</span><span class="hv">{lab}</span></span></a></li>')


def main():
    today = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else (datetime.now(timezone.utc) + timedelta(hours=9)).date()
    yp = os.path.join(SITE, "kanto-yado.json")
    if not os.path.exists(yp):
        print("宿の一覧がないので作らない")
        return
    Y = {re.sub(r"\s+", "", k): v for k, v in json.load(open(yp, encoding="utf-8")).items() if v}
    cards = load_cards(Y)
    global DATED_OK
    DATED_OK = check_dated()
    T = today.isoformat()
    items = {p: [] for p in KANTO_ORDER}
    for k, c in cards.items():
        if c["p"] not in items or not c["href"] or (c["e"] and c["e"] < T):
            continue
        c["on"], c["k"] = bool(c["s"]) and c["s"] <= T, k  # 11/6 夜：始まる日が無い（日程の発表前）物を「開催中」にしない
        c["pre"] = not c["s"]
        c["sat"] = None if c["pre"] else sat_for(c, today)
        items[c["p"]].append(c)
    for p in KANTO_ORDER:
        items[p].sort(key=lambda c: (0, c["e"] or "9") if c["on"] else ((2, "") if c["pre"] else (1, c["s"])))
    n_all = sum(len(v) for v in items.values())
    n_inn = sum(len(Y[c["k"]][:3]) for v in items.values() for c in v)

    secs = []
    for p in KANTO_ORDER:
        if not items[p]:
            continue
        rows = []
        for c in items[p]:
            tag = (f'<span class="st {"on" if c["on"] else ("pre" if c["pre"] else "soon")}">{"開催中" if c["on"] else ("日程は発表前" if c["pre"] else "これから")}</span>'
                   + ('<span class="fr">無料</span>' if c["free"] else ""))
            mp = f'<a class="mp" href="{E(c["mp"])}" target="_blank" rel="noopener" data-k="地図｜{E(c["t"][:14])}">地図</a>' if c["mp"] else ""
            hs = "".join(hotel(c, h) for h in sorted(Y[c["k"]][:3], key=lambda h: h.get("km") or 99))  # 11/6 夜：近い順に
            m = f'<div class="m">{E(c["m"])}</div>' if c["m"] else ""
            rows.append(f'<article class="it" data-s="{E(c["s"])}" data-e="{E(c["e"])}"><a class="card" href="{E(c["href"])}" target="_blank" rel="noopener" data-k="公式｜{E(c["t"][:14])}">'
                        f'<div class="tg">{tag}</div><div class="d">{E(c["d"])}</div><div class="t">{E(c["t"])}</div>{m}<div class="go">公式 →</div></a>'
                        f'<div class="inn"><div class="ih"><span>近くの宿</span>{mp}</div><ul>{hs}</ul></div></article>')
        secs.append(f'<section class="ps" data-p="{p}" style="--c:{PREF_COLOR[p]}"><h2>{p}<small>{len(items[p])}か所</small></h2>{"".join(rows)}</section>')

    # 地図（10/31 オーナー「お泊まりは地図…燈のも」）：月の build_akari.py が作る site/townnotes/map-tomari.js。中身が変わると ?v= も変わる
    _mj = os.path.join(SITE, "townnotes", "map-tomari.js")
    mapjs = (f'<script src="/townnotes/map-tomari.js?v={hashlib.sha1(open(_mj, "rb").read()).hexdigest()[:8]}" defer></script>'
             if os.path.exists(_mj) else "")
    btns = '<button class="on" data-p="すべて">すべて</button>' + "".join(
        f'<button data-p="{p}" style="--pc:{PREF_COLOR[p]}">{p}</button>' for p in KANTO_ORDER if items[p])
    dnote = "<br>「◯/◯（土）の空室」は、その日1泊・大人2人で開きます（日曜は今夜の1泊）。" if DATED_OK else ""
    upd = f"{today.year}年{today.month}月{today.day}日"
    out = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>泊まりで行く関東のおでかけ｜近くの宿つき｜うさぎ│LIFE NOTES</title>
<meta name="description" content="関東の少し遠いおでかけ{n_all}か所と、近くの評価の高い宿をまとめました。東京・神奈川・埼玉・千葉・茨城・栃木・群馬。">
<link rel="canonical" href="{BASE}/tomari"><meta property="og:title" content="泊まりで行く関東のおでかけ"><meta property="og:image" content="{BASE}/logo.png">
<link rel="icon" href="/logo-s.png"><link rel="apple-touch-icon" href="/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=Jost:wght@300;400;500&display=swap">
<style>
body{{margin:0;background:#FFFFFF;font-family:"Zen Kaku Gothic New",sans-serif;color:#2B2622}}
.wrap{{max-width:440px;margin:0 auto;padding:0 16px 40px}}
.head{{text-align:center;padding:34px 0 8px}}
.head img{{width:60px;height:60px;display:block;margin:0 auto;border-radius:50%;background:#fff}}
.en{{font-family:Jost,sans-serif;font-weight:300;font-size:10px;letter-spacing:.42em;color:#8C7B6E;margin-top:12px}}
h1{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:24px;line-height:1.5;letter-spacing:.12em;color:#231E1B;margin:12px 0 8px;font-feature-settings:"palt"}}
.sub{{font-size:13px;line-height:2;color:#6B6058;margin:0}}
.cnt{{display:flex;justify-content:center;gap:18px;margin-top:12px;font-size:12px;color:#6B6058}}.cnt b{{font-family:"Shippori Mincho",serif;font-size:20px;color:#2B2622;margin:0 2px}}
.upd{{font-size:11px;color:#8C7B6E;margin-top:4px}}
.flt{{position:sticky;top:0;z-index:5;background:rgba(253,252,250,.96);display:flex;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;gap:0 16px;margin:20px -16px 0;padding:10px 64px 10px 16px;border-top:1px solid #DDDDDD;border-bottom:1px solid #DDDDDD}}
.flt::-webkit-scrollbar{{display:none}}
.flt button{{flex:none;border:none;background:none;padding:6px 0;font-family:"Zen Kaku Gothic New",sans-serif;font-size:13px;font-weight:700;letter-spacing:.06em;color:var(--pc,#8C7B6E);border-bottom:1px solid transparent;cursor:pointer}}
.flt button.on{{color:var(--pc,#2B2622);border-bottom-color:var(--pc,#2B2622)}}
.wk{{display:flex;justify-content:center;margin:12px 0 0}}
.wk button{{font-family:"Zen Kaku Gothic New",sans-serif;font-size:12px;letter-spacing:.04em;color:#5B5450;background:#fff;border:1px solid #CECECE;border-radius:99px;padding:8px 14px;cursor:pointer}}
.wk button[aria-pressed=true]{{background:#2B2622;border-color:#2B2622;color:#fff}}
.pr{{font-size:11px;line-height:1.8;color:#8C7B6E;text-align:center;margin:10px 0 0}}
.ps{{scroll-margin-top:60px;margin-top:28px}}
h2{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:18px;letter-spacing:.14em;margin:0 0 12px;padding-left:10px;border-left:3px solid var(--c);display:flex;align-items:baseline;gap:10px}}
h2 small{{font-family:"Zen Kaku Gothic New",sans-serif;font-size:11px;color:#8C7B6E;letter-spacing:.04em;font-weight:500}}
.it{{margin-bottom:16px;background:#fff;border:1px solid #DDDDDD;border-radius:4px}}
.card{{display:block;position:relative;text-decoration:none;color:inherit;padding:14px 64px 12px 16px}}
.tg{{display:flex;gap:6px;margin-bottom:6px}}
.st,.fr{{font-size:10.5px;letter-spacing:.06em;padding:1px 7px;border:1px solid;line-height:1.7}}
.st.on{{color:#fff;background:var(--c);border-color:var(--c)}}.st.soon{{color:var(--c)}}.st.pre{{color:#8A8A8A;border-color:#C9C9C9}}.fr{{color:#5F8A5A}}
.d{{font-size:13px;color:var(--c);font-weight:700;letter-spacing:.02em}}
.t{{font-family:"Shippori Mincho",serif;font-weight:600;font-size:16px;line-height:1.5;margin:4px 0}}
.m{{font-size:12px;color:#7A6E66;line-height:1.6}}
.go{{position:absolute;right:14px;top:16px;font-size:11px;letter-spacing:.06em;color:#6B6058;border-bottom:1px solid #CECECE;padding-bottom:1px}}
.inn{{border-top:1px dashed #D7D7D7;margin:0 16px;padding:10px 0 6px}}
.ih{{display:flex;justify-content:space-between;align-items:center;font-size:11px;letter-spacing:.14em;color:#8C7B6E;margin-bottom:2px}}
.ih .mp{{font-size:11px;letter-spacing:.08em;color:#6B6058;text-decoration:none;border-bottom:1px solid #CECECE;padding:4px 0 1px}}
.inn ul{{list-style:none;margin:0;padding:0}}
.inn li{{border-top:1px solid #ECECEC}}.inn li:first-child{{border-top:0}}
.inn li a{{display:grid;grid-template-columns:1fr auto;column-gap:10px;padding:10px 0;text-decoration:none;color:#2B2622;min-height:44px;box-sizing:border-box}}
.hn{{font-size:13.5px;font-weight:700;line-height:1.45;grid-column:1}}
.hm{{grid-column:1;font-size:11px;color:#857A70;margin-top:2px}}.hm b{{color:#B5532F;font-weight:700}}
.hp{{grid-column:2;grid-row:1/3;align-self:center;display:flex;flex-direction:column;align-items:flex-end;gap:5px;white-space:nowrap}}
.hy{{font-family:Jost,sans-serif;font-size:13px;color:#2B2622}}
.hv{{font-size:11px;font-weight:700;color:#B5532F;border:1px solid #B5532F;border-radius:999px;padding:3px 10px;line-height:1.4}}
.hv:after{{content:" →"}}
.none{{display:none;text-align:center;font-size:13px;color:#8C7B6E;padding:40px 0}}
.note{{font-size:12px;line-height:1.9;color:#7A6E66;background:#F1F1F1;padding:14px 16px;margin-top:30px}}
.back{{display:block;width:max-content;margin:28px auto 0;color:#2B2622;text-decoration:none;font-size:13px;letter-spacing:.1em;border-bottom:1px solid #2B2622;padding-bottom:2px}}
.ft{{text-align:center;font-size:10px;letter-spacing:.04em;color:#8C7B6E;margin-top:30px}}
</style><script src="/assets/night.js?v=14"></script><script src="/assets/menu.js?v=30" defer></script><link rel="stylesheet" href="/assets/sub.css?v=4"><script src="/assets/v2sub.js?v=11" defer></script></head><body><div class="wrap">
<header class="head"><img src="/logo-s.png" width="60" height="60" alt="うさぎ│LIFE NOTES"><div class="en">STAY &amp; GO</div>
<h1>泊まりで行くおでかけ</h1><p class="sub">関東の少し遠いおでかけと、<br>近くの評価の高い宿をまとめました。</p>
<div class="cnt"><span>おでかけ<b>{n_all}</b>か所</span><span>宿<b>{n_inn}</b>軒</span></div><div class="upd">{upd} 更新</div></header>
<div class="flt" id="flt">{btns}</div>
<div class="wk"><button type="button" id="wk" aria-pressed="false">この週末に開いている所だけ</button></div>
<p class="pr">宿は楽天トラベルの評価3.5以上・口コミ10件以上から、評価の高い順に3軒。<br>値段は1泊の最安の目安で、日や人数で変わります。{dnote}宿のリンクは広告（PR）です。</p>
{"".join(secs)}
<div class="none" id="none">この週末に開いている所はありません。</div>
<div class="note">おでかけの日にちや時間は、出かける前に必ず公式ページで確かめてください。宿の空きや値段は楽天トラベルでご確認ください。</div>
<a class="back" href="/">関東おでかけリストへ戻る</a>
<div class="ft">うさぎ│LIFE NOTES　関東おでかけリスト</div></div>
<script>(function(){{
var B=document.querySelectorAll("#flt button"),S=document.querySelectorAll(".ps"),wk=document.getElementById("wk"),P="すべて",W=false;
function we(){{var n=new Date(Date.now()+9*36e5),d=n.getUTCDay(),sat=new Date(n);sat.setUTCDate(n.getUTCDate()+((6-d+7)%7));if(d===0)sat.setUTCDate(n.getUTCDate()-1);var sun=new Date(sat);sun.setUTCDate(sat.getUTCDate()+1);return [sat.toISOString().slice(0,10),sun.toISOString().slice(0,10)];}}
var WE=we(),T=new Date(Date.now()+9*36e5).toISOString().slice(0,10);
/* 作り直しの前に終わった物は、ページ側で隠す */
document.querySelectorAll(".it").forEach(function(it){{if(it.dataset.e&&it.dataset.e<T)it.remove();}});
function draw(){{var any=0;S.forEach(function(s){{var on=P==="すべて"||s.dataset.p===P,c=0;s.querySelectorAll(".it").forEach(function(it){{var a=it.dataset.s||"0000",e=it.dataset.e||"9999",ok=!W||(it.dataset.s&&a<=WE[1]&&e>=WE[0])/* 11/6 夜：日程の発表前は週末に入れない */;it.hidden=!ok;if(ok)c++;}});var h=s.querySelector("h2 small");if(h)h.textContent=c+"か所";s.hidden=!on||!c;if(on&&c)any++;}});document.getElementById("none").style.display=any?"none":"block";}}
function ck(f,k){{try{{navigator.sendBeacon("/c?f="+f+"&s="+f+"&k="+encodeURIComponent(k.slice(0,40)));}}catch(e){{}}}}
B.forEach(function(b){{b.addEventListener("click",function(){{B.forEach(function(x){{x.classList.toggle("on",x===b)}});P=b.dataset.p;draw();ck("tomari","絞り込み："+P);var t=document.querySelector(".flt").getBoundingClientRect().top+scrollY;if(scrollY>t)scrollTo({{top:t,behavior:"smooth"}});}});}});
wk.addEventListener("click",function(){{W=!W;wk.setAttribute("aria-pressed",W);draw();ck("tomari","この週末");}});
document.addEventListener("click",function(e){{var a=e.target.closest&&e.target.closest("a[data-k],a[data-y]");if(!a)return;if(a.dataset.y)ck("yado",a.dataset.y);else ck("tomari",a.dataset.k);}},true);
draw();ck("tomari","表示");
}})();</script>{mapjs}</body></html>
'''
    open(os.path.join(SITE, "tomari.html"), "w", encoding="utf-8").write(out)
    print(json.dumps({"tomari": n_all, "yado": n_inn}, ensure_ascii=False))


if __name__ == "__main__":
    main()
