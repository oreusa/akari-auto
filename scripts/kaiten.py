"""関東の開店・閉店ニュース（/kaiten）を作る。11/17 月（関西 https://kansai.townnote.app/kaiten と同じ形。usagi tools/kaiten/build.py）。
元は data/kaiten.json（月の毎晩 21:20 の回が「速報の種」の【速報 関東】から足す）。
頭（題・フォント・night.js・menu.js）は関東の紅葉ページ（site/koyo.html）から借り、中身と見た目はここで全部書く。夜の色は night.js が作る。
使い方: python3 scripts/kaiten.py                  （page.yml で koyo.py のあと。失敗してもHPは出す）
        python3 scripts/kaiten.py add '{"d":"2026-11-20","k":"open","p":"東京","n":"名前","pt":"新しい点","pl":"場所","tm":"","u":"https://..."}' …"""
import datetime, html, json, os, re, sys, urllib.parse
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SITE = os.path.join(ROOT, "site")
DATA = os.path.join(ROOT, "data", "kaiten.json")
BASE = "https://usagi-life-notes.pages.dev/"  # page.yml が LIFE_BASE（kanto.townnote.app）に置き換える
E = html.escape
DONE_DAYS = 30
PREFS = ["東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬"]
KL = {"open": "開店", "pop": "期間限定", "close": "閉店"}
WD = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
TODAY = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date()


def add(rows):
    j = json.load(open(DATA, encoding="utf-8"))
    have = {(x["u"], x["n"]) for x in j["items"]}
    n = 0
    for r in rows:
        x = json.loads(r)
        for k in ("d", "k", "p", "n", "pt", "pl", "u"):
            assert x.get(k), f"{k} が無い: {r}"
        assert x["k"] in KL and x["p"] in PREFS and x["u"].startswith("https://"), r
        d = datetime.date.fromisoformat(x["d"])
        if (x["u"], x["n"]) in have or (x["k"] == "close" and d < TODAY) or (d - TODAY).days < -DONE_DAYS:
            print("足さない:", x["n"]); continue
        x.setdefault("tm", ""); x["added"] = TODAY.isoformat()
        j["items"].append(x); have.add((x["u"], x["n"])); n += 1
    json.dump(j, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("足した", n, "件・全部", len(j["items"]), "件")


def bucket(x, t=TODAY):
    n = (datetime.date.fromisoformat(x["d"]) - t).days
    if x["k"] == "close":
        return "close" if n >= 0 else None
    if n >= 0:
        return "soon"
    if x["k"] == "pop" and x.get("end"):
        return "done" if datetime.date.fromisoformat(x["end"]) >= t else None
    return "done" if n >= -DONE_DAYS else None


def card(x):
    q = urllib.parse.quote(re.sub(r"（.*?）|「|」", " ", x["n"]) + " " + (x["pl"].split("・")[0] or x["p"]))
    end = f' data-end="{x["end"]}"' if x.get("end") else ""
    return (f'<article class="it" data-d="{x["d"]}" data-k="{x["k"]}" data-p="{x["p"]}"{end}><span class="tag {x["k"]}">{KL[x["k"]]}</span>'
            f'<h3 class="nm">{E(x["n"])}</h3><p class="pt">{E(x["pt"])}</p><dl><dt>場所</dt><dd>{E(x["p"])}{"・" + E(x["pl"]) if x.get("pl") else ""}</dd>'
            + (f'<dt>時間</dt><dd>{E(x["tm"])}</dd>' if x.get("tm") else "") + "</dl>"
            f'<div class="ln"><a class="src" href="{E(x["u"])}" target="_blank" rel="noopener" data-k="公式の発表｜{E(x["n"])}">公式の発表 ↗</a>'
            f'<a href="https://www.google.com/maps/search/?api=1&amp;query={q}" target="_blank" rel="noopener" data-k="地図｜{E(x["n"])}">地図</a></div></article>')


def fz(f):
    m = re.match(r"(?:(\d{4})年)?(\d+)月(.*)", f)
    if not m:
        return f, ""
    return f"{m.group(2)}月", (m.group(3) or m.group(1) or "")  # 11月／下旬、3月／2027


CSS = """<style>
body{margin:0;background:#fff;color:#2B2622;font-family:"Zen Kaku Gothic New",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:480px;margin:0 auto;padding:0 16px 120px}
.head{text-align:center;padding:30px 0 6px}.head img{border-radius:50%}
.en{font-family:Jost,sans-serif;font-weight:300;font-size:10px;letter-spacing:.42em;color:#8C7B6E;margin-top:8px}
h1{font-family:"Shippori Mincho",serif;font-weight:600;font-size:25px;line-height:1.5;letter-spacing:.1em;color:#231E1B;margin:12px 0 8px;font-feature-settings:"palt"}
h1 span{display:block;font-size:14px;letter-spacing:.08em;color:#6B6058;margin-top:2px}
.sub{font-size:13px;line-height:2;color:#6B6058;margin:0}
.upd{font-size:11px;letter-spacing:.08em;color:#8C7B6E;margin-top:10px}
.cnt{display:grid;grid-template-columns:repeat(3,1fr);margin:18px 0 0;border-top:1px solid #E6E0D9;border-bottom:1px solid #E6E0D9}
.cnt div{text-align:center;padding:12px 4px 11px;border-left:1px solid #E6E0D9}.cnt div:first-child{border-left:0}
.cnt small{display:block;font-size:10.5px;letter-spacing:.12em;color:#8C7B6E}
.cnt b{display:block;font-family:"Shippori Mincho",serif;font-weight:600;font-size:24px;color:#231E1B;margin-top:2px;font-variant-numeric:tabular-nums}
.kbar{background:#fff;margin:10px -16px 0;padding:10px 16px 8px;border-bottom:1px solid #E6E0D9}
.seg{display:grid;grid-template-columns:repeat(3,1fr);background:#F1EEEA;border-radius:10px;padding:3px}
.seg button{font:700 13px "Zen Kaku Gothic New",sans-serif;letter-spacing:.06em;border:0;background:transparent;color:#8C7B6E;padding:8px 0;border-radius:8px;cursor:pointer}
.seg button[aria-pressed=true]{background:#fff;color:#2B2622;box-shadow:0 1px 2px rgba(0,0,0,.08)}
.kpref{display:flex;gap:0 16px;overflow-x:auto;scrollbar-width:none;margin-top:8px}.kpref::-webkit-scrollbar{display:none}
.kpref button{flex:none;font:700 13px "Zen Kaku Gothic New",sans-serif;letter-spacing:.06em;border:0;background:none;color:#8C7B6E;padding:6px 0;border-bottom:1.5px solid transparent;cursor:pointer}
.kpref button[aria-pressed=true]{color:#2B2622;border-bottom-color:#2B2622}
.day{display:grid;grid-template-columns:62px 1fr;gap:0 14px;padding:18px 0 4px;border-bottom:1px solid #E6E0D9}
.dt{position:sticky;top:12px;align-self:start}
.dt .md{font-family:Jost,sans-serif;font-size:22px;letter-spacing:.02em;color:#231E1B;line-height:1.1;font-variant-numeric:tabular-nums}
.dt .wd{font-family:Jost,sans-serif;font-size:10px;letter-spacing:.3em;color:#8C7B6E;margin-top:4px}
.dt .left{display:inline-block;font-size:10.5px;font-weight:700;color:#6B6058;margin-top:6px}.dt .left.today{color:#3E6B57}
.items{display:grid;gap:14px;min-width:0;padding-bottom:12px}.it{min-width:0}.it+.it{border-top:1px dashed #E6E0D9;padding-top:14px}
.day[hidden],.it[hidden]{display:none}
.tag{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.06em;border-radius:5px;padding:1px 7px;margin-bottom:4px}
.tag.open{color:#3E6B57;background:#E8F0EB}.tag.close{color:#9A4B3C;background:#F5E6E2}.tag.pop{color:#7A5A2E;background:#F3ECE0}
.nm{font-family:"Shippori Mincho",serif;font-weight:600;font-size:16.5px;line-height:1.6;letter-spacing:.03em;color:#231E1B;margin:0;word-break:auto-phrase}
.pt{font-size:13.5px;line-height:1.85;margin:4px 0 0}
.it dl{display:grid;grid-template-columns:auto 1fr;gap:2px 10px;margin:8px 0 0;font-size:12.5px;line-height:1.75}
.it dt{color:#8C7B6E;letter-spacing:.06em}.it dd{margin:0;color:#6B6058;min-width:0;overflow-wrap:anywhere}
.ln{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.ln a{font-size:12.5px;font-weight:700;color:#2B2622;text-decoration:none;border:1px solid #E6E0D9;border-radius:99px;padding:6px 12px}.ln a.src{background:#F7F5F2}
.kempty{font-size:13px;color:#6B6058;text-align:center;padding:36px 0;display:none}
.note{font-size:12px;line-height:1.9;color:#6B6058;background:#F7F5F2;border-radius:10px;padding:14px 16px;margin-top:24px}
.kfol{margin-top:18px;text-align:center}.kfol p{font-size:13px;line-height:1.9;color:#6B6058;margin:0 0 10px}
.kfol a{display:inline-block;margin:0 4px 8px;font-size:13px;font-weight:700;text-decoration:none;border-radius:99px;padding:9px 16px;background:#2B2622;color:#fff}
.kfol a+a{background:#fff;color:#2B2622;box-shadow:inset 0 0 0 1px #2B2622}
.also{margin-top:22px}.also small{display:block;font-size:11px;letter-spacing:.14em;color:#8C7B6E;margin-bottom:8px}
.also a{display:inline-block;margin:0 8px 8px 0;padding:7px 13px;border:1px solid #D9D2CB;border-radius:99px;color:#2B2622;text-decoration:none;font-size:12.5px}
.back{display:block;text-align:center;border:1px solid #2B2622;border-radius:12px;padding:13px 16px;margin:18px 0 10px;color:#2B2622;text-decoration:none;font-weight:700;font-size:14px}
.sign{text-align:center;font-family:Jost,sans-serif;font-size:11px;letter-spacing:.3em;color:#8C7B6E}
</style>"""


def build():
    items = json.load(open(DATA, encoding="utf-8"))["items"]
    live = [x for x in items if bucket(x)]
    for x in live:
        assert x["p"] in PREFS, x["n"]
    cnt = {k: sum(bucket(x) == k for x in live) for k in ("soon", "done", "close")}
    groups = {}
    for x in sorted(live, key=lambda x: (x["d"], x["k"] != "close", x["n"])):
        groups.setdefault(x.get("fuzzy") or x["d"], {"d": x["d"], "f": x.get("fuzzy"), "a": []})["a"].append(x)
    body = ""
    for g in groups.values():
        d = datetime.date.fromisoformat(g["d"])
        if g["f"]:
            md, yr = fz(g["f"])
        else:
            md, yr = f"{d.month}.{d.day:02d}", (str(d.year) if d.year != TODAY.year else "")
        wd = yr or ("" if g["f"] else WD[d.weekday()])
        body += (f'<section class="day" data-d="{g["d"]}"' + (' data-f="1"' if g["f"] else "") + f'><div class="dt"><div class="md">{E(md)}</div>'
                 f'<div class="wd">{wd}</div><span class="left"></span></div><div class="items">' + "".join(card(x) for x in g["a"]) + "</div></section>")
    N = len(live)
    k = open(os.path.join(SITE, "koyo.html"), encoding="utf-8").read()
    head = k[:k.index("</head>")]
    head = re.sub(r"<style>.*?</style>", "", head, flags=re.S)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', "", head, flags=re.S)
    head = re.sub(r'<link rel="stylesheet" href="/assets/sub.css[^>]*>|<script src="/assets/yado.js[^>]*></script>', "", head)
    title = f"関東の開店・閉店ニュース｜新しいお店・閉まるお店を公式の発表で（{TODAY.month}月{TODAY.day}日）"
    desc = (f"東京・神奈川・埼玉・千葉など関東で、これから開くお店{cnt['soon']}件・この{DONE_DAYS}日に開いたお店{cnt['done']}件・閉まるお店{cnt['close']}件。"
            "各社の公式の発表だけを毎日たしかめて足しています。日付・場所と、公式の発表と地図へすぐ行けます。")
    head = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", head, count=1)
    for p in ('name="description"', 'property="og:description"'):
        head = re.sub(rf'(<meta {p} content=")[^"]*', lambda m: m.group(1) + E(desc), head, count=1)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + "関東の開店・閉店ニュース", head, count=1)
    head = re.sub(r'(<meta property="article:modified_time" content=")[^"]*', lambda m: m.group(1) + TODAY.isoformat() + "T07:00:00+09:00", head, count=1)
    head = re.sub(r'(<link rel="canonical" href="[^"]*?/)koyo"', r'\1kaiten"', head, count=1)
    head = re.sub(r'(<meta property="og:url" content="[^"]*?/)koyo"', r'\1kaiten"', head, count=1)
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": "関東の開店・閉店ニュース",
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": x["n"], "url": x["u"]} for i, x in enumerate(sorted(live, key=lambda x: x["d"]))]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "関東おでかけリスト", "item": BASE + "odekake"},
              {"@type": "ListItem", "position": 2, "name": "関東の開店・閉店ニュース", "item": BASE + "kaiten"}]}]
    head += CSS + "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in ld)
    top = ('<div class="cnt" aria-label="件数"><div><small>これから開く</small><b id="n-soon">%d</b></div><div><small>この%d日に開いた</small><b id="n-done">%d</b></div>'
           '<div><small>閉まる</small><b id="n-close">%d</b></div></div>' % (cnt["soon"], DONE_DAYS, cnt["done"], cnt["close"])
           + '<div class="kbar"><div class="seg" role="group" aria-label="見るもの"><button type="button" data-v="soon" aria-pressed="true">これから</button>'
           '<button type="button" data-v="done" aria-pressed="false">開いた</button><button type="button" data-v="close" aria-pressed="false">閉まる</button></div>'
           '<div class="kpref" role="group" aria-label="都県"><button type="button" data-p="" aria-pressed="true">すべて</button>'
           + "".join(f'<button type="button" data-p="{p}" aria-pressed="false">{p}</button>' for p in PREFS if any(x["p"] == p for x in live)) + "</div></div>")
    JS = ('<script>(function(){var O=false;try{O=localStorage.getItem("usagi_owner")==="1";}catch(e){}'
          'function c(k){if(O)return;try{var b=JSON.stringify({k:k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true});}catch(e){}}'
          'c("表示：開店・閉店ニュース"+(document.referrer&&!/townnote\\.(pages|app)|life-notes|lifenote/.test(document.referrer)?"（外から）":""));'
          'document.addEventListener("click",function(e){var a=e.target.closest?e.target.closest("[data-k]"):null;if(a)c("クリック：開店・閉店ニュース｜"+a.getAttribute("data-k"));});'
          'var T=new Date();T=new Date(T.getTime()+(T.getTimezoneOffset()+540)*6e4);T=T.getFullYear()+"-"+("0"+(T.getMonth()+1)).slice(-2)+"-"+("0"+T.getDate()).slice(-2);'
          'function dd(a){return Math.round((new Date(a+"T00:00:00")-new Date(T+"T00:00:00"))/864e5)}'
          'function bk(x){var n=dd(x.dataset.d),k=x.dataset.k;if(k==="close")return n>=0?"close":"";if(n>=0)return "soon";if(k==="pop"&&x.dataset.end)return dd(x.dataset.end)>=0?"done":"";return n>=-%d?"done":""}'
          'var view="soon",pref="",L=document.getElementById("klist"),D=[].slice.call(L.querySelectorAll(".day"));'
          'function go(){var c={soon:0,done:0,close:0},any=false;D.forEach(function(s){var sh=0;s.querySelectorAll(".it").forEach(function(x){var b=bk(x);if(b)c[b]++;var on=b===view&&(!pref||x.dataset.p===pref);x.hidden=!on;if(on)sh++});s.hidden=!sh;if(sh)any=true;'
          'var n=dd(s.dataset.d),l=s.querySelector(".left");l.textContent=s.dataset.f?"日付はまだ":n===0?"きょう":n>0?"あと"+n+"日":(-n)+"日前";l.className="left"+(n===0?" today":"")});'
          '["soon","done","close"].forEach(function(k){document.getElementById("n-"+k).textContent=c[k]});document.getElementById("kempty").style.display=any?"none":"block";'
          'D.slice().sort(function(a,b){return view==="done"?(a.dataset.d<b.dataset.d?1:-1):(a.dataset.d<b.dataset.d?-1:1)}).forEach(function(s){L.insertBefore(s,document.getElementById("kempty"))})}'
          'document.querySelectorAll(".seg button").forEach(function(b){b.onclick=function(){view=b.dataset.v;document.querySelectorAll(".seg button").forEach(function(x){x.setAttribute("aria-pressed",x===b)});go();c("開店・閉店｜"+b.textContent)}});'
          'document.querySelectorAll(".kpref button").forEach(function(b){b.onclick=function(){pref=b.dataset.p;document.querySelectorAll(".kpref button").forEach(function(x){x.setAttribute("aria-pressed",x===b)});go();c("開店・閉店｜都県 "+(pref||"すべて"))}});'
          'go();})();</script>') % DONE_DAYS
    s = (head + '</head><body data-kind="開店・閉店ニュース"><div class="wrap"><header class="head"><img src="/logo.png" width="60" height="60" alt="LIFE NOTE のロゴ">'
         '<div class="en">KANTO NEW SHOPS</div><h1>関東の開店・閉店ニュース<span>新しいお店・閉まるお店を公式の発表で</span></h1>'
         '<p class="sub">お店や施設の公式の発表だけを、毎日たしかめて足しています。<br>日付と街で、近くの新しいお店がすぐ分かります。</p>'
         f'<div class="upd">{TODAY.year}年{TODAY.month}月{TODAY.day}日 更新・{N}件</div></header>' + top
         + f'<main id="klist">{body}<p class="kempty" id="kempty">この条件のお店は、いまはありません。</p></main>'
         '<p class="note">日付・時間・内容は、各社の公式の発表をもとにしています。変わることがあるので、出かける前に「公式の発表」で確かめてください。閉店のセールの日数や値引きの中身は、発表に書かれた物だけを載せています。</p>'
         '<div class="kfol"><p>新しいお店の速報は、毎日 X にも出しています。</p><a href="https://x.com/ai_usagichan" target="_blank" rel="noopener" data-k="速報｜Xで毎日見る">X で毎日見る</a>'
         '<a href="https://www.threads.com/@usagichan_ai_si" target="_blank" rel="noopener" data-k="速報｜Threadsで見る">Threads で見る</a></div>'
         '<nav class="also" aria-label="あわせて見る"><small>あわせて見る</small><a href="/odekake" data-k="あわせて：おでかけリスト">関東おでかけリスト</a>'
         '<a href="/ima" data-k="あわせて：いま行ける">今から行ける所</a><a href="/illumination" data-k="あわせて：イルミネーション">関東のイルミネーション</a></nav>'
         '<a class="back" href="/odekake">関東おでかけリストを見る</a><p class="sign">LIFE NOTE</p></div>' + JS + "</body></html>")
    assert "紅葉" not in s[s.index("<body"):], "紅葉の言葉が残っている"
    open(os.path.join(SITE, "kaiten.html"), "w", encoding="utf-8").write(s)
    sm = os.path.join(SITE, "sitemap.xml")
    if os.path.exists(sm):
        x = open(sm, encoding="utf-8").read()
        if "/kaiten<" not in x:
            open(sm, "w", encoding="utf-8").write(x.replace("</urlset>", f"<url><loc>{BASE}kaiten</loc><lastmod>{TODAY}</lastmod></url></urlset>", 1))
    print("kaiten", N, cnt)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "add":
        add(sys.argv[2:])
    build()
