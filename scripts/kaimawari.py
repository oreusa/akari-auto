"""楽天お買い物マラソンの「買いまわり 1,000円ぽっきり」ページ（site/kaimawari.html）を作る。

11/1 オーナー「いつになったら売上作るんだ」「こんな機能つけたら、他で見つけたこれは燈ならもっとこうして使える」。
10月は楽天クリック約400・成果0。買いまわりは「1店で1,000円以上を何店で買うか」でポイントが増えるので、
マラソン中は1,000円ちょうどの消耗品を探す人が多い（主婦のブログで定番の記事）。燈は楽天の検索で毎回
「1,000〜1,199円・送料込み・レビュー1,000件以上・★4.0以上」だけを集め、ジャンルごとに並べる。
日程は data/sales.json（夜の回が公式のお知らせで確かめて直す）。page.yml で毎回作り直す。
"""
import html
import json
import re
import os
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))
import lib  # noqa: E402

JST = timezone(timedelta(hours=9))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://usagi-life-notes.pages.dev"
PAGE = "kaimawari"
# 毎日なくなる物から（10/30 の学び：買われやすいのは消耗品）。楽天のジャンル番号
GENRES = [
    ("日用品", "215783"), ("食品", "100227"), ("水・飲み物", "100316"), ("キッチン", "558944"),
    ("美容・コスメ", "100939"), ("ベビー・キッズ", "100533"), ("ペット", "101213"),
]
PER = 6  # 1ジャンルに出す数
WEEK = "月火水木金土日"


def esc(s):
    return html.escape(str(s or ""), quote=True)


# 11/25 夜：BF が終わっても品名に「11/25 01:59まで」「先行セール中！」が残っていた → 日付つきの期限・セールの売り文句は品名から外す
_LIM = re.compile(r"[\d０-９]{1,2}[/／月][\d０-９]{1,2}日?(?:[（(][^）)]{1,3}[）)])?\s*(?:[\d０-９]{1,2}[:：][\d０-９]{2})?\s*(?:まで|迄)[^\s】]*"
                  r"|(?:先行)?セール中[！!]*|ブラックフライデー(?:限定|特価|セール)?|お買い物マラソン(?:限定|特価)?|期間限定[^\s】]*|ポイント\d+倍[^\s】]*")
def short(name, n=40):
    name = " ".join(_LIM.sub(" ", str(name)).replace("【", " ").replace("】", " ").split())
    return name if len(name) <= n else name[:n] + "…"


def fetch(genre, seen=None):
    """1,000〜1,199円・送料込み・販売中を、レビューの多い順に。条件に合う物だけ返す。"""
    items, err = lib._rakuten_search({"genreId": genre, "minPrice": 1000, "maxPrice": 1199, "postageFlag": 1,
                                      "availability": 1, "sort": "-reviewCount", "hits": 30})
    if not items:
        return [], err
    out = []
    seen = set() if seen is None else seen  # 11/9 夜#156：ジャンルをまたいで同じ店が出ていた → ページ全体で1店1つ
    for it in items:
        rc, av = int(it.get("reviewCount") or 0), float(it.get("reviewAverage") or 0)
        aff, shop = it.get("affiliateUrl") or "", it.get("shopCode") or ""
        if rc < 1000 or av < 4.0 or not aff.startswith("https://hb.afl.rakuten.co.jp/") or shop in seen:
            continue
        seen.add(shop)  # 同じ店が並ぶと買いまわりの店数が増えないので、1店1つ
        out.append({"name": short(it.get("itemName")), "price": int(it.get("itemPrice") or 0), "rc": rc, "av": av,
                    "shop": it.get("shopName") or "", "url": aff, "img": lib._item_image(it),
                    "plain": (it.get("itemUrl") or "").split("?")[0]})
        if len(out) >= PER:
            break
    return out, ""


def sale_now(now):
    d = lib.load_json(os.path.join(ROOT, "data", "sales.json"), {}) or {}
    for s in d.get("sales", []):
        end = datetime.fromisoformat(s["end"]).replace(tzinfo=JST)
        if end >= now:
            return s
    return None


def when(s):
    a = datetime.fromisoformat(s["start"])
    b = datetime.fromisoformat(s["end"])
    return f"{a.month}/{a.day}（{WEEK[a.weekday()]}）{a:%H:%M} 〜 {b.month}/{b.day}（{WEEK[b.weekday()]}）{b:%H:%M}"


def aff(u):
    """楽天のページへのリンクを、紹介の印つきに（ID が無い時はそのまま）。"""
    import urllib.parse
    aid = os.environ.get("RAKUTEN_AFFILIATE_ID")
    q = urllib.parse.quote(u, safe="")
    return f"https://hb.afl.rakuten.co.jp/hgc/{aid}/?pc={q}&m={q}" if aid else u


def md(iso):
    a = datetime.fromisoformat(iso)
    return f"{a.month}/{a.day}（{WEEK[a.weekday()]}）{a:%H:%M}"


def set10(groups):
    """11/17 月：10店で10倍。ジャンルを順に回って、別々のお店の物を10個えらぶ（ページの中の物だけ）。"""
    out, i = [], 0
    while len(out) < 10:
        added = False
        for g, v in groups:
            if i < len(v) and len(out) < 10:
                out.append((g, v[i]))
                added = True
        if not added:
            break
        i += 1
    return out


def plan(sale, groups):
    """買う前の段取り・10店の組み立て・よくある質問（数字は sales.json＝公式で確かめた物だけ）。"""
    if not sale:
        return "", ""
    st, en = sale["start"], sale["end"]
    ev = sale["name"]
    # 11/23 夜の見回り：11/19 21:59 に終わった「開始2時間のクーポン」が 11/23 も出ていた → 終わったクーポンは段取り・ボタン・質問から外す（ページの JS も時刻で消す）
    if sale.get("coupon_end"):
        try:
            if datetime.fromisoformat(sale["coupon_end"]).replace(tzinfo=JST) <= datetime.now(JST):
                sale = dict(sale); sale.pop("coupon_end", None); sale.pop("coupon_url", None)
        except Exception:
            pass
    steps = []
    es = sale.get("entry_start")
    steps.append(("エントリーする", (f"{md(es)}からできます。" if es else "") + "期間中にエントリーすれば、エントリー前の買い物も対象です。押し忘れがいちばん多い失敗です。"))
    if sale.get("coupon_end"):
        steps.append(("クーポンを先に取っておく", f"{esc(sale.get('coupon_name') or 'クーポン')}は、使えるのが<b>{md(st)}〜{md(sale['coupon_end'])}の2時間だけ</b>です。取れるのは始まる前から。条件や回数はお店ごとにちがいます。"))
    steps.append(("買う物をカートに入れておく", "1店で1,000円（税込・送料は入らない）以上が1店に数えられます。同じ店でいくつ買っても1店です。クーポンを使って999円以下になると数えられないので、1,000円ちょうどの物にクーポンを使う時は気をつけてください。下の10店の例やジャンルから選べます。"))
    steps.append(("始まったら買う", f"{md(st)}から{md(en)}まで。2店で2倍、10店で10倍（11店からも10倍）。買う順番は関係ありません。"))
    steps.append(("ポイントを待つ", f"買いまわりで増える分は上限7,000ポイント（期間限定）。" + (f"もらえるのは{esc(sale['points_day'])}です。" if sale.get("points_day") else "")))
    li = "".join(f'<li><b>{i}. {t}</b><span>{d}</span></li>' for i, (t, d) in enumerate(steps, 1))
    links = f'<a class="entry nofilt" href="{esc(aff(sale.get("url") or ""))}" rel="sponsored noopener" target="_blank" data-k="エントリー2">楽天でエントリーする →</a>'
    if sale.get("coupon_url"):
        links += f'<a class="cpn nofilt" href="{esc(aff(sale["coupon_url"]))}" rel="sponsored noopener" target="_blank" data-k="クーポン">開始2時間のクーポンを取る →</a>'
    box = f'<section class="pl"><h2>{esc(ev)}の回り方</h2><ol>{li}</ol>{links}</section>'
    s10 = set10(groups)
    if len(s10) >= 2:
        tot = sum(e["price"] for _, e in s10)
        n = len(s10)
        pt = min(7000, tot * (n - 1) // 100)
        rows = "".join(f'<li><a class="r" href="{esc(e["url"])}" rel="sponsored noopener" target="_blank" data-k="10店｜{esc(e["name"][:24])}"><i>{k}</i><span>{esc(e["name"])}<small>{esc(g)}・{esc(e["shop"])}</small></span><b>{e["price"]:,}円</b></a></li>'
                       for k, (g, e) in enumerate(s10, 1))
        box += (f'<section class="pl s10"><h2>{n}店で{n}倍にする例</h2><p class="sm">下のジャンルから、別々のお店の物を{n}個えらびました。毎日なくなる物だけです。</p><ol>{rows}</ol>'
                f'<p class="tot">合計 <b>{tot:,}円</b>（送料込み） → 買いまわりで増える分 <b>{pt:,}</b>ポイントの目安</p>'
                '<p class="sm">ポイントは通常の1倍とほかのキャンペーンを入れない目安です。値段は変わることがあります。</p></section>')
    faq = [
        (f"{ev}はいつ？", f"{when(sale)}です（楽天の公式ページより）。"),
        ("エントリーは必要？", "必要です。" + (f"{md(es)}から" if es else "") + "期間中にエントリーすれば、エントリー前の買い物も対象になります。"),
        ("何店で何倍？", "1店で1,000円（税込）以上買ったお店の数で、2店で2倍、10店で10倍です。11店以上も10倍です。"),
        ("ポイントの上限は？", "買いまわりで増える分は7,000ポイントまで（期間限定ポイント）です。"),
    ]
    if sale.get("coupon_end"):
        faq.append(("最大50%OFFのクーポンはいつ使える？", f"{md(st)}〜{md(sale['coupon_end'])}の2時間だけです。対象のお店だけで、条件はお店ごとにちがいます。"))
    fq = "".join(f'<details><summary>{esc(q)}</summary><p>{a}</p></details>' for q, a in faq)
    box += f'<section class="pl fq"><h2>よくある質問</h2>{fq}<p class="sm">{esc(sale.get("checked","").replace("-","/")[5:])} に楽天の公式ページで確かめました。条件は必ず公式ページでも確かめてください。</p></section>'
    import re as _re
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": _re.sub(r"<[^>]+>", "", a)}} for q, a in faq]}
    return box, '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>"


def card(e):
    img = f'<img src="{esc(e["img"])}" alt="" width="84" height="84" loading="lazy" onerror="this.remove()">' if e["img"] else ""
    return (f'<li class="it"><a class="cd" href="{esc(e["url"])}" rel="sponsored noopener" target="_blank" data-k="{esc(e["name"][:30])}">'
            f'{img}<span class="tx"><span class="nm">{esc(e["name"])}</span>'
            f'<span class="mt"><b>{e["price"]:,}円</b>（送料込み）　★{e["av"]:.2f}　レビュー{e["rc"]:,}件</span>'
            f'<span class="sh">{esc(e["shop"])}</span><span class="go">楽天で見る →</span></span></a></li>')


def render(groups, now, sale):
    upd = f"{now.month}/{now.day}（{WEEK[now.weekday()]}）{now:%H:%M} 楽天で確かめた値段"
    if sale:
        head = (f'<p class="sale"><b>{esc(sale["name"])}</b><br>{when(sale)}'
                f'<span class="st" id="st" data-s="{esc(sale["start"])}" data-e="{esc(sale["end"])}" data-c="{esc(sale.get("coupon_end") or "")}"></span></p>')
        # 11/1 月：買う前に要るエントリーの入口（楽天は押してから24時間の買い物が紹介料の対象）
        import urllib.parse
        aid = os.environ.get("RAKUTEN_AFFILIATE_ID")
        mu = sale.get("url") or "https://event.rakuten.co.jp/campaign/point-up/marathon/"
        eu = f"https://hb.afl.rakuten.co.jp/hgc/{aid}/?pc={urllib.parse.quote(mu, safe='')}&m={urllib.parse.quote(mu, safe='')}" if aid else mu
        head += (f'<a class="entry nofilt" href="{esc(eu)}" rel="sponsored noopener" target="_blank" data-k="エントリー">楽天でエントリーする →</a>'
                 '<p class="note">エントリーを忘れずに（期間中にエントリーすれば、エントリー前の買い物も対象です）</p>')
        # 11/11 sales.json の note は中の人のメモ（名前や段取りが入る）。お客さんのページには出さない。予定の時だけ決まった1行を出す
        if sale.get("note"):
            head += '<p class="note">日程は予定です。始まる前に、楽天の公式ページでお確かめください。</p>'
    else:
        head = '<p class="sale">次のお買い物マラソンの日程が出たら、ここに書きます。</p>'
    n = sum(len(v) for _, v in groups)
    pbox, pld = plan(sale, groups)
    tabs = "".join(f'<button type="button" data-f="{esc(g)}">{esc(g)}</button>' for g, v in groups if v)
    secs = "".join(f'<section class="ps" data-p="{esc(g)}"><h2>{esc(g)}<span class="c">{len(v)}件</span></h2><ul>{"".join(card(e) for e in v)}</ul></section>'
                   for g, v in groups if v)
    ev = sale["name"].replace("楽天", "") if sale else "お買い物マラソン"  # 11/17 月：ブラックフライデーも同じ買いまわり（公式で確かめた）。題をその時のセールの名前に
    title = f"楽天{ev} 買いまわり 1,000円ぽっきり（送料込み）まとめ｜うさぎ│LIFE NOTES"
    desc = f"楽天{ev}の買いまわり用に、1,000〜1,199円・送料込み・レビュー1,000件以上・評価4.0以上の物だけを、ジャンルごとに集めました。ポイントの計算つき。"
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}/{PAGE}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}/og-v10.png"><meta property="og:url" content="{SITE}/{PAGE}"><meta name="twitter:card" content="summary">
{pld}<link rel="icon" href="logo.png"><link rel="apple-touch-icon" href="logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=Jost:wght@300;400&display=swap">
<style>.entry{{display:block;background:#BF0000;color:#fff;text-align:center;text-decoration:none;font-weight:700;font-size:15px;letter-spacing:.06em;padding:14px 10px;border-radius:6px;margin:12px 0 4px}}
:root{{color-scheme:light;--bg:#FFFFFF;--ink:#2B2622;--sub:#6B6058;--mute:#8C7B6E;--line:#DDDDDD;--line2:#CECECE;--brown:#A07E66;--red:#B5643F;
  --min:"Shippori Mincho","Hiragino Mincho ProN","Yu Mincho",serif;--go:"Zen Kaku Gothic New","Hiragino Sans","Noto Sans JP",sans-serif;--en:"Jost","Futura","Avenir Next",sans-serif}}
*{{box-sizing:border-box}}html{{-webkit-text-size-adjust:100%}}
body{{margin:0;background:var(--bg);color:var(--ink);font:400 14px/1.7 var(--go)}}a{{color:inherit;text-decoration:none}}
.wrap{{max-width:460px;margin:0 auto;padding:0 16px 48px}}
.head{{text-align:center;padding:40px 0 8px}}.head img{{width:64px;height:64px;display:block;margin:0 auto;border-radius:50%;background:#fff}}
.en{{font:300 10px/1 var(--en);letter-spacing:.5em;color:var(--brown);margin:16px 0 0;padding-left:.5em}}
h1{{font:600 21px/1.5 var(--min);letter-spacing:.08em;font-feature-settings:"palt";margin:14px 0 6px}}
h1 small{{display:block;font-size:14px;letter-spacing:.16em;margin-top:4px}}
.up{{font-size:11.5px;color:var(--mute);margin:0}}
.sale{{background:#fff;border:1px solid var(--line);border-radius:4px;padding:12px 14px;margin:18px 0 0;font-size:13px;line-height:1.8;text-align:center}}
.note{{font-size:11.5px;color:var(--mute);margin:6px 0 0;text-align:center}}
.lead{{font-size:12.5px;line-height:1.95;color:var(--sub);margin:14px 0 0;text-align:left}}
.calc{{background:#fff;border:1px solid var(--line);border-radius:4px;padding:14px;margin:18px 0 0}}
.calc h2{{font:600 15px/1.4 var(--min);letter-spacing:.1em;margin:0 0 10px}}
.calc label{{display:flex;justify-content:space-between;align-items:center;font-size:13px;margin:6px 0}}
.calc input{{width:110px;font:500 15px/1 var(--go);padding:8px;border:1px solid var(--line2);border-radius:3px;text-align:right}}
.calc .res{{font-size:13.5px;margin:10px 0 0;line-height:1.8}}.calc .res b{{font-size:18px;color:var(--red)}}
.calc .sm{{font-size:11px;color:var(--mute);margin:6px 0 0}}
.tabs{{display:flex;gap:6px;overflow-x:auto;margin:22px -2px 6px;padding:2px;scrollbar-width:none;position:sticky;top:0;background:var(--bg);z-index:2}}
.tabs::-webkit-scrollbar{{display:none}}
.tabs button{{flex:none;font:700 12.5px/1 var(--go);letter-spacing:.06em;color:var(--mute);background:#fff;border:1px solid #CFCFCF;border-radius:99px;padding:10px 14px;cursor:pointer}}
.tabs button.on{{background:var(--ink);border-color:var(--ink);color:#fff}}
.ps h2{{display:flex;align-items:baseline;gap:8px;font:600 17px/1.4 var(--min);letter-spacing:.12em;margin:26px 0 10px;padding-bottom:8px;border-bottom:1px solid var(--line2)}}
.ps h2 .c{{font:400 12px/1 var(--go);color:var(--mute)}}
ul{{list-style:none;margin:0;padding:0}}.it{{margin:0 0 10px}}
.cd{{display:flex;gap:12px;background:#fff;border:1px solid var(--line);border-radius:4px;padding:12px}}
.cd img{{flex:none;width:84px;height:84px;object-fit:contain;border-radius:3px;background:#fff}}
.tx{{display:flex;flex-direction:column;gap:3px;min-width:0}}
.nm{{font:600 13.5px/1.55 var(--go)}}.mt{{font-size:12px;color:var(--sub)}}.mt b{{font-size:14px;color:var(--ink)}}
.sh{{font-size:11px;color:var(--mute)}}.go{{font-size:12px;color:var(--brown);margin-top:2px}}
.st{{display:block;font-weight:700;color:var(--red);margin-top:4px}}
.pl{{background:#fff;border:1px solid var(--line);border-radius:4px;padding:14px;margin:18px 0 0}}
.pl h2{{font:600 15px/1.4 var(--min);letter-spacing:.1em;margin:0 0 10px}}
.pl ol{{list-style:none;margin:0;padding:0}}.pl li{{margin:0 0 10px;font-size:12.5px;line-height:1.8;color:var(--sub)}}
.pl li>b{{display:block;font-size:13.5px;color:var(--ink)}}.pl li span b{{color:var(--red)}}
.cpn{{display:block;text-align:center;font-weight:700;font-size:14px;letter-spacing:.04em;padding:12px 10px;border-radius:6px;margin:8px 0 0;border:1.5px solid #BF0000;color:#BF0000;background:#fff}}
.s10 li{{margin:0;border-top:1px solid var(--line)}}.s10 .r{{display:flex;gap:10px;align-items:center;padding:9px 0}}
.s10 .r i{{flex:none;width:22px;height:22px;border-radius:50%;background:var(--ink);color:#fff;font:700 11px/22px var(--go);text-align:center;font-style:normal}}
.s10 .r span{{flex:1;min-width:0;font-size:12.5px;line-height:1.5;color:var(--ink)}}.s10 .r small{{display:block;font-size:10.5px;color:var(--mute)}}
.s10 .r>b{{flex:none;font-size:13px}}.tot{{font-size:13px;margin:10px 0 0;border-top:1px solid var(--line2);padding-top:10px}}.tot b{{color:var(--red);font-size:16px}}
.pl .sm{{font-size:11px;color:var(--mute);margin:6px 0 0}}
.fq details{{border-top:1px solid var(--line);padding:10px 0}}.fq summary{{font-weight:700;font-size:13px;cursor:pointer}}.fq details p{{font-size:12.5px;color:var(--sub);margin:6px 0 0}}
.foot{{font-size:11.5px;line-height:1.9;color:var(--sub);border-top:1px solid var(--line2);margin-top:32px;padding-top:16px}}
.back{{display:block;text-align:center;font:700 13px/1 var(--go);letter-spacing:.1em;border:1px solid var(--ink);border-radius:2px;padding:14px;margin:20px 0 0;background:#fff}}
.sign{{text-align:center;font:400 11px/1 var(--en);letter-spacing:.3em;color:var(--brown);margin:24px 0 0}}
</style><script src="/assets/night.js?v=14"></script><script src="/assets/menu.js?v=46" defer></script><link rel="stylesheet" href="/assets/sub.css?v=4"><script src="/assets/v2sub.js?v=11" defer></script></head>
<body><div class="wrap">
<header class="head"><img src="logo-s.png" alt="うさぎ│LIFE NOTES のロゴ" width="64" height="64">
<p class="en">KAIMAWARI</p>
<h1>買いまわりの1,000円ぽっきり<small>楽天{esc(ev)}</small></h1>
<p class="up">{esc(upd)}</p>
{head}
<p class="lead">{esc(ev)}は、1店で1,000円以上の買い物をしたお店の数だけ、ポイントが上がります（最大10倍）。あと1店を足したい時のために、1,000〜1,199円で送料込み、レビュー1,000件以上・評価4.0以上の物だけを、楽天で確かめて{n}件集めました。同じお店は1つだけにしています。</p>
</header>
{pbox}
<div class="calc"><h2>ポイントの計算</h2>
<label>買ったお店の数<input id="kn" type="number" inputmode="numeric" min="1" max="10" value="5"></label>
<label>買い物の合計（円）<input id="ky" type="number" inputmode="numeric" min="0" step="100" value="10000"></label>
<p class="res" id="kr"></p>
<p class="sm">買いまわりで増える分だけの目安です（通常の1倍とほかのキャンペーンは入っていません）。上限は7,000ポイント。正しい条件は楽天のキャンペーンページで確かめてください。</p></div>
<nav class="tabs" aria-label="ジャンル"><button type="button" data-f="" class="on">すべて</button>{tabs}</nav>
<main>{secs}</main>
<footer class="foot">
<p>値段・送料・レビューは、このページを作った時に楽天で確かめた物です。変わることがあるので、買う前にリンク先で確かめてください。</p>
<p>このページのリンクは楽天アフィリエイトの広告（PR）です。</p>
<a class="back" href="./">関東おでかけリストを見る</a>
<p class="sign">うさぎ│LIFE NOTES</p>
</footer></div>
<script>
(function(){{
  var n=document.getElementById('kn'),y=document.getElementById('ky'),r=document.getElementById('kr');
  function calc(){{var s0=parseInt(n.value||'1',10),m0=parseInt(y.value||'0',10),s=Math.max(1,Math.min(10,s0||1)),m=Math.max(0,m0||0),nt='';
    /* 11/6 夜「11店・0店・マイナスを黙って直す」→ 直した時は、なぜかを書く */
    if(s0>10)nt='お店の数は10店までで計算します（買いまわりは10倍まで）。';else if(!(s0>=1))nt='お店の数は1〜10で入れてください（1店で計算しています）。';
    if(m0<0)nt+='金額はマイナスにできないので、0円で計算しています。';
    var p=Math.min(7000,Math.floor(m*(s-1)/100));
    r.innerHTML=s+'店で、買いまわりの分は <b>'+p.toLocaleString()+'</b> ポイント'+(s<10?'<br>あと1店（1,000円）足すと、+'+Math.min(7000-p,Math.floor((m+1000)*s/100)-p).toLocaleString()+'ポイント':'')+(nt?'<br><small style="color:#A8432F">'+nt+'</small>':'');}}
  var st=document.getElementById('st');
  if(st){{var S=new Date(st.dataset.s+':00+09:00'),E=new Date(st.dataset.e+':00+09:00'),C=st.dataset.c?new Date(st.dataset.c+':00+09:00'):null;
    function lf(ms){{var m=Math.max(0,Math.floor(ms/6e4)),d=Math.floor(m/1440),h=Math.floor(m%1440/60),mi=m%60;return (d?d+'日':'')+(d||h?h+'時間':'')+(d?'':mi+'分');}}
    function tick(){{var t=new Date(),x='';
      if(t<S)x='始まるまで あと'+lf(S-t)+'（先にエントリーとクーポン）';
      else if(C&&t<=C)x='開催中・最大50%OFFクーポンは あと'+lf(C-t);
      else if(t<=E)x='開催中・終わりまで あと'+lf(E-t);
      else x='終わりました';
      st.textContent=x;
      /* 11/25 夜：終わったあとも「楽天でエントリーする」と段取りが残っていた（ページを作り直すまで）→ 終わったら見た人の画面で外す */
      if(t>E&&!st.dataset.done){{st.dataset.done=1;
        document.querySelectorAll('a.entry,.pl,.kpl').forEach(function(el){{el.hidden=true;el.style.display='none'}});
        var sp=st.closest('.sale,.kms');if(sp){{sp.innerHTML='<b>'+(sp.querySelector('b')||{{textContent:''}}).textContent+'は終わりました</b><br>次の楽天のセールの日程が出たら、ここに書きます。下の物は、ふだんの日も1,000円ぽっきり（送料込み）で買えます。'}}
        var sc=sp&&sp.parentNode;if(sc)sc.querySelectorAll('.note,.dhint').forEach(function(el){{el.hidden=true;el.style.display='none'}});}}}}
    tick();setInterval(tick,30000);}}
  n.addEventListener('input',calc);y.addEventListener('input',calc);calc();
  var bs=document.querySelectorAll('.tabs button');
  bs.forEach(function(b){{b.addEventListener('click',function(){{var f=b.dataset.f;
    document.querySelectorAll('.ps').forEach(function(s){{s.hidden=!!f&&s.dataset.p!==f}});
    bs.forEach(function(x){{x.classList.toggle('on',x===b)}});}})}});
  document.querySelectorAll('.cd,.s10 .r,.cpn,.pl .entry').forEach(function(a){{a.addEventListener('click',function(){{
    try{{navigator.sendBeacon("/c?f=kaimawari&s=kaimawari&k="+encodeURIComponent(a.dataset.k||''))}}catch(e){{}}}})}});
}})();
</script></body></html>
"""


def main():
    now = datetime.now(JST)
    groups, errs, seen = [], [], set()
    for g, gid in GENRES:
        try:
            items, err = fetch(gid, seen)
        except Exception as e:  # 楽天につながらない時は、そのジャンルを出さない
            items, err = [], str(e)[:80]
        if err:
            errs.append(f"{g}: {err[:80]}")
        groups.append((g, items))
        time.sleep(1.1)  # 楽天APIは1秒に1回まで
    n = sum(len(v) for _, v in groups)
    if n < 6:  # 少なすぎる時は前のページを残す（空のページを出さない）
        print(json.dumps({"kaimawari": n, "skip": True, "errs": errs}, ensure_ascii=False))
        return
    site = os.path.join(ROOT, "site")
    os.makedirs(site, exist_ok=True)
    open(os.path.join(site, f"{PAGE}.html"), "w", encoding="utf-8").write(render(groups, now, sale_now(now)))
    # 11/17 月：ROOM の台本（room_auto.py）がセールの間に「買いまわりのあと1店」として先頭近くに使う
    lib.save_json(os.path.join(ROOT, "data", "kaimawari.json"), {"date": now.date().isoformat(), "sale": (sale_now(now) or {}).get("name", ""),
                  "items": [dict(e, genre=g) for g, v in groups for e in v if e.get("plain", "").startswith("https://item.rakuten.co.jp/")]})
    print(json.dumps({"kaimawari": n, "by": {g: len(v) for g, v in groups}, "errs": errs}, ensure_ascii=False))


if __name__ == "__main__":
    main()
