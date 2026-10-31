"""関東イルミネーション2026-2027のまとめページ（site/illumination.html）と、検索用の robots.txt・sitemap.xml を作る。
10/31 月からの頼み（オーナー経由）：Googleで「イルミネーション 東京 2026」と調べた人を、SNSを見ていなくても関東おでかけリストに呼ぶ。
元は data/illumi.json。終わった物は作る時に外し、ページを開いた日にも JS で隠す。開催中／これからは開いた日で決まる。"""
import html, json, os, sys, urllib.parse
from datetime import date, datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://usagi-life-notes.pages.dev"
PAGE = "illumination"  # Cloudflare Pages は .html を外したアドレスに直すので、正しいアドレスはこちら
PREFS = [("東京", "東京都"), ("神奈川", "神奈川県"), ("埼玉", "埼玉県"), ("千葉", "千葉県"),
         ("茨城", "茨城県"), ("栃木", "栃木県"), ("群馬", "群馬県")]
YADO = {"東京": "tokyo", "神奈川": "kanagawa", "埼玉": "saitama", "千葉": "chiba",
        "茨城": "ibaraki", "栃木": "tochigi", "群馬": "gunma"}
WEEK = "月火水木金土日"


def esc(s):
    return html.escape(str(s or ""), quote=True)


def md(s):
    d = date.fromisoformat(s)
    return f"{d.month}/{d.day}（{WEEK[d.weekday()]}）"


def yado(pref):
    """遠出の所だけ：その県の宿の一覧（楽天トラベル）。鍵のない手元では広告にしない"""
    url = f"https://travel.rakuten.co.jp/yado/{YADO[pref]}/"
    aid = os.environ.get("RAKUTEN_AFFILIATE_ID")
    if not aid:
        return url
    enc = urllib.parse.quote(url, safe="")
    return f"https://hb.afl.rakuten.co.jp/hgc/{aid}/?pc={enc}&m={enc}"


def card(e, today):
    known = bool(e.get("start"))
    if known:
        st = "now" if date.fromisoformat(e["start"]) <= today else "soon"
        badge = "開催中" if st == "now" else "これから"
        when = md(e["start"]) if e["start"] == e["end"] else f'{md(e["start"])}〜{md(e["end"])}'
    else:
        st, badge = "tba", "発表前"
        when = f'2026年の日程は発表前（昨年 {esc(e.get("last", ""))}）'
    free = '<span class="fr">無料</span>' if e.get("free") is True else ""
    data = f'data-s="{esc(e.get("start") or "")}" data-e="{esc(e.get("end") or "")}" data-p="{esc(e["pref"])}"'
    # 地図：Googleマップで会場を開く（10/31 オーナー「地図もつけよう」）。同じ言葉で TOWN NOTES の地図のピンも立てる（scripts/townnotes.py）
    q = f'{e["venue"]} {dict(PREFS)[e["pref"]]}{e["city"]}'
    gm = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(q)
    out = (f'<li class="it" {data}><div class="cw"><a class="cd" href="{esc(e["url"])}" target="_blank" rel="noopener">'
           f'<span class="bd"><span class="st {st}">{badge}</span>{free}</span>'
           f'<span class="dt">{when}</span><span class="nm">{esc(e["name"])}</span>'
           f'<span class="pl">{esc(e["city"])}｜{esc(e["venue"])}</span><span class="ar">→</span></a>'
           f'<a class="mp" href="{esc(gm)}" target="_blank" rel="noopener">地図</a></div>')
    if e.get("far"):
        out += (f'<a class="yd" href="{esc(yado(e["pref"]))}" target="_blank" rel="noopener sponsored">'
                f'遠出になるので、近くの宿をさがす（楽天トラベル）</a>')
    return out + "</li>"


def render(items, today, now):
    n = len(items)
    secs, tabs = [], ['<button class="on" data-f="">すべて</button>']
    for p, full in PREFS:
        rows = [e for e in items if e["pref"] == p]
        if not rows:
            continue
        tabs.append(f'<button data-f="{p}">{p}</button>')
        secs.append(f'<section class="ps" data-p="{p}"><h2>{full}<b class="c">{len(rows)}件</b></h2>'
                    f'<ul>{"".join(card(e, today) for e in rows)}</ul></section>')
    names = [e["name"] for e in items if e.get("start")][:3]
    desc = (f"関東（東京・神奈川・埼玉・千葉・茨城・栃木・群馬）のイルミネーション2026-2027を{n}か所、"
            f"都県ごとに日程・場所・無料かどうかで一覧に。{'・'.join(names)}など。{now.year}年{now.month}月{now.day}日更新。")
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": "関東イルミネーション2026-2027 日程一覧",
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "item": {
              "@type": "Event", "name": e["name"], "startDate": e["start"], "endDate": e["end"],
              "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
              "location": {"@type": "Place", "name": e["venue"],
                           "address": f'{dict(PREFS)[e["pref"]]}{e["city"]}'}, "url": e["url"]}}
              for i, e in enumerate(x for x in items if x.get("start"))]}
    return TEMPLATE.format(
        n=n, desc=esc(desc), url=f"{SITE}/{PAGE}", tabs="".join(tabs), secs="".join(secs),
        upd=f"{now.year}年{now.month}月{now.day}日 更新",
        ld=json.dumps(ld, ensure_ascii=False).replace("</", "<\\/"))


TEMPLATE = """<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>関東イルミネーション2026-2027｜東京・神奈川・埼玉・千葉・茨城・栃木・群馬の日程一覧</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="関東イルミネーション2026-2027 日程一覧｜うさぎ│LIFE NOTES">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://usagi-life-notes.pages.dev/og-v10.png">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#FAF8F5">
<link rel="icon" href="logo.png"><link rel="apple-touch-icon" href="logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=Jost:wght@300;400&display=swap">
<script type="application/ld+json">{ld}</script>
<style>
/* 地図（townnotes/map-illumi.js）も .pf .fr .ar .st などを使うので、ページの見た目はカードや箱の中だけにかける */
:root{{color-scheme:light;--bg:#FDFCFA;--ink:#2B2622;--sub:#6B6058;--mute:#8C7B6E;--line:#E6DED4;--line2:#D6CCC1;
  --brown:#A07E66;--brown2:#8C6A55;--free:#5E8A4A;--now:#B5643F;--soon:#71849B;
  --min:"Shippori Mincho","Hiragino Mincho ProN","Yu Mincho",serif;--go:"Zen Kaku Gothic New","Hiragino Sans","Noto Sans JP",sans-serif;
  --en:"Jost","Futura","Avenir Next",sans-serif}}
*{{box-sizing:border-box}}
html{{-webkit-text-size-adjust:100%}}
body{{margin:0;background:var(--bg);color:var(--ink);font:400 14px/1.7 var(--go)}}
a{{color:inherit;text-decoration:none}}
a:focus-visible,button:focus-visible{{outline:1px solid var(--brown);outline-offset:3px}}
.wrap{{max-width:460px;margin:0 auto;padding:0 max(16px,env(safe-area-inset-right,0px)) 48px max(16px,env(safe-area-inset-left,0px))}}
.head{{text-align:center;padding:40px 0 8px}}
.head img{{width:64px;height:64px;display:block;margin:0 auto;border-radius:50%;background:#fff}}
.en{{font:300 10px/1 var(--en);letter-spacing:.5em;color:var(--brown);margin:16px 0 0;padding-left:.5em}}
h1{{font:600 23px/1.45 var(--min);letter-spacing:.1em;font-feature-settings:"palt";margin:14px 0 6px}}
h1 small{{display:block;font-size:15px;letter-spacing:.2em;margin-top:4px}}
.up{{font-size:11.5px;color:var(--mute);margin:0}}
.lead{{font-size:12.5px;line-height:1.95;color:var(--sub);margin:14px 0 0;text-align:left}}
.tabs{{display:flex;gap:6px;overflow-x:auto;margin:22px -2px 6px;padding:2px;scrollbar-width:none;position:sticky;top:0;background:var(--bg);z-index:2}}
.tabs::-webkit-scrollbar{{display:none}}
.tabs button{{flex:none;font:700 12.5px/1 var(--go);letter-spacing:.06em;color:var(--mute);background:#fff;border:1px solid #D9CFC4;border-radius:99px;padding:10px 14px;cursor:pointer}}
.tabs button.on{{background:var(--ink);border-color:var(--ink);color:#fff}}
.ps h2{{display:flex;align-items:baseline;gap:8px;font:600 17px/1.4 var(--min);letter-spacing:.12em;margin:26px 0 10px;padding-bottom:8px;border-bottom:1px solid var(--line2)}}
.ps h2 .c{{font:400 12px/1 var(--go);color:var(--mute);letter-spacing:.04em}}
ul{{list-style:none;margin:0;padding:0}}
.it{{margin:0 0 10px}}
.cw{{position:relative}}
.cd{{position:relative;display:block;background:#fff;border:1px solid var(--line);border-radius:4px;padding:12px 34px 36px 14px}}
.mp{{position:absolute;left:14px;bottom:10px;font-size:11px;letter-spacing:.08em;color:var(--sub);border-bottom:1px solid var(--line2);line-height:1.4;padding:6px 8px 0 0}}
.mp:before{{content:"";display:inline-block;width:8px;height:10px;margin-right:4px;vertical-align:-1px;background:currentColor;-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 10'%3E%3Cpath d='M4 0a4 4 0 0 0-4 4c0 3 4 6 4 6s4-3 4-6a4 4 0 0 0-4-4z'/%3E%3C/svg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 10'%3E%3Cpath d='M4 0a4 4 0 0 0-4 4c0 3 4 6 4 6s4-3 4-6a4 4 0 0 0-4-4z'/%3E%3C/svg%3E") center/contain no-repeat}}
.bd{{display:flex;gap:6px;margin-bottom:4px}}
.cd .st,.cd .fr{{font:700 10.5px/1 var(--go);letter-spacing:.08em;padding:4px 7px;border-radius:2px}}
.cd .st.now{{background:var(--now);color:#fff}} .cd .st.soon{{background:#fff;color:var(--soon);border:1px solid var(--soon)}}
.cd .st.tba{{background:#F1ECE6;color:var(--mute)}}
.cd .fr{{color:var(--free);border:1px solid #CFE0CC}}
.dt{{display:block;font-size:12.5px;color:var(--sub)}}
.nm{{display:block;font:600 15px/1.5 var(--min);letter-spacing:.04em;margin:2px 0}}
.pl{{display:block;font-size:12px;color:var(--mute)}}
.cd .ar{{position:absolute;right:14px;top:50%;transform:translateY(-50%);color:var(--brown);font-family:var(--en)}}
.yd{{display:block;font-size:11px;color:var(--brown2);text-decoration:underline;text-underline-offset:3px;margin:5px 2px 0;text-align:right}}
.none{{font-size:12.5px;color:var(--mute);text-align:center;margin:14px 0}}
.foot{{font-size:11.5px;line-height:1.9;color:var(--sub);border-top:1px solid var(--line2);margin-top:32px;padding-top:16px}}
.back{{display:block;text-align:center;font:700 13px/1 var(--go);letter-spacing:.1em;border:1px solid var(--ink);border-radius:2px;padding:14px;margin:20px 0 0;background:#fff}}
.sign{{text-align:center;font:400 11px/1 var(--en);letter-spacing:.3em;color:var(--brown);margin:24px 0 0}}
</style></head>
<body><div class="wrap">
<header class="head">
<img src="logo-s.png" alt="うさぎ│LIFE NOTES のロゴ" width="64" height="64">
<p class="en">KANTO ILLUMINATION</p>
<h1>関東イルミネーション<small>2026 - 2027 日程一覧</small></h1>
<p class="up">{upd}</p>
<p class="lead">東京・神奈川・埼玉・千葉・茨城・栃木・群馬のイルミネーション{n}か所を、都県ごとに日程・場所・無料かどうかで並べました。開催中・これからは、ページを開いた日で切り替わります。終わった所は消えます。</p>
</header>
<nav class="tabs" aria-label="都県でしぼる">{tabs}</nav>
<main>{secs}<p class="none" hidden>この都県で、いま見られる物はありません。</p></main>
<footer class="foot">
<p>日程は各公式のお知らせで確かめた物です。名前を押すと公式のページ（無い所は市や観光協会のページ）、「地図」を押すと場所が開きます。「発表前」は2026年の日程がまだ出ていない所で、昨年の期間を書いています。時間や料金は変わることがあるので、行く前にリンク先で確かめてください。</p>
<p>「近くの宿をさがす」は楽天トラベルの広告リンクです。</p>
<a class="back" href="./">関東おでかけリストを見る</a>
<p class="sign">うさぎ│LIFE NOTES</p>
</footer>
</div>
<script>
(function(){{
  var d=new Date(),t=d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2);
  document.querySelectorAll('.it').forEach(function(li){{
    var s=li.dataset.s,e=li.dataset.e,b=li.querySelector('.st');
    if(e&&e<t){{li.remove();return}}
    if(s&&b){{if(s<=t){{b.className='st now';b.textContent='開催中'}}else{{b.className='st soon';b.textContent='これから'}}}}
  }});
  document.querySelectorAll('.ps').forEach(function(sec){{
    var n=sec.querySelectorAll('.it').length;sec.querySelector('.c').textContent=n+'件';if(!n)sec.remove();
  }});
  var bs=document.querySelectorAll('.tabs button'),none=document.querySelector('.none');
  function show(f){{
    var any=false;
    document.querySelectorAll('.ps').forEach(function(sec){{var on=!f||sec.dataset.p===f;sec.hidden=!on;if(on)any=true}});
    none.hidden=any;
    bs.forEach(function(b){{b.classList.toggle('on',b.dataset.f===f)}});
  }}
  bs.forEach(function(b){{
    if(b.dataset.f&&!document.querySelector('.ps[data-p="'+b.dataset.f+'"]'))b.remove();
    b.addEventListener('click',function(){{show(b.dataset.f);try{{localStorage.setItem('illumi-pref',b.dataset.f)}}catch(x){{}}}});
  }});
  try{{var k=localStorage.getItem('illumi-pref');if(k&&document.querySelector('.ps[data-p="'+k+'"]'))show(k)}}catch(x){{}}
}})();
</script>
</body></html>
"""

ROBOTS = f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n"


def sitemap(now):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f'  <url><loc>{SITE}/{PAGE}</loc><lastmod>{now:%Y-%m-%d}</lastmod><changefreq>daily</changefreq></url>\n'
            '</urlset>\n')


def main():
    now = datetime.now(JST)
    if "--now" in sys.argv:
        now = datetime.fromisoformat(sys.argv[sys.argv.index("--now") + 1]).replace(tzinfo=JST)
    today = now.date()
    d = json.load(open(os.path.join(ROOT, "data", "illumi.json"), encoding="utf-8"))
    # 終わった物は外す。開催中→これから→発表前の順、その中は終わる日・始まる日の近い順
    items = [e for e in d["items"] if not e.get("end") or date.fromisoformat(e["end"]) >= today]

    def key(e):
        if not e.get("start"):
            return (2, "")
        return (0, e["end"]) if date.fromisoformat(e["start"]) <= today else (1, e["start"])
    items.sort(key=key)
    site = os.path.join(ROOT, "site")
    os.makedirs(site, exist_ok=True)
    open(os.path.join(site, "illumination.html"), "w", encoding="utf-8").write(render(items, today, now))
    open(os.path.join(site, "robots.txt"), "w", encoding="utf-8").write(ROBOTS)
    open(os.path.join(site, "sitemap.xml"), "w", encoding="utf-8").write(sitemap(now))
    print(json.dumps({"illumi": len(items), "ended": len(d["items"]) - len(items)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
