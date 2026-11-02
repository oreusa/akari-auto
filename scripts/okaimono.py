"""くらべたおかいものリスト（site/okaimono.html = /okaimono）を、関東おでかけリスト（/odekake）から作る。
11/2 オーナー「買い物のほうはもっと真剣に工夫しろ。見やすく使いやすいの為に分けたんだろ」「TOWN NOTE こんなんじゃないだろ」
→ 月の関西不動産リスト（おでかけリストの派生）と同じ作り方：おでかけリストの見出し・件数・タブ・しぼりこみ・カード・下のボタン列を
  そのまま使い、中のカードだけを買い物に入れかえる。
  タブは4つ（比べて選ぶ：くらべた物・1個あたり ／ 安く買う：値下がり・セール）。しぼりこみは物の種類（水・お米・日用品…）。
  カードの中身は、それまでの係が作ったページ（index の比べた物・いち押し・宿、/tanka・/furusato・/nesage・/kaimawari）から読む。
scripts/lifenote.py が呼ぶ：build(odekake_html, index_html) → okaimono の html。
"""
import html, json, os, re, sys, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(R, "site")
E = html.escape
# 種類の色（都県の色と同じ明るさ。並んだ時に見分けやすい順）
PAL = ["#4F86C6", "#E09A3E", "#5FA06A", "#D2697E", "#3FA3B5", "#9C7BB8", "#D9775A", "#C4925A", "#6F8C68", "#7A8FB8", "#A08A5A", "#6E9F8C"]
FIX = {"いち押し": "#C2703F", "ふるさと納税": "#B5788A", "宿": "#5F9A9A", "お店のお得": "#8C7B6E", "楽天のセール": "#BF0000"}


def txt(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()


def rd(n):
    p = os.path.join(S, n)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


def block(h, start_re):
    """start_re で始まる要素を、入れ子を数えて丸ごと返す（全部）。"""
    out, pos = [], 0
    while True:
        m = re.compile(start_re).search(h, pos)
        if not m:
            return out
        tag = re.match(r"<(\w+)", m.group(0)).group(1)
        i, depth, op = m.end(), 1, re.compile(rf"<{tag}\b")
        while depth:
            j = h.find(f"</{tag}>", i)
            if j < 0:
                return out
            depth += len(op.findall(h, i, j)) - 1
            i = j + len(tag) + 3
        out.append(h[m.start():i])
        pos = i


def first(pat, s, default=""):
    m = re.search(pat, s, flags=re.S)
    return m.group(1) if m else default


# ---------- カードを集める（1枚 = dict(tab, cat, top, title, sub, href, pr, e)） ----------
def rate_of(a):
    return txt(first(r'<span class="sc">(.*?)</span>', a)).replace("｜", "・")


def from_index(ix):
    out = []
    names = dict(re.findall(r'<button data-c="(\w+)">([^<]+)<i>', ix))  # 比べた物の種類（stab）
    for a in block(ix, r'<article class="card cmp hot"'):
        out.append(dict(tab="pick", cat="いち押し", top="今日のうさぎのいち押し", title=txt(first(r'<div class="t">(.*?)</div>', a)),
                        sub=txt(first(r'<p class="why">(.*?)</p>', a)), href=html.unescape(first(r'<a class="buy" href="([^"]+)"', a)), pr=True, rate=rate_of(a)))
    for a in block(ix, r'<article data-c="\w+" class="card sh'):
        c = first(r'data-c="(\w+)"', a)
        when = txt(first(r'<span class="when">(.*?)</span>', a))
        out.append(dict(tab="pick", cat=names.get(c, "くらしの物"), top=when or "3つ以上を比べて選んだ物",
                        title=txt(first(r'<div class="t">(.*?)</div>', a)), sub=txt(first(r'<p class="why">(.*?)</p>', a)),
                        href=html.unescape(first(r'<a class="buy" href="([^"]+)"', a)), pr=True, rate=rate_of(a)))
    trip = (block(ix, r'<section class="blk" id="trip"') or [""])[0]
    for a in block(trip, r'<article class="card'):
        out.append(dict(tab="pick", cat="宿", top="口コミ1,000件以上・評価4.5以上の宿", title=txt(first(r'<div class="t">(.*?)</div>', a)),
                        sub=txt(first(r'<p class="why">(.*?)</p>', a)), href=html.unescape(first(r'<a class="buy" href="([^"]+)"', a)), pr=True,
                        rate=rate_of(a), img=html.unescape(first(r'<img class="ph" src="([^"]+)"', a))))
    deal = (block(ix, r'<section class="blk" id="deal"') or [""])[0]
    for a in block(deal, r'<div class="card it"'):
        out.append(dict(tab="sale", cat="お店のお得", top=txt(first(r'<span class="when">(.*?)</span>', a)),
                        title=txt(first(r'<div class="t">(.*?)</div>', a)), sub="公式ページで確かめたお得です",
                        href=html.unescape(first(r'<a class="go" href="([^"]+)"', a)), pr=False, e=first(r'data-e="([^"]+)"', a)))
    return [x for x in out if x["href"] and x["title"]]


def lis(page):
    """/tanka などの ps 欄（種類）ごとの li.it を読む。"""
    h = rd(page)
    out = []
    for sec in block(h, r'<section class="ps"'):
        cat = txt(first(r"<h2>(.*?)(?:<span|</h2>)", sec)).split("（")[0]
        for li in re.findall(r'<li class="it">(.*?)</li>', sec, flags=re.S):
            out.append((cat, li))
    return out


def li_card(cat, li, tab, src):
    href = html.unescape(first(r'<a class="cd" href="([^"]+)"', li))
    nm = txt(first(r'<span class="nm">(.*?)</span>', li))
    pu = txt(first(r'<span class="pu">(.*?)</span>', li))
    df = txt(first(r'<span class="df[^"]*">(.*?)</span>', li))
    mt = txt(first(r'<span class="mt">(.*?)</span>', li))
    price, _, rate = mt.partition("★")
    rate = ("★" + rate.strip()) if rate else ""
    return dict(tab=tab, cat=cat, top=pu or src, big=df, title=nm, sub=price.strip(), href=href, pr=True,
                rate=re.sub(r"\s+", "・", rate), img=html.unescape(first(r'<img src="([^"]+)"', li)))


# ---------- 写真（11/2 オーナー「写真もついてないし。俺だったらここで買わないかも」）
# 比べた物・いち押しのカードには写真がないので、楽天のAPIで商品（宿）の写真を取る。1度取った写真は data/okaimono_img.json に残す
IMGF = os.path.join(R, "data", "okaimono_img.json")


def real_url(href):
    m = re.search(r"[?&]pc=([^&]+)", href)
    return urllib.parse.unquote(m.group(1)) if m else href


def photos(cards):
    try:
        cache = json.load(open(IMGF, encoding="utf-8"))
    except Exception:
        cache = {}
    try:
        import lib
        lib.rakuten_env()
        api = True
    except Exception:
        api = False
    n = 0
    for c in cards:
        if c.get("img"):
            continue
        u = real_url(c["href"])
        if u in cache:
            c["img"] = cache[u]
            continue
        if not api or n >= 30:
            continue
        got = ""
        try:
            code = lib.item_code_from_url(u)
            hm = re.search(r"travel\.rakuten\.co\.jp/HOTEL/(\d+)", u)
            if code:
                r = lib.rakuten_item(code)
                got = r.get("image") or ""
            elif hm:
                r = lib.rakuten_travel_api(hm.group(1))
                got = (r.get("hotelImageUrl") or r.get("hotelThumbnailUrl") or "") if isinstance(r, dict) else ""
            n += 1
            time.sleep(1.1)
        except Exception as e:
            print("写真が取れない", u[:60], e)
        if got.startswith("https://"):
            cache[u] = got
            c["img"] = got
    try:
        os.makedirs(os.path.dirname(IMGF), exist_ok=True)
        json.dump(cache, open(IMGF, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    except Exception:
        pass
    print("おかいもの 写真", sum(1 for c in cards if c.get("img")), "/", len(cards), "（APIで新しく", n, "件）")


def collect(ix):
    cards = from_index(ix)
    for cat, li in lis("tanka.html"):
        if "Amazon" not in li:
            cards.append(li_card(cat, li, "unit", "1個あたり"))
    for cat, li in lis("furusato.html"):
        c = li_card("ふるさと納税", li, "unit", "寄付1万円あたり")
        c["top"] = cat + "・" + c["top"]
        cards.append(c)
    ns = rd("nesage.html")
    for li in re.findall(r'<li class="it">(.*?)</li>', first(r"^(.*?)(?:いつもより高い物|$)", ns), flags=re.S):
        cards.append(li_card(txt(first(r'<span class="ct">(.*?)</span>', li)) or "値下がり", li, "down", "値下がり"))
    for cat, li in lis("kaimawari.html"):
        c = li_card(cat, li, "sale", "1,000円ぽっきり")
        c["top"] = "買いまわりの1,000円ぽっきり（送料込み）"
        cards.append(c)
    cards = [c for c in cards if c["href"] and c["title"]]
    photos(cards)
    return cards


def card_html(c, col):
    pc = col.get(c["cat"], "#8C7B6E")
    rel = "sponsored noopener" if c["pr"] else "noopener"
    chips = f'<span class="p" data-p="{E(c["cat"])}">{E(c["cat"])}</span>' + ('<span class="f">PR</span>' if c["pr"] else '<span class="f">公式</span>')
    e = f' data-e="{E(c["e"])}"' if c.get("e") else ""
    u = real_url(c["href"])
    btn = "楽天トラベルで見る" if "travel.rakuten" in u else ("楽天で見る" if c["pr"] else "公式ページを見る")
    img = (f'<span class="kp"><img src="{E(c["img"])}" alt="" width="96" height="96" loading="lazy" decoding="async" '
           f'referrerpolicy="no-referrer" onerror="this.parentNode.classList.add(\'no\');this.remove()"></span>') if c.get("img") else ""
    top = E(c["top"])
    top = re.sub(r"([\d,.]+)(円|%)", r"<b>\1</b>\2", top)
    return (f'<div class="card it kc{"" if img else " noimg"}" data-pref="{E(c["cat"])}" data-free="0" data-wk="0"{e} style="--pc:{pc}">'
            f'<div class="v2c">{chips}</div><div class="kb">{img}<div class="kx">'
            f'<div class="v2d">{top}</div>'
            + (f'<div class="kbig">{E(c["big"])}</div>' if c.get("big") else "")
            + f'<div class="t"><a class="go" href="{E(c["href"])}" rel="{rel}" target="_blank" aria-label="{E(c["title"][:40])}を{btn[:-2]}で開く">'
            f'<span class="nwp">{E(c["title"])}</span></a></div>'
            + (f'<div class="ks">{E(c["sub"])}</div>' if c["sub"] else "")
            + '</div></div>'
            f'<div class="kf"><span class="kr">{E(c.get("rate") or "")}</span><span class="kbtn">{btn}<i>→</i></span></div>'
            '</div>')


TABS = [("pick", "COMPARED", "くらべた物", "/okaimono", ""),
        ("unit", "PER UNIT", "1個あたり", "/tanka", "1個あたり・ふるさと納税を、くわしく見る"),
        ("down", "PRICE DOWN", "値下がり", "/nesage", "値下がりの記録を、くわしく見る"),
        ("sale", "SALE", "セール", "/kaimawari", "買いまわりの1,000円ぽっきりを、ぜんぶ見る")]
NONE = {"down": "値段の記録が2日分たまると、本当に下がった物だけがここに出ます",
        "sale": "いまはセールの物がありません。大きなセールの前に出します"}


def build(od, ix):
    cards = collect(ix)
    cats = []
    for c in cards:
        if c["cat"] not in cats:
            cats.append(c["cat"])
    col, k = {}, 0
    for c in cats:
        if c in FIX:
            col[c] = FIX[c]
        else:
            while PAL[k % len(PAL)] in FIX.values():
                k += 1
            col[c] = PAL[k % len(PAL)]
            k += 1
    h = od
    # ---- 見出し
    h = re.sub(r'<h1 class="ttl">.*?</h1>', '<h1 class="ttl">くらべたおかいものリスト</h1>', h, count=1, flags=re.S)
    h = re.sub(r'<p class="sub">.*?</p>', '<p class="sub">うさぎが3つ以上を数字で比べて選んだ物と、<br>本当に安くなった物を、毎日のせています</p>', h, count=1, flags=re.S)
    h = re.sub(r'<div class="sea">.*?</div>', "", h, count=1, flags=re.S)
    # 上の3つの入口（いま行ける・地図・イルミ）と季節の輪はおでかけだけ → 外す（月の不動産リストと同じ：入口1行＋件数）
    h = re.sub(r'<script>document\.documentElement\.classList\.add\("top2"\)</script><link rel="stylesheet" href="/assets/top2\.css[^"]*">', "", h)
    h = re.sub(r'<script src="/assets/top2\.js[^"]*"></script>', "", h)
    h = re.sub(r'<script src="/townnotes/map\.js[^"]*"[^>]*></script>', "", h)
    h = re.sub(r'<svg class="yr".*?</svg>', "", h, count=1, flags=re.S)
    for a in block(h, r'<a class="ilk"'):
        h = h.replace(a, "")
    sale = (block(ix, r'<section class="sbox" id="sale"') or [""])[0]
    if sale:
        go = first(r'<a class="sb-go" href="([^"]+)"', sale)
        nm, wh = txt(first(r'<p class="sb-t">(.*?)</p>', sale)), txt(first(r'<p class="sb-w">(.*?)</p>', sale))
        top = (f'<a class="ilk" href="{go}" rel="sponsored noopener" target="_blank" data-k="上の入口｜セールのエントリー">{E(nm)}　エントリー<span>→</span></a>'
               f'<p class="ilks">{E(wh)}（楽天アフィリエイトの広告）</p>')
    else:
        top = '<a class="ilk" href="/furusato" data-k="上の入口｜ふるさと納税">ふるさと納税 寄付1万円あたりで比べた<span>→</span></a>'
    n = {t: sum(1 for c in cards if c["tab"] == t) for t, *_ in TABS}
    seen = 0
    for p in ("tanka.html", "furusato.html"):
        seen += sum(int(x.replace(",", "")) for x in re.findall(r"の(\d[\d,]*)件を見て", rd(p)))
    cnt = (f'<p class="cnt" data-v="odekake"><span>比べた物<b id="n-now">{n["pick"] + n["unit"]}</b>件</span>'
           + (f'<span>調べた商品<b>{seen:,}</b>件</span>' if seen else f'<span>値下がり<b>{n["down"]}</b>件</span>') + '</p>')
    flt = ('<nav class="flt" data-v="odekake" aria-label="しぼりこみ"><button class="on" data-p="">すべて</button>'
           + "".join(f'<button data-p="{E(c)}" style="--pc:{col[c]}">{E(c)}</button>' for c in cats) + "</nav>")
    first_t = next((t for t, *_ in TABS if n[t]), "pick")
    otab = ('<nav class="otab" aria-label="おかいもの" data-g1="比べて選ぶ" data-g2="安く買う">' + "".join(
        f'<button type="button" data-t="{t}"{" class=on" if t == first_t else ""}{"" if n[t] else " disabled"}><i>{en}</i>{jp}<small>{n[t]}件</small></button>'
        for t, en, jp, *_ in TABS) + "</nav>")
    panes = ""
    for t, en, jp, link, lt in TABS:
        cs = [card_html(c, col) for c in cards if c["tab"] == t]
        more = f'<button class="gm" type="button" data-l="もっと見る（あと">もっと見る（あと{len(cs) - 5}件）</button>' if len(cs) > 5 else ""
        deep = f'<a class="pdeep" href="{link}" data-k="タブの下｜{jp}">{lt}<span>→</span></a>' if lt else ""
        panes += (f'<div class="pane" data-t="{t}"{"" if t == first_t else " hidden"}>{"".join(cs)}{more}'
                  f'<p class="none">{NONE.get(t, "この種類の物は、これから増やしていきます")}</p>{deep}</div>')
    od_sec = (block(h, r'<section class="blk" id="odekake"') or [""])[0]
    h = h.replace(od_sec, f'<section class="blk" id="odekake" data-v="odekake">{otab}{panes}</section>')
    for r in (r'<nav class="flt"', r'<p class="cnt"', r'<section class="blk arch" id="archive"'):
        for b in block(h, r):
            h = h.replace(b, "", 1)
    h = h.replace('<section class="blk" id="odekake"', top + cnt + flt + '<section class="blk" id="odekake"', 1)
    # ---- 下の欄
    h = re.sub(r'<p class="tip">.*?</p>', "", h, flags=re.S)
    h = re.sub(r'<p class="pr-note">.*?</p>',
               '<p class="pr-note">このページには楽天アフィリエイトの広告（PR）があります。<br>値段は確かめた時のものです。買う前に、楽天のページで最新の値段を確かめてください。</p>',
               h, count=1, flags=re.S)
    h = h.replace('<a class="co" data-en="LISTING" href="https://ig.me/m/ai_usagichan1" rel="noopener">',
                  '<a class="co" data-en="RAKUTEN ROOM" href="https://room.rakuten.co.jp/ai_usagichan/items" rel="noopener">', 1)
    h = re.sub(r'(<a class="co" data-en="RAKUTEN ROOM"[^>]*>).*?</a>', r'\1楽天ROOM<span>うさぎが比べて選んだ物を、まとめて置いています</span></a>', h, count=1, flags=re.S)
    h = re.sub(r'<p class="ft">.*?</p>', '<p class="ft">LIFE NOTE│比べた物は、このページに毎日足していきます</p>', h, count=1, flags=re.S)
    h = re.sub(r'<a class="tnx" href="/okaimono".*?</a>', '<a class="tnx" href="/odekake" data-k="下の入口｜関東おでかけリスト"><small>関連サイト</small>'
               '<b>関東おでかけリスト<span>→</span></b><i>関東のイベント・新しいお店や施設を、公式ページつきで</i></a>', h, count=1, flags=re.S)
    css = ('<style>'
           '.ilks{text-align:center;font-size:11px;color:var(--sub);margin:-12px 0 16px}'
           # 買い物のカード：左に商品の写真、右に「1Lあたり○円」と名前、下に評価と「楽天で見る」
           '#odekake .card.it.kc{padding:14px 14px 14px 16px}'
           '#odekake .card.it.kc:after{content:none}'
           '#odekake .kc .kb{display:flex;gap:12px;align-items:flex-start;margin-top:8px}'
           '#odekake .kc .kp{flex:none;width:96px;height:96px;border-radius:8px;background:#fff;border:1px solid #ECECEC;overflow:hidden;display:flex;align-items:center;justify-content:center}'
           '#odekake .kc .kp img{width:100%;height:100%;object-fit:contain;display:block}'
           '#odekake .kc .kp.no{display:none}'
           '#odekake .kc .kx{flex:1;min-width:0}'
           '#odekake .kc .v2d{margin:0;font-family:"Zen Kaku Gothic New",sans-serif;font-size:12.5px;line-height:1.5;letter-spacing:.02em;color:color-mix(in srgb,var(--pc) 72%,#000);font-weight:700}'
           '#odekake .kc .v2d b{font-family:Jost,sans-serif;font-size:19px;font-weight:600;letter-spacing:0;margin:0 1px}'
           '#odekake .kc .kbig{display:inline-block;margin:4px 0 2px;padding:2px 8px;border-radius:99px;background:color-mix(in srgb,var(--pc) 12%,#fff);color:color-mix(in srgb,var(--pc) 70%,#000);font-size:11px;font-weight:700}'
           '#odekake .kc .t{margin:4px 0 0;font-size:14px;line-height:1.5;font-weight:700;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}'
           '#odekake .kc .ks{margin-top:4px;font-size:12px;line-height:1.55;color:var(--sub);display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}'
           '#odekake .kc .kf{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:12px;padding-top:10px;border-top:1px dashed #E4E4E4}'
           '#odekake .kc .kr{font-size:11.5px;color:var(--sub);min-width:0}'
           '#odekake .kc .kbtn{flex:none;display:inline-flex;align-items:center;gap:8px;padding:9px 16px;border-radius:99px;background:var(--pc);color:#fff;font-size:12.5px;font-weight:700;letter-spacing:.04em}'
           '#odekake .kc .kbtn i{font-style:normal;font-family:Jost,sans-serif}'
           '.pdeep{display:block;width:max-content;max-width:100%;margin:6px auto 4px;color:#231E1B;text-decoration:none;font:600 13px/1.5 var(--min);letter-spacing:.06em;border-bottom:1px solid #231E1B;padding-bottom:3px}'
           '.pdeep span{font-family:Jost;margin-left:8px;color:#9C8775}'
           '.flt[data-v=odekake]{flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none}.flt[data-v=odekake]::-webkit-scrollbar{display:none}'
           '.flt[data-v=odekake] button{flex:none}.flt button.hid{display:none}'
           'h1.ttl:not(:where(.tn *)){font-size:clamp(20px,6.2vw,30px);letter-spacing:.06em;white-space:nowrap}'
           '.flt[data-v=odekake]{justify-content:flex-start}.flt[data-v=odekake]:before,.flt[data-v=odekake]:after{content:"";flex:1 0 0}'
           '</style>')
    h = h.replace("</head>", css + "</head>", 1)
    # 種類のしぼりこみは、いま開いているタブにある種類だけ出す／押されたPRを数える／下のボタン列は買い物の4つ
    js = ('<script>(function(){'
          'function sync(){var on=document.querySelector(".otab button.on"),t=on?on.dataset.t:"pick",has={};'
          'document.querySelectorAll(\'#odekake .pane[data-t="\'+t+\'"] .card.it\').forEach(function(c){has[c.dataset.pref]=1;});'
          'document.querySelectorAll(".flt button[data-p]").forEach(function(b){if(b.dataset.p)b.classList.toggle("hid",!has[b.dataset.p]);});'
          'var cur=document.querySelector(".flt button.on");if(cur&&cur.dataset.p&&!has[cur.dataset.p]){var a=document.querySelector(\'.flt button[data-p=""]\');if(a)a.click();}}'
          'function en(){document.querySelectorAll(".otab button").forEach(function(b){if(document.querySelector(\'#odekake .pane[data-t="\'+b.dataset.t+\'"] .card.it\'))b.disabled=false;});}'
          'document.querySelectorAll(".otab button").forEach(function(b){b.addEventListener("click",function(){setTimeout(sync,0);});});'
          'document.querySelectorAll(".flt button[data-p]").forEach(function(b){b.addEventListener("click",function(){setTimeout(en,0);});});sync();'
          'var F="";try{F=sessionStorage.getItem("f")||"";}catch(e){}'
          'document.addEventListener("click",function(ev){var a=ev.target.closest&&ev.target.closest("a.go[rel~=sponsored],a.ilk[rel~=sponsored]");if(!a||!navigator.sendBeacon)return;'
          'var p=a.closest(".pane"),k=a.textContent.replace(/\\s+/g,"").slice(0,30);'
          'try{navigator.sendBeacon("/c?f="+encodeURIComponent(F||"direct")+"&s="+encodeURIComponent(("okai-"+(p?p.dataset.t:"top")).slice(0,16))+"&k="+encodeURIComponent(k));}catch(e){}},true);'
          'var q=null;try{q=new URLSearchParams(location.search).get("t");}catch(e){}var hs=location.hash.slice(1);if(!q&&hs)q={deal:"sale",sale:"sale",shop:"pick",trip:"pick",hot:"pick",unit:"unit",down:"down"}[hs]||null;if(q){var b=document.querySelector(\'.otab button[data-t="\'+q+\'"]\');if(b&&!b.disabled)b.click();}'
          '})();</script>')
    h = h.replace('<body class="', '<body data-bar="okai" class="', 1)
    i = h.rfind("</body>")
    return h[:i] + js + h[i:]
