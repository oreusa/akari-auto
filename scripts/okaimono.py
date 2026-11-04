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
                        sub=txt(first(r'<p class="why">(.*?)</p>', a)), href=html.unescape(first(r'<a class="buy" href="([^"]+)"', a)), pr=True, rate=rate_of(a), but=txt(first(r'<p class="why but">(.*?)</p>', a))))
    for a in block(ix, r'<article data-c="\w+" class="card sh'):
        c = first(r'data-c="(\w+)"', a)
        when = txt(first(r'<span class="when">(.*?)</span>', a))
        out.append(dict(tab="pick", cat=names.get(c, "くらしの物"), top=when or "3つ以上を比べて選んだ物",
                        title=txt(first(r'<div class="t">(.*?)</div>', a)), sub=txt(first(r'<p class="why">(.*?)</p>', a)),
                        href=html.unescape(first(r'<a class="buy" href="([^"]+)"', a)), pr=True, rate=rate_of(a), but=txt(first(r'<p class="why but">(.*?)</p>', a))))
    trip = (block(ix, r'<section class="blk" id="trip"') or [""])[0]
    for a in block(trip, r'<article class="card'):
        out.append(dict(tab="pick", cat="宿", top="口コミ1,000件以上・評価4.5以上の宿", title=txt(first(r'<div class="t">(.*?)</div>', a)),
                        sub=txt(first(r'<p class="why">(.*?)</p>', a)), href=html.unescape(first(r'<a class="buy" href="([^"]+)"', a)), pr=True,
                        rate=rate_of(a), but=txt(first(r'<p class="why but">(.*?)</p>', a)), img=html.unescape(first(r'<img class="ph" src="([^"]+)"', a))))
    deal = (block(ix, r'<section class="blk" id="deal"') or [""])[0]
    for a in block(deal, r'<div class="card it"'):
        out.append(dict(tab="sale", kind="deal", cat="お店のお得", top=txt(first(r'<span class="when">(.*?)</span>', a)),
                        title=txt(first(r'<div class="t">(.*?)</div>', a)), sub="",
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
    pm = re.search(r"平均より\s*(\d+)%\s*安い", df)
    return dict(tab=tab, cat=cat, top=pu or src, big=df, title=nm, sub=price.strip(), href=href, pr=True,
                bd=html.unescape(first(r'data-bd="([^"]*)"', li)),
                rk=first(r'<span class="rk">(\d+)</span>', li), pct=int(pm.group(1)) if pm else 0,
                rate=re.sub(r"\s+", "・", rate), img=html.unescape(first(r'<img[^>]*? src="([^"]+)"', li)))


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
        u = real_url(c["href"])
        # 11/2 比べた物のカードは見出しが「〇〇3つ、…」なので、Amazon・Yahoo! で探すための本当の商品名も取る
        want_nm = c["tab"] == "pick" and "travel.rakuten" not in u
        if not c.get("img") and u in cache:
            c["img"] = cache[u]
        if want_nm and ("n:" + u) in cache:
            c["nm"] = cache["n:" + u]
        if (c.get("img") or u in cache) and (not want_nm or c.get("nm")):
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
                # 11/3 商品ページの名前（mf-003 など）と楽天の番号が違う物は、見出しの言葉でお店の中を探し直す
                if not got:
                    kw = re.split(r"[|｜、,，0-9０-９（(]", re.sub(r"^楽天ふるさと納税の", "", c["title"]))[0].strip()
                    for k in [kw, kw[:2]]:
                        if len(k) < 2:
                            continue
                        time.sleep(1.1)
                        r2 = lib.rakuten_item(code, keyword=k)
                        if r2.get("image"):
                            r, got = r2, r2["image"]
                            break
                if not got:
                    print("写真なし", u[:70], (r.get("why") or "")[:80], list(r)[:6])
                if r.get("name"):
                    cache["n:" + u] = c["nm"] = r["name"]
            elif hm:
                r = lib.rakuten_travel_api(hm.group(1))
                got = (r.get("hotelImageUrl") or r.get("hotelThumbnailUrl") or "") if isinstance(r, dict) else ""
            n += 1
            time.sleep(1.1)
        except Exception as e:
            print("写真が取れない", u[:60], e)
        if got.startswith("https://") and not c.get("img"):
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
    # 11/3 楽天とYahoo!を同じ種類の中で1個あたりの安い順に並べ直し、順位も付け直す（Yahoo!が下にまとまって写真も順位も無かった）
    grp = {}
    for cat, li in lis("tanka.html"):
        if "Amazon" not in li:
            grp.setdefault(cat, []).append(li_card(cat, li, "unit", "1個あたり"))
    for cat, cs in grp.items():
        def per(c):
            m = last_num(c["top"])
            try:
                return float(m[1].replace(",", "")) if m else 9e9
            except ValueError:
                return 9e9
        # 11/4 奥さんの感想「知らないメーカーが上位だと買う気にならない」→ 名の知れたメーカー（/tanka の data-bd）を先に
        cs.sort(key=lambda c: (not c.get("bd"), per(c)))
        for j, c in enumerate(cs, 1):
            c["rk"] = str(j)
        cards.extend(cs)
    for cat, li in lis("furusato.html"):
        c = li_card("ふるさと納税", li, "unit", "寄付1万円あたり")
        c["top"] = cat + "・" + c["top"]
        cards.append(c)
    ns = rd("nesage.html")
    for li in re.findall(r'<li class="it">(.*?)</li>', first(r"^(.*?)(?:いつもより高い物|$)", ns), flags=re.S):
        cards.append(li_card(txt(first(r'<span class="ct">(.*?)</span>', li)) or "値下がり", li, "down", "値下がり"))
    for cat, li in lis("kaimawari.html"):
        c = li_card(cat, li, "sale", "1,000円ぽっきり")
        c["top"] = "1,000円ぽっきり（送料込み）"
        cards.append(c)
    cards = [c for c in cards if c["href"] and c["title"]]
    # 11/3 同じ物が2回出ていた（ふるさと納税のトイレットペーパー）→ 同じタブ・見出し・リンクは1つに
    seen, uniq = set(), []
    for c in cards:
        k = (c["tab"], c["title"], c["href"])
        if k not in seen:
            seen.add(k)
            uniq.append(c)
    cards = uniq
    # 11/3 種類の点検：商品名と種類が合わない物（日用品の言葉なのに食べ物など）は直して、ログに残す
    try:
        from page import LIFE_WORDS
    except Exception:
        LIFE_WORDS = ("トイレットペーパー", "ティッシュ", "洗剤", "柔軟剤", "シャンプー", "マスク", "ゴミ袋", "おむつ")
    for c in cards:
        if c["tab"] == "pick" and c["cat"] in ("食べ物", "食べ物・飲み物") and any(w in c["title"] for w in LIFE_WORDS):
            print("種類を直した", c["cat"], "→ 日用品：", c["title"][:40])
            c["cat"] = "日用品"
    photos(cards)
    return cards


def last_num(t):
    """「1Lあたり 75.6円」→ ("1Lあたり", "75.6", "円")。いちばん後ろの数字が主役。"""
    ms = list(re.finditer(r"([\d,.]+)(円|kg|g|L|ロール|m|個|本)", t))
    if not ms:
        return None
    m = ms[-1]
    return t[:m.start()].strip(), m.group(1), m.group(2)


# 11/2 もしもアフィリエイト（Yahoo!ショッピング・審査なしで提携済み）。同じ品を Yahoo! でも探せるボタン。
# a_id はオーナーの もしも の「LIFE NOTE」用の番号（公開リンクに出る物なので秘密ではない）。Amazon は審査が通ったら足す。
COPY = "買う前に、AIに聞いてみる。"  # 11/3 ページ一番上の一言（オーナーが選ぶ）
MOSHIMO_YAHOO = "https://af.moshimo.com/af/c/click?a_id=5877817&p_id=1225&pc_id=1925&pl_id=18502&url="


def shop_q(title):
    """商品名から検索の言葉を作る（【】や（）の中の宣伝文句を外して、前の方の言葉だけ）"""
    t = re.sub(r"[【\[（(＜<《].*?[】\]）)＞>》]", " ", title)
    t = re.sub(r"(送料無料|ポイント\d+倍|楽天\S*|あす楽|クーポン\S*|最大\S*%\S*|\d+%OFF|公式|SALE|セール)", " ", t, flags=re.I)
    w = [x for x in re.split(r"[\s　/／・,、|｜]+", t) if x][:4]
    return " ".join(w)[:40] or title[:30]


def yahoo_url(title):
    from urllib.parse import quote
    return MOSHIMO_YAHOO + quote("https://shopping.yahoo.co.jp/search?p=" + quote(shop_q(title)), safe="")


# 11/2 オーナー「Amazonは元々登録してる」→ アソシエイトに直接（lib.AMAZON_TAG）。商品名で探した結果へ
def amazon_url(title):
    from urllib.parse import quote
    import lib
    return f"https://www.amazon.co.jp/s?k={quote(shop_q(title))}&tag={lib.AMAZON_TAG}"


def others(c, shop):
    """楽天の品だけ、同じ品を Amazon と Yahoo! でも探せる小さな文字リンク"""
    if shop != "楽天":
        return ""
    # 1個あたり・値下がりのカードは商品名そのもの。比べた物は API で取った商品名（無ければ付けない）
    name = c.get("nm") or ("" if c["tab"] == "pick" else c["title"])
    if not name:
        return ""
    return ('<span class="kot">'
            f'<a class="kyh" href="{E(amazon_url(name))}" rel="sponsored noopener" target="_blank">Amazon<i>›</i></a>'
            f'<a class="kyh" href="{E(yahoo_url(name))}" rel="sponsored noopener" target="_blank">Yahoo!<i>›</i></a></span>')


def card_html(c, col, i=0):
    """11/2 100サイトを見て作り直し（mybest・価格.com・LOHACO・Wirecutter・Baymard・北欧暮らしの道具店 ほか）。
    数字で選ぶ物（1個あたり・値下がり・セール）は横長の1行カード：左に写真の台、右に「1Lあたり○円」を主役、平均との差、送料込みの値段、★と件数。
    比べて選んだ物は大きな写真のカード：見出し・選んだ理由・「ただし」（正直な弱み）・評価。
    PRの札はカードに付けず、ページの上に1行（mybest と同じ。11/2 オーナー「PRっぽくない方が読まれる」）。"""
    pc = col.get(c["cat"], "#8C7B6E")
    rel = "sponsored noopener" if c["pr"] else "noopener"
    e = f' data-e="{E(c["e"])}"' if c.get("e") else ""
    u = real_url(c["href"])
    yh = "yahoo" in u.lower() or "valuecommerce" in u or "moshimo" in u
    shop = "楽天トラベル" if "travel.rakuten" in u else ("Yahoo!ショッピング" if yh else ("楽天" if c["pr"] else "公式ページ"))
    img = (f'<img src="{E(c["img"])}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer" '
           f'onerror="this.parentNode.classList.add(\'no\');this.remove()">') if c.get("img") else ""
    ph_cls = "kp" + ("" if img else " no")
    # 11/3 写真がない時も形をそろえる：種類の頭文字を種類の色で出す
    kpi = f'<span class="kpi">{E((c.get("cat") or "・")[0])}</span>'
    go = (f'<a class="go" href="{E(c["href"])}" rel="{rel}" target="_blank" aria-label="{E(c["title"][:40])}を{shop}で見る">'
          f'<span class="nwp">{E(c["title"])}</span></a>')
    rate = c.get("rate") or ""
    rate = re.sub(r"★\s*([\d.]+)\s*[・ ]\s*レビュー\s*([\d,]+)件", r"★\1（\2件）", rate)
    unit = c["tab"] in ("unit", "down", "sale") and c.get("sub") is not None and c["tab"] != "pick" and c.get("kind") != "deal"
    cid = f' id="k{i}"'
    if unit:
        top = E(c["top"])
        m = last_num(c["top"])
        if m:
            hero = (f'<div class="kv"><span class="kvl">{E(m[0])}</span>'
                    f'<b>{E(m[1])}</b><span class="kvu">{E(m[2])}</span></div>')
        else:
            hero = f'<div class="kv"><span class="kvl">{top}</span></div>'
        diff = ""
        if c.get("pct"):
            diff = f'<span class="kd">平均より{c["pct"]}%安い</span>'
        elif c.get("big"):
            diff = f'<span class="kd">{E(c["big"].replace("比べた全部の", ""))}</span>'
        rk = f'<em class="krk{" top" if c.get("rk") in ("1", "2", "3") else ""}">{E(c["rk"])}</em>' if c.get("rk") else ""
        price = c.get("sub") or ""
        return (f'<div class="card it kc ku" data-pref="{E(c["cat"])}" data-free="0" data-wk="0"{e}{cid} style="--pc:{pc}">'
                f'<div class="{ph_cls}">{rk}{kpi}{img}</div><div class="kx">'
                f'<span class="kcat">{E(c["cat"])}</span>{hero[:-6]}{diff}</div>'
                f'<div class="t">{go}</div>'
                + (f'<div class="ks">{E(price)}</div>' if price else "")
                + (f'<div class="kr">{E(rate)}</div>' if rate else "")
                + f'<div class="kbt"><span class="kgo">{shop}で見る<i>›</i></span>' + others(c, shop) + '</div></div></div>')
    # 比べて選んだ物（大きなカード）
    why = c.get("sub") or ""
    but = c.get("but") or ""
    return (f'<div class="card it kc kb2" data-pref="{E(c["cat"])}" data-free="0" data-wk="0"{e}{cid} style="--pc:{pc}">'
            f'<div class="{ph_cls}">{kpi}{img}</div><div class="kx">'
            f'<span class="kcat">{E(c["cat"])}<i>{E(c["top"])}</i></span>'
            f'<div class="t">{go}</div>'
            # 11/3 オーナー「文字ばっかりにならないように。誰も読まない」→ 理由と「ただし」は押した人だけに開く
            + ((f'<details class="kwd"><summary>選んだ理由{"と注意" if but else ""}を見る</summary>'
                + (f'<p class="kwhy"><b>選んだ理由</b>{E(why)}</p>' if why else "")
                + (f'<p class="kbut"><b>ただし</b>{E(but.replace("ただし、", "").replace("ただし", ""))}</p>' if but else "")
                + '</details>') if (why or but) else "")
            + '<div class="kf">' + (f'<span class="kr">{E(rate)}</span>' if rate else "<span></span>")
            + f'<span class="kbt"><span class="kgo">{shop}で見る<i>›</i></span>' + others(c, shop) + '</span></div></div></div>')


TABS = [("pick", "COMPARED", "くらべた物", "/okaimono", ""),
        ("unit", "PER UNIT", "1個あたり", "/tanka", "1個あたり・ふるさと納税を、くわしく見る"),
        ("down", "PRICE DOWN", "値下がり", "/nesage", "値下がりの記録を、くわしく見る"),
        ("sale", "SALE", "セール", "/kaimawari", "買いまわりの1,000円ぽっきりを、ぜんぶ見る")]
NONE = {"down": "値段の記録が2日分たまると、本当に下がった物だけがここに出ます",
        "sale": "いまはセールの物がありません。大きなセールの前に出します"}


def stale(c):
    """11/3 「明日11/1丸亀製麺…」が11/3にも出ていた → 日付が過ぎたお得は出さない"""
    import datetime
    m = re.search(r"(\d{1,2})/(\d{1,2})", c.get("title") or "")
    if not m or c["tab"] != "pick":
        return False
    t = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    try:
        d = datetime.date(t.year, int(m.group(1)), int(m.group(2)))
    except ValueError:
        return False
    if (t.date() - d).days > 300:  # 年をまたぐ（12月に1/5など）
        d = d.replace(year=t.year + 1)
    return d < t.date()


# 11/3 オーナー「うさぎの結論めっちゃわかりやすい。使いやすさと見やすさ、本気で」→ 結論を種類のまとまりで区切る
GROUPS = [("飲み物", ("水", "炭酸水", "お茶", "コーヒー")),
          ("食べ物", ("お米", "パスタ", "プロテイン", "コーヒー豆")),
          ("洗たく・おふろ・台所", ("洗濯洗剤", "柔軟剤", "シャンプー", "ボディソープ", "食器用洗剤")),
          ("くらしの消耗品", ("トイレットペーパー", "ティッシュ", "ゴミ袋", "乾電池", "マスク")),
          ("赤ちゃん", ("おむつ", "おしりふき")),
          ("ペット", ("ドッグフード", "キャットフード")),
          ("ふるさと納税", ("ふるさと納税",))]


def group_of(cat):
    for i, (g, cs) in enumerate(GROUPS):
        if cat in cs:
            return i, g
    return len(GROUPS), "そのほか"


BAG = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M5 8h14l-1 12H6z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg>'


def compared(c):
    return bool(re.match(r"(.+?)(\d+)(つ|軒|社|種類)、", c["title"]) or "｜" in c["title"])


def pick_row(c, i, col):
    """比べて選んだ物を、結論と同じ1行に。押すと理由・注意・お店のボタンが開く（details なので JS いらず）"""
    t = c["title"]
    name, sub, val = t, (c.get("sub") or c["cat"]).split("。")[0], ""
    m = re.match(r"(.+?)(\d+)(つ|軒|社|種類)、(.+)$", t)
    if m:
        name, n, res = m.group(1), m.group(2) + m.group(3), m.group(4).replace("選んだのは", "")
        v = re.match(r"(.*?)約?([\d,.]+)円$", res)
        if v:
            val = v.group(2)
            sub = f"{n}比べた" + (f"・{v.group(1).rstrip('の')}" if v.group(1) else "")
        else:
            sub = f"{n}比べて選んだのは{res}"
    elif "｜" in t:
        name, sub = t.split("｜", 1)
        name = name.replace("楽天ふるさと納税の", "ふるさと納税・")
    pc = col.get(c["cat"], "#8C7B6E")
    u = real_url(c["href"])
    yh = "yahoo" in u.lower() or "valuecommerce" in u or "moshimo" in u
    shop = "楽天トラベル" if "travel.rakuten" in u else ("Yahoo!ショッピング" if yh else ("楽天" if c["pr"] else "公式ページ"))
    rel = "sponsored noopener" if c["pr"] else "noopener"
    im = (f'<img src="{E(c["img"])}" alt="" loading="lazy" referrerpolicy="no-referrer">' if c.get("img")
          else f'<i class="ph0" style="--pc:{pc}">{BAG}</i>')
    why, but, rate = c.get("sub") or "", c.get("but") or "", c.get("rate") or ""
    rate = re.sub(r"★\s*([\d.]+)\s*[・ ]\s*レビュー\s*([\d,]+)件", r"★\1（\2件）", rate)
    body = ((f'<p class="kwhy"><b>選んだ理由</b>{E(why)}</p>' if why else "")
            + (f'<p class="kbut"><b>ただし</b>{E(but.replace("ただし、", "").replace("ただし", ""))}</p>' if but else "")
            + (f'<p class="kr">{E(rate)}</p>' if rate else ""))
    return (f'<details class="kpr" id="k{i}" style="--pc:{pc}"><summary>{im}<span><b>{E(name)}</b>{E(sub)}</span>'
            f'<em>{E(val)}{"<small>円</small>" if val else ""}</em></summary><div class="kpb">{body}'
            f'<div class="kpg"><a class="go kgo2" href="{E(c["href"])}" rel="{rel}" target="_blank">{shop}で見る<i>›</i></a>'
            + others(c, shop) + '</div></div></details>')


def build(od, ix):
    cards = [c for c in collect(ix) if not stale(c)]
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
    h = re.sub(r'<p class="sub">.*?</p>', '<p class="sub">送料込み・1個あたりで、毎日くらべています<span class="kad">リンクは広告です</span></p>'
               , h, count=1, flags=re.S)
    # 11/3 オーナー「上と下どっちもPRいらねぇだろ、同じ画面だぞ上は消せ」→ 上の1行は消す。広告の表示（ステマ規制）は
    # 11/3 オーナー「各ところにPRダサいからやめて」→ ボタン横のPRも消す。広告の表示（ステマ規制）は見出しの下の小さな1か所＋下の欄で守る
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
               f'<p class="ilks">{E(wh)}</p>')
    else:
        top = '<a class="ilk" href="/furusato" data-k="上の入口｜ふるさと納税">ふるさと納税 寄付1万円あたりで比べた<span>→</span></a>'
    n = {t: sum(1 for c in cards if c["tab"] == t) for t, *_ in TABS}
    seen = 0
    for p in ("tanka.html", "furusato.html"):
        seen += sum(int(x.replace(",", "")) for x in re.findall(r"の(\d[\d,]*)件を見て", rd(p)))
    cnt = (f'<p class="cnt" data-v="odekake"><span>比べた物<b id="n-now">{n["pick"] + n["unit"]}</b>件</span>'
           + (f'<span>調べた商品<b>{seen:,}</b>件</span>' if seen else f'<span>値下がり<b>{n["down"]}</b>件</span>') + '</p>')
    # 11/2 オーナー「なんか凄いなってならない」→ どれだけ比べてしぼったかを、上で1枚に（楽天で見た数 → のせた数）
    fs = {"seen": 0, "read": 0, "ok": 0}
    for f in ("tanka.json", "furusato.json"):
        try:
            for cc in json.load(open(os.path.join(R, "data", f), encoding="utf-8")).get("cats", []):
                for k in fs:
                    fs[k] += int(cc.get(k) or 0)
        except Exception:
            pass
    best = max([c.get("pct") or 0 for c in cards] + [0])
    fun = ""
    if fs["seen"] and n["unit"]:
        steps = [("楽天で見た商品", fs["seen"]), ("量を読んで、1個あたりに直した", fs["read"]),
                 ("レビューが多く・評価4.0以上", fs["ok"]), ("同じお店は1つにして、安い順にのせた", n["unit"])]
        lab = ["楽天で見た", "量で比べた", "評価の条件", "のせた"]
        fun = ('<section class="kfun" aria-label="うさぎの比べ方"><p class="kft">うさぎが楽天で比べて、しぼりました</p><div class="kfr">'
               + '<i class="kfa">→</i>'.join(f'<div class="kfs"><b>{v:,}</b><span>{lab[i]}</span></div>' for i, (l, v) in enumerate(steps))
               + '</div>' + (f'<p class="kfx">のせた物は、比べた平均より<b>最大{best}%</b>安い</p>' if best else "") + '</section>')
    flt = ('<nav class="flt" data-v="odekake" aria-label="しぼりこみ"><button class="on" data-p="">すべて</button>'
           + "".join(f'<button data-p="{E(c)}" style="--pc:{col[c]}">{E(c)}</button>' for c in cats) + "</nav>")
    first_t = next((t for t, *_ in TABS if n[t]), "pick")
    otab = ('<nav class="otab" aria-label="おかいもの" data-g1="比べて選ぶ" data-g2="安く買う">' + "".join(
        f'<button type="button" data-t="{t}"{" class=on" if t == first_t else ""}{"" if n[t] else " disabled"}><i>{en}</i>{jp}<small>{n[t]}件</small></button>'
        for t, en, jp, *_ in TABS) + "</nav>")
    panes = ""
    for t, en, jp, link, lt in TABS:
        if t == "pick":
            pk = [c for c in cards if c["tab"] == t]
            a = [pick_row(c, cards.index(c), col) for c in pk if compared(c)]
            b = [pick_row(c, cards.index(c), col) for c in pk if not compared(c)]
            cs = (['<section class="kpl"><div class="kch"><b>うさぎが比べて選んだ物</b><small>押すと理由が開きます</small></div>'
                   + "".join(a) + ('<p class="kgh">ほかのおすすめ</p>' + "".join(b) if b else "") + '</section>'] if (a or b) else [])
        else:
            cs = [card_html(c, col, cards.index(c)) for c in cards if c["tab"] == t]
        more = f'<button class="gm" type="button" data-l="もっと見る（あと">もっと見る（あと{len(cs) - 8}件）</button>' if len(cs) > 8 else ""
        deep = f'<a class="pdeep" href="{link}" data-k="タブの下｜{jp}">{lt}<span>→</span></a>' if lt else ""
        panes += (f'<div class="pane" data-t="{t}"{"" if t == first_t else " hidden"}>{"".join(cs)}{more}'
                  f'<p class="none">{NONE.get(t, "この種類の物は、これから増やしていきます")}</p>{deep}</div>')
    od_sec = (block(h, r'<section class="blk" id="odekake"') or [""])[0]
    h = h.replace(od_sec, f'<section class="blk" id="odekake" data-v="odekake"><div id="kqr" hidden></div>{otab}{panes}</section>')
    for r in (r'<nav class="flt"', r'<p class="cnt"', r'<section class="blk arch" id="archive"'):
        for b in block(h, r):
            h = h.replace(b, "", 1)
    # 11/2 うさぎの結論（360life・mybest のベストバイ型を、種類ごとの1位を1行ずつに）。押すとその商品のカードへ
    con = ""
    ones = [(i, c) for i, c in enumerate(cards) if c["tab"] == "unit" and c.get("rk") == "1"]
    ones.sort(key=lambda x: group_of(x[1]["cat"])[0])
    if ones:
        rows, gl = "", None
        for i, c in ones:
            g = group_of(c["cat"])[1]
            if g != gl:
                rows += f'<p class="kgh">{E(g)}</p>'
                gl = g
            m = last_num(c["top"])
            val = f'{E(m[1])}<small style="display:inline;color:#1A1A1A;font-size:11px">{E(m[2])}</small>' if m else ""
            lab = (m[0] if m else c["top"]).split("・")[-1]
            nm = ("ふるさと納税・" + c["top"].split("・")[0]) if c["cat"] == "ふるさと納税" else c["cat"]
            sub = f'平均より{c["pct"]}%安い' if c.get("pct") else E(c.get("big", "").replace("比べた全部の", ""))
            im = f'<img src="{E(c["img"])}" alt="" loading="lazy" referrerpolicy="no-referrer">' if c.get("img") else '<i class="ph0"></i>'
            rows += (f'<a href="#k{i}" data-t="unit" data-p="{E(c["cat"])}" data-k="結論｜{E(c["cat"])}">{im}'
                     f'<span><b>{E(nm)}</b>{E(lab)}{"いちばん多い" if c["cat"] == "ふるさと納税" else "いちばん安い"}</span><em>{val}<small>{sub}</small></em></a>')
        upd = first(r'"at": "([^"]+)"', open(os.path.join(R, "data", "tanka.json"), encoding="utf-8").read()) if os.path.exists(os.path.join(R, "data", "tanka.json")) else ""
        con = (f'<section class="kcon" aria-label="うさぎの結論"><div class="kch"><b>うさぎの結論</b><small>{E(upd[5:].replace("-", "/"))} 楽天・Yahoo!で確かめた値段</small></div>{rows}</section>')
    # ふるさと納税の締め切り（細い帯1本だけ。秒のカウントダウンはしない）
    import datetime
    today = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    left = (datetime.datetime(today.year, 12, 31) - today).days + 1
    dl = (f'<a class="kdl" href="/furusato" data-k="上の帯｜ふるさと"><span>ふるさと納税　今年の分は12/31まで</span><span>あと<b>{left}</b>日 ›</span></a>'
          if 0 < left <= 100 else "")
    # 11/3 オーナー「目を引く凄いHPに。みんな使いやすく、このAIに調べさせたら楽だと」→ 一番上に「聞く」欄（site/assets/kq.js）。
    # 燈が毎日比べてためた答えからすぐ探す（その場でAIは使わない＝お金がかからない）。無い物は記録して、次の日に燈が比べる
    import lib
    # 11/3 オーナー「めちゃくちゃ使いにくい」→ 一番上は「聞く欄」と大きな種類のボタンだけ。押すとその物の安い順がすぐ出る。他の情報は下へ
    ncat = {}
    for c in cards:
        ncat[c["cat"]] = ncat.get(c["cat"], 0) + 1
    # mybest・Baymard：種類の入口は写真つきの大きなタイル（その種類の1位の写真）。文字だけのボタンより早く見つかる
    pic = {}
    for c in cards:
        if c.get("img") and (c["cat"] not in pic or (c["tab"] == "unit" and c.get("rk") == "1")):
            pic[c["cat"]] = c["img"]
    # 11/3 撮って確かめ：16種類だと答えが画面の下に落ちる → 最初は9つ（1個あたりで比べた物・写真のある物を先に）、残りは「ほかの種類」で開く
    unitc = {c["cat"] for c in cards if c["tab"] == "unit"}
    tiles = [c for c in cats if c not in ("宿", "お店のお得", "楽天のセール", "いち押し")]
    tiles.sort(key=lambda c: (c not in unitc, not pic.get(c), -ncat[c]))
    def tile(c, i):
        return (f'<button type="button" data-q="{E(c)}" style="--pc:{col[c]}"{" class=kqm" if i >= 9 else ""}>'
                + (f'<img src="{E(pic[c])}" alt="" loading="lazy" referrerpolicy="no-referrer">' if pic.get(c) else '<i></i>')
                + f'<b{" class=lg" if len(c) > 6 else ""}>{E(c)}</b><small>{ncat[c]}件</small></button>')
    chips = "".join(tile(c, i) for i, c in enumerate(tiles))
    if len(tiles) > 9:
        chips += f'<button type="button" class="kqmore">ほかの種類も見る（あと{len(tiles) - 9}）</button>'
    ask = (f'<section class="kq" aria-label="AIに聞く" data-amz="{E(lib.AMAZON_TAG)}" data-yh="{E(MOSHIMO_YAHOO)}"><p class="kqh">{E(COPY)}</p>'
           '<form class="kqf" role="search"><input id="kq" type="search" autocomplete="off" enterkeyhint="search" placeholder="例：トイレットペーパー、水、洗剤" aria-label="ほしい物">'
           '<button type="submit">比べる</button></form>'
           + (f'<div class="kqc">{chips}</div>' if chips else "")
           + (f'<p class="kqs">うさぎが楽天の商品<b>{seen:,}</b>件を、送料込み・1個あたりで比べました</p>' if seen else "") + '</section>')
    # 並び：聞く欄 → 種類ごとの1位（結論）→ セールの入口・ふるさとの帯 → 全部の一覧。比べ方の図は一番下
    h = h.replace('<section class="blk" id="odekake"', ask + con + top + dl + flt + '<section class="blk" id="odekake"', 1)
    if fun:
        ob = (block(h, r'<section class="blk" id="odekake"') or [""])[0]
        if ob:
            h = h.replace(ob, ob + fun, 1)
    # ---- 下の欄
    h = re.sub(r'<p class="tip">.*?</p>', "", h, flags=re.S)
    h = re.sub(r'<p class="pr-note">.*?</p>',
               '<p class="pr-note">このページには楽天アフィリエイト・Amazonアソシエイト・もしもアフィリエイト（Yahoo!ショッピング）の広告（PR）があります。<br>値段は確かめた時のものです。買う前に、各お店のページで最新の値段を確かめてください。<br><a href="/privacy">プライバシーポリシーと広告について</a></p>',
               h, count=1, flags=re.S)
    h = h.replace('<a class="co" data-en="LISTING" href="https://ig.me/m/ai_usagichan1" rel="noopener">',
                  '<a class="co" data-en="RAKUTEN ROOM" href="https://room.rakuten.co.jp/ai_usagichan/items" rel="noopener">', 1)
    h = re.sub(r'(<a class="co" data-en="RAKUTEN ROOM"[^>]*>).*?</a>', r'\1楽天ROOM<span>うさぎが比べて選んだ物を、まとめて置いています</span></a>', h, count=1, flags=re.S)
    h = re.sub(r'<p class="ft">.*?</p>', '<p class="ft">LIFE NOTE│比べた物は、このページに毎日足していきます</p>', h, count=1, flags=re.S)
    h = re.sub(r'<a class="tnx" href="/okaimono".*?</a>', '<a class="tnx" href="/odekake" data-k="下の入口｜関東おでかけリスト"><small>関連サイト</small>'
               '<b>関東おでかけリスト<span>→</span></b><i>関東のイベント・新しいお店や施設を、公式ページつきで</i></a>', h, count=1, flags=re.S)
    css = ('<style>'
           '.ilks{text-align:center;font-size:11px;color:var(--sub);margin:-12px 0 16px}'
           # 11/2 100サイトを見て：白・細線・影なし。数字は Jost、主役は1個あたり。写真は冷たいグレーの台に乗せてそろえる
           '#odekake .pane:not([hidden]){display:block}'
           '#odekake .card.it.kc{margin:0 0 12px;padding:14px;border:1px solid #E8E8E8;border-radius:12px;box-shadow:none!important;background:#fff}'
           '#odekake .card.it.kc:after{content:none}'
           '#odekake .card.it.kc[hidden]{display:none!important}'
           '#odekake .kc .kp{position:relative;flex:none;background:#F5F5F7;border-radius:10px;display:flex;align-items:center;justify-content:center;overflow:hidden}'
           '#odekake .kc .kp img{width:100%;height:100%;object-fit:contain;padding:8%;box-sizing:border-box;mix-blend-mode:multiply;display:block}'
           '#odekake .kc .kp.no{display:none}'
           '#odekake .kc .t{margin:4px 0 0;font-size:14px;line-height:1.5;font-weight:700;color:#1A1A1A;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}'
           '#odekake .kc .t .nwp{display:inline}'
           '#odekake .kc .kcat{display:block;font-size:11px;letter-spacing:.08em;color:#6B6B6B}'
           '#odekake .kc .kcat:before{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--pc);margin-right:6px;vertical-align:1px}'
           '#odekake .kc .kcat i{font-style:normal;margin-left:8px;color:#9A9A9A;letter-spacing:.02em}'
           '#odekake .kc .kr{margin-top:4px;font:500 12px/1.4 Jost,"Zen Kaku Gothic New",sans-serif;color:#1A1A1A}'
           '#odekake .kc .kgo{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:700;color:#1A1A1A;border-bottom:1px solid #1A1A1A;padding-bottom:1px}'
           '#odekake .kc .kgo i{font-style:normal;font-family:Jost,sans-serif;font-size:15px;line-height:1}'
           # 横長（1個あたり・値下がり・セール）
           '#odekake .kc.ku{display:flex;gap:14px;align-items:flex-start}'
           '#odekake .kc.ku .kp{width:104px;height:104px}'
           '#odekake .kc.ku .kx{flex:1;min-width:0}'
           '#odekake .kc .krk{position:absolute;left:6px;top:6px;z-index:1;min-width:24px;height:24px;padding:0 5px;box-sizing:border-box;border-radius:99px;border:1px solid #BDBDBD;background:#fff;color:#6B6B6B;font:500 12px/22px Jost,sans-serif;font-style:normal;text-align:center}'
           '#odekake .kc .krk.top{background:#1A1A1A;border-color:#1A1A1A;color:#fff}'
           '#odekake .kc .kv{margin-top:2px;display:flex;align-items:baseline;gap:3px;flex-wrap:wrap;color:#1A1A1A}'
           '#odekake .kc .kvl{font-size:11.5px;color:#6B6B6B;margin-right:2px}'
           '#odekake .kc .kv b{font:500 26px/1.1 Jost,sans-serif;font-variant-numeric:tabular-nums;letter-spacing:-.01em}'
           '#odekake .kc .kvu{font-size:12px;font-weight:700}'
           '#odekake .kc .kd{display:inline-block;margin-top:4px;padding:2px 8px;border-radius:99px;background:#E8F3EE;color:#1F6B4F;font-size:11px;font-weight:700}'
           '#odekake .kc.ku .t{font-size:12.5px;font-weight:500;color:#333;margin-top:6px}'
           '#odekake .kc .ks{margin-top:3px;font-size:11.5px;line-height:1.5;color:#6B6B6B}'
           '#odekake .kc.ku .kgo{margin-top:8px}'
           '#odekake .kc .kbt{display:flex;align-items:center;gap:14px;flex-wrap:wrap}#odekake .kc.ku .kbt{margin-top:8px}#odekake .kc.ku .kbt .kgo{margin-top:0}'
           '#odekake .kc .kot{display:inline-flex;gap:12px}#odekake .kc.kb2 .kf{flex-wrap:wrap;row-gap:10px}#odekake .kc.kb2 .kf .kr{white-space:nowrap}#odekake .kc.kb2 .kf .kbt{margin-left:auto}#odekake .kc .kyh{position:relative;z-index:2;display:inline-flex;align-items:center;gap:5px;font-size:11.5px;font-weight:700;color:#6B6B6B;text-decoration:none;border-bottom:1px solid #BDBDBD;padding-bottom:1px}'
           '#odekake .kc .kyh i{font-style:normal;font-family:Jost,sans-serif;font-size:14px;line-height:1}'
           # 大きなカード（比べて選んだ物）
           '#odekake .kc.kb2{padding:0;overflow:hidden}'
           '#odekake .kc.kb2 .kp{border-radius:0;aspect-ratio:4/3;width:100%}'
           '#odekake .kc.kb2 .kp img{padding:6%}'
           '#odekake .kc.kb2 .kx{padding:14px 16px 16px}'
           '#odekake .kc.kb2 .t{margin-top:6px;font:600 18px/1.5 var(--min);letter-spacing:.02em;-webkit-line-clamp:3}'
           '#odekake .kc .kwhy,#odekake .kc .kbut{margin:10px 0 0;font-size:12.5px;line-height:1.7;color:#333}'
           '#odekake .kc .kwhy b,#odekake .kc .kbut b{display:inline-block;margin-right:8px;font-size:10.5px;letter-spacing:.06em;color:#1F6B4F;border:1px solid currentColor;border-radius:3px;padding:0 5px;line-height:1.6;vertical-align:1px}'
           '.head .sub .kad{display:block;margin-top:2px;font-size:10px;color:#A0A0A0;letter-spacing:.02em}'
           '#odekake .kc .kwd{position:relative;z-index:2;margin-top:10px}'
           '#odekake .kc .kwd summary{display:inline-flex;align-items:center;gap:6px;list-style:none;cursor:pointer;font-size:12px;font-weight:700;color:#6B6B6B}'
           '#odekake .kc .kwd summary::-webkit-details-marker{display:none}'
           '#odekake .kc .kwd summary:after{content:"＋";font-size:12px;color:#9A9A9A}#odekake .kc .kwd[open] summary:after{content:"−"}'
           '#odekake .kc.kb2 .t{-webkit-line-clamp:2!important}'
           # 11/3 オーナー「見やすく」→ 写真が画面いっぱいで1枚しか見えなかった。写真は左に小さく、横長のカードに（1個あたりと同じ形）
           '#odekake .kc.kb2{display:flex!important;gap:14px;align-items:flex-start;padding:16px!important}'
           '#odekake .kc.kb2 .kp{width:96px!important;height:96px!important;aspect-ratio:auto!important;border-radius:10px!important;flex:none}'
           '#odekake .kc.kb2 .kp img{padding:8%}'
           '#odekake .kc.kb2 .kx{flex:1;min-width:0;padding:0!important}'
           '#odekake .kc.kb2 .t{font-size:15.5px!important;line-height:1.5!important;margin-top:4px}'
           '#odekake .kc.kb2 .kcat i{display:none}'
           # 11/3 写真なしでも同じ形に（頭文字）。1個あたりは「平均より◯%安い」を値段の横に並べて短く
           '#odekake .kc .kpi{display:none}'
           '#odekake .kc.kb2 .kp.no,#odekake .kc.ku .kp.no{display:flex!important;background:color-mix(in srgb,var(--pc) 12%,#fff)}'
           '#odekake .kc .kp.no .kpi{display:block;font:600 34px/1 var(--min),serif;color:var(--pc)}'
           '#odekake .kc.ku .kv .kd{margin:0 0 0 6px;align-self:center}'
           '#odekake .kc.ku .kbt{margin-top:6px}'  # 「3つ以上を比べて選んだ物」は毎回同じなので、上の説明1か所に
           '#odekake .kc .kbut{color:#555;margin-top:6px}#odekake .kc .kbut b{color:#8A6D3B}'
           '#odekake .kc .kf{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:14px;padding-top:12px;border-top:1px solid #EFEFEF}'
           # ページの上の1行（広告の表示）と、結論
           '.head .kprl{position:relative;margin:10px 0 0;text-align:center;font-size:10.5px;line-height:1.5;color:#9A9A9A}'
           '.kcon{margin:0 0 16px;border:1px solid #E8E8E8;border-radius:12px;overflow:hidden}'
           '.kcon .kch{display:flex;justify-content:space-between;align-items:baseline;padding:12px 14px 8px}'
           '.kcon .kch b{font:600 15px/1.4 var(--min);letter-spacing:.08em;color:#1A1A1A}'
           '.kcon .kch small{font-size:10.5px;color:#9A9A9A}'
           '.kcon a{display:grid;grid-template-columns:44px 1fr auto;gap:10px;align-items:center;padding:9px 14px;border-top:1px solid #F0F0F0;text-decoration:none;color:#1A1A1A}'
           '.kcon a img,.kcon a .ph0{width:44px;height:44px;border-radius:8px;background:#F5F5F7;object-fit:contain;mix-blend-mode:multiply}'
           '.kcon a .ph0{display:block}'
           '.kcon a span{min-width:0;font-size:11.5px;color:#6B6B6B;line-height:1.4}'
           '.kcon a span b{display:block;font-size:13px;color:#1A1A1A;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'
           '.kcon a em{font-style:normal;text-align:right;font:500 20px/1.1 Jost,sans-serif;color:#1A1A1A;white-space:nowrap}'
           # 11/3 結論のまとまり見出し・比べて選んだ物の1行（結論と同じ形。押すと開く）
           '.kcon .kgh,.kpl .kgh{margin:0;padding:14px 14px 6px;border-top:1px solid #F0F0F0;font-size:11px;font-weight:700;letter-spacing:.12em;color:#8C8C8C;background:#FAFAFA}'
           '.kpl{margin:0 0 16px;border:1px solid #E8E8E8;border-radius:12px;overflow:hidden;background:#fff}'
           '.kpl .kch{display:flex;justify-content:space-between;align-items:baseline;padding:12px 14px 8px}'
           '.kpl .kch b{font:600 15px/1.4 var(--min);letter-spacing:.08em;color:#1A1A1A}.kpl .kch small{font-size:10.5px;color:#9A9A9A}'
           '.kpr{border-top:1px solid #F0F0F0}'
           '.kpr summary{display:grid;grid-template-columns:44px 1fr auto 14px;gap:10px;align-items:center;padding:10px 14px;cursor:pointer;list-style:none}'
           '.kpr summary::-webkit-details-marker{display:none}'
           '.kpr summary:after{content:"+";font:300 18px/1 Jost,sans-serif;color:#9A9A9A;text-align:center}.kpr[open] summary:after{content:"−"}'
           '.kpr summary img,.kpr summary .ph0,.kcon a .ph0{width:44px;height:44px;border-radius:8px;background:#F5F5F7;object-fit:contain;mix-blend-mode:multiply}'
           '.kpr summary .ph0,.kcon a .ph0{display:flex;align-items:center;justify-content:center;font:600 18px/1 var(--min),serif;font-style:normal;color:var(--pc,#8C7B6E);background:color-mix(in srgb,var(--pc,#8C7B6E) 12%,#fff)}'
           '.kpr summary span{min-width:0;font-size:11.5px;color:#6B6B6B;line-height:1.45}'
           '.kpr summary span b{display:block;font-size:13.5px;color:#1A1A1A;font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}'
           '.kpr summary em{font-style:normal;font:500 19px/1.1 Jost,sans-serif;color:#1A1A1A;white-space:nowrap}'
           '.kpr summary em small{font:700 11px "Zen Kaku Gothic New",sans-serif;margin-left:1px}'
           '.kpb{padding:2px 14px 14px 68px;font-size:12.5px;line-height:1.7;color:#333}'
           '.kpb p{margin:0 0 6px}.kpb p b{display:inline-block;margin-right:8px;font-size:11px;color:#6B6B6B}'
           '.kpb .kbut b{color:#A0522D}'
           '.kpg{display:flex;flex-wrap:wrap;align-items:center;gap:14px;margin-top:8px}'
           '.kpg .kgo2{display:inline-flex;align-items:center;gap:6px;padding:9px 16px;border-radius:99px;background:#1A1A1A;color:#fff;font-size:12.5px;font-weight:700;text-decoration:none}'
           '.kpg .kgo2 i{font-style:normal;font-family:Jost,sans-serif}'
           '.kpg .kot{display:inline-flex;gap:16px}.kpg .kyh{display:inline-flex;gap:4px;font-size:12px;font-weight:700;color:#6B6B6B;text-decoration:none;border-bottom:1px solid #BDBDBD;padding-bottom:1px}.kpg .kyh i{font-style:normal}'
           '.kcon a em small{display:block;font:700 10px "Zen Kaku Gothic New",sans-serif;color:#1F6B4F;margin-top:2px}'
           '.kdl{display:flex;justify-content:space-between;align-items:center;gap:8px;margin:0 0 10px;padding:8px 12px;border-radius:8px;background:#F5F5F7;font-size:11.5px;color:#333;text-decoration:none}'
           '.kdl b{font:500 15px Jost,sans-serif;color:#1A1A1A;margin:0 2px}'
           '.kfun{margin:0 0 18px;padding:12px 12px 10px;border:1px solid #E6E7EA;border-radius:12px;background:#fff}'
           '.kft{margin:0 0 8px;text-align:center;font:600 12.5px/1.4 "Zen Kaku Gothic New",sans-serif;letter-spacing:.06em;color:#231E1B}'
           '.kft i{display:none}'
           '.kfr{display:grid;grid-template-columns:1fr auto 1fr auto 1fr auto 1fr;align-items:center;text-align:center}'
           '.kfs b{display:block;font:600 19px/1.1 Jost,sans-serif;color:#231E1B}.kfs:last-child b{color:#C0392B;font-size:23px}'
           '.kfs span{display:block;margin-top:3px;font-size:9.5px;line-height:1.3;color:#8C7B6E}'
           '.kfa{color:#C9B8A8;font-family:Jost,sans-serif;font-size:13px}'
           '.kfx{margin:8px 0 0;text-align:center;font-size:11.5px;font-weight:700;color:#231E1B}.kfx b{font:600 15px Jost,sans-serif;color:#C0392B;margin:0 2px}'
           '.pdeep{display:block;width:max-content;max-width:100%;margin:6px auto 4px;color:#231E1B;text-decoration:none;font:600 13px/1.5 var(--min);letter-spacing:.06em;border-bottom:1px solid #231E1B;padding-bottom:3px}'
           '.pdeep span{font-family:Jost;margin-left:8px;color:#9C8775}'
           '.flt[data-v=odekake]{flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none}.flt[data-v=odekake]::-webkit-scrollbar{display:none}'
           '.flt[data-v=odekake] button{flex:none}.flt button.hid{display:none}'
           'h1.ttl:not(:where(.tn *)){font-size:clamp(20px,6.2vw,30px);letter-spacing:.06em;white-space:nowrap}'
           '.flt[data-v=odekake]{justify-content:flex-start}.flt[data-v=odekake]:before,.flt[data-v=odekake]:after{content:"";flex:1 0 0}'
           # 11/3 聞く欄（白・細線。ボタンだけ黒）
           '.kq{margin:4px 0 18px;padding:16px 14px 12px;border:1px solid #1A1A1A;border-radius:14px;background:#fff}'
           '.kqh{margin:0 0 10px;text-align:center;font:600 16px/1.5 var(--min);letter-spacing:.06em;color:#1A1A1A}'
           '.kqf{display:flex;gap:8px;margin:0}'
           '.kqf input{flex:1;min-width:0;height:46px;padding:0 14px;border:1px solid #D0D0D0;border-radius:10px;font-size:16px;background:#fff;color:#1A1A1A;-webkit-appearance:none;box-sizing:border-box}'
           '.kqf input:focus{outline:none;border-color:#1A1A1A}'
           '.kqf button{flex:none;height:46px;padding:0 18px;border:0;border-radius:10px;background:#1A1A1A;color:#fff;font-size:15px;font-weight:700}'
           '.kqc{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:12px}'
           '.kqc button{position:relative;padding:12px 4px 10px;border:1px solid #E0E0E0;border-radius:10px;background:#fff;color:#1A1A1A;text-align:center;min-height:58px}'
           '.kqc button:before{content:"";position:absolute;left:50%;top:0;width:24px;height:3px;margin-left:-12px;border-radius:0 0 3px 3px;background:var(--pc)}'
           '.kqc button img,.kqc button i{display:block;width:52px;height:52px;margin:0 auto 6px;object-fit:contain;mix-blend-mode:multiply;background:#F5F5F7;border-radius:8px}'
           '.kqf{position:sticky;top:6px;z-index:5}'
           '#kqr .kqg{margin:0 0 14px;padding:12px 14px;border:1px solid #E8E8E8;border-radius:12px}#kqr .kqg p{margin:0 0 8px;font-size:11px;color:#6B6B6B}'
           '#kqr .kqr{display:grid;grid-template-columns:30px 1fr auto;gap:8px;align-items:center;margin:6px 0}'
           '#kqr .kqr img,#kqr .kqr i{width:30px;height:30px;border-radius:6px;object-fit:contain;background:#F5F5F7;mix-blend-mode:multiply;display:block}'
           '#kqr .kqr span{height:10px;border-radius:99px;background:#F0F0F2;overflow:hidden}#kqr .kqr em{display:block;height:100%;border-radius:99px;background:#C8CCD2}'
           '#kqr .kqr.b em{background:#1F6B4F}#kqr .kqr b{font:600 15px Jost,sans-serif;color:#1A1A1A;white-space:nowrap}#kqr .kqr b small{font:700 10px "Zen Kaku Gothic New",sans-serif;margin-left:1px}'
           '#kqr .kqr.b b{color:#1F6B4F}'
           '.kqc .kqm{display:none}.kqc.op .kqm{display:block}.kqc .kqmore{grid-column:1/-1;min-height:0;padding:9px;font-size:12.5px;color:#333}.kqc.op .kqmore{display:none}'
           '.kqc button b.lg{font-size:11.5px;letter-spacing:-.02em}'
           '.kqon2 .kqc,.kqon2 .kqs,.kqon2 .otab{display:none!important}'
           '.kqc button b{display:block;font-size:13.5px;line-height:1.3}.kqc button small{display:block;margin-top:2px;font:500 11px Jost,sans-serif;color:#6B6B6B}'
           '.kqs{margin:10px 0 0;text-align:center;font-size:11px;color:#6B6B6B}.kqs b{font:600 13px Jost,sans-serif;color:#1A1A1A;margin:0 2px}'
           '.kqon2 .kcon,.kqon2 .kfun,.kqon2 .kdl,.kqon2 a.ilk,.kqon2 .ilks{display:none!important}'
           '#kqr{margin:0 0 16px}'
           '#kqr .kqt{margin:0 0 10px;font-size:13px;font-weight:700;color:#1A1A1A}#kqr .kqt small{display:block;font-weight:400;font-size:11px;color:#6B6B6B;margin-top:2px}'
           '#kqr .kqn{padding:16px;border:1px solid #E8E8E8;border-radius:12px;font-size:13px;line-height:1.7;color:#333}'
           '#kqr .kqn a{display:inline-block;margin:10px 14px 0 0;font-weight:700;color:#1A1A1A;border-bottom:1px solid #1A1A1A;text-decoration:none}'
           '#kqr .kqx{display:block;margin:6px auto 0;padding:8px 16px;border:1px solid #D0D0D0;border-radius:99px;background:#fff;font-size:12px;color:#333}'
           '#kqr .kqb{margin:0 0 6px;font-size:11.5px;font-weight:700;letter-spacing:.04em;color:#1F6B4F}'
           '#odekake #kqr .card.it.kc.kq1{border:2px solid #1A1A1A}'
           '#kqr .kqe{margin:4px 0 10px;padding:10px 12px;border-radius:10px;background:#F5F5F7}#kqr .kqe small{display:block;font-size:11px;color:#6B6B6B;margin-bottom:4px}#kqr .kqe .ilk{margin:0}'
           'body.okp .flt[data-v=odekake],#odekake .pane[data-t=pick] .none{display:none!important}'
           '#odekake.kqon>.otab,#odekake.kqon>.pane{display:none!important}.kqon2 .flt[data-v=odekake]{display:none}'
           '</style>')
    h = h.replace("</head>", css + "</head>", 1)
    # 種類のしぼりこみは、いま開いているタブにある種類だけ出す／押されたPRを数える／下のボタン列は買い物の4つ
    js = ('<script>(function(){'
          'function sync(){var on=document.querySelector(".otab button.on"),t=on?on.dataset.t:"pick",has={};document.body.classList.toggle("okp",t==="pick");'
          'document.querySelectorAll(\'#odekake .pane[data-t="\'+t+\'"] .card.it\').forEach(function(c){has[c.dataset.pref]=1;});'
          'document.querySelectorAll(".flt button[data-p]").forEach(function(b){if(b.dataset.p)b.classList.toggle("hid",!has[b.dataset.p]);});'
          'var cur=document.querySelector(".flt button.on");if(cur&&cur.dataset.p&&!has[cur.dataset.p]){var a=document.querySelector(\'.flt button[data-p=""]\');if(a)a.click();}}'
          'function en(){document.querySelectorAll(".otab button").forEach(function(b){if(document.querySelector(\'#odekake .pane[data-t="\'+b.dataset.t+\'"] .card.it\'))b.disabled=false;});}'
          'document.querySelectorAll(".otab button").forEach(function(b){b.addEventListener("click",function(){setTimeout(sync,0);});});'
          'document.querySelectorAll(".flt button[data-p]").forEach(function(b){b.addEventListener("click",function(){setTimeout(en,0);});});sync();'
          'document.querySelectorAll(".kcon a").forEach(function(a){a.addEventListener("click",function(ev){ev.preventDefault();'
          'var b=document.querySelector(\'.otab button[data-t="\'+a.dataset.t+\'"]\');if(b)b.click();'
          'var f=document.querySelector(\'.flt button[data-p="\'+a.dataset.p+\'"]\');setTimeout(function(){if(f)f.click();'
          'var el=document.querySelector(a.getAttribute("href"));if(el)scrollTo({top:el.getBoundingClientRect().top+scrollY-80,behavior:"smooth"});},60);});});'
          'var F="";try{F=sessionStorage.getItem("f")||"";}catch(e){}'
          'document.addEventListener("click",function(ev){var a=ev.target.closest&&ev.target.closest("a.go[rel~=sponsored],a.ilk[rel~=sponsored],a.kyh");if(!a||!navigator.sendBeacon)return;'
          'var p=a.closest(".pane"),k=((a.classList.contains("kyh")||a.classList.contains("kgo2"))?a.textContent.replace(/[›\\s]/g,"")+"｜"+((a.closest(".kc")||a).querySelector(".go")||(a.closest(".kpr")||a).querySelector("summary b")||a).textContent:a.textContent).replace(/\\s+/g,"").slice(0,30);'
          'try{navigator.sendBeacon("/c?f="+encodeURIComponent(F||"direct")+"&s="+encodeURIComponent(("okai-"+(p?p.dataset.t:"top")).slice(0,16))+"&k="+encodeURIComponent(k));}catch(e){}},true);'
          'var q=null;try{q=new URLSearchParams(location.search).get("t");}catch(e){}var hs=location.hash.slice(1);if(!q&&hs)q={deal:"sale",sale:"sale",shop:"pick",trip:"pick",hot:"pick",unit:"unit",down:"down"}[hs]||null;if(q){var b=document.querySelector(\'.otab button[data-t="\'+q+\'"]\');if(b&&!b.disabled)b.click();}'
          '})();</script>')
    h = h.replace('<body class="', '<body data-bar="okai" class="', 1)
    h = h.replace("c.hidden=!ok||(!op&&k>5);", "c.hidden=!ok||(!op&&k>8);").replace('m.dataset.l+(k-5)+"件）";m.hidden=op||k<=5;', 'm.dataset.l+(k-8)+"件）";m.hidden=op||k<=8;')
    js += '<script src="/assets/kq.js?v=4" defer></script><script src="/assets/okv.js?v=3" defer></script>'
    i = h.rfind("</body>")
    return h[:i] + js + h[i:]
