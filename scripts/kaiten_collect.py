"""（usagi の tools/kaiten/collect.py と同じ物。直す時は両方）開店・閉店ニュースを、公式の発表から機械で毎日集める（11/17 夜〜。オーナー「手抜き」「UI/UXは素晴らしいものに」を受けて）。
それまでは月が1件ずつ手で足していた（関西28件）。外のまとめは月に約1,000件（kaiten-1117/sources.md の推測）なので、桁が足りなかった。

元（どれも会社・施設の公式の発表。外のまとめサイトの文は使わない）：
  1. PR TIMES の新着（https://prtimes.jp/sitemap-news.xml、約15時間ぶん）。題で「オープン・開店・閉店・出店」などを選び、
     発表のページを開いて、位置情報（店舗・民間施設）か本文の「住所・所在地」で府県を決める。本文の「営業時間」「アクセス」も拾う。
  2. ローソンの新店（関東・近畿の表。開店日・住所が表で出ている）。
  3. ダイソーの NEW SHOP（題に府県が入っている。住所は出ていないので、府県と店名だけ）。
画像は使わない（PR TIMES の画像は報道の目的だけ。報道規約3条1項・6条）。文は題と本文の事実（住所・時間・駅）だけを短く。

使い方: python3 tools/kaiten/collect.py kansai|kanto [YYYY-MM-DD]
  kansai → tools/kaiten/kansai.json（usagi）、kanto → data/kaiten.json（akari に同じ物を置く）に足す。
  見た発表は seen.json（14日）に残して、2回開かない。1回に開く発表は60件まで（相手のサイトに負担をかけない。1.2秒あける）。
"""
import datetime, html, json, os, re, sys, time, urllib.request

REGION = sys.argv[1] if len(sys.argv) > 1 else "kansai"
TODAY = datetime.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).date()
HERE = os.path.dirname(os.path.abspath(__file__))
PREFS = {"kansai": ["大阪府", "京都府", "兵庫県", "奈良県", "滋賀県", "和歌山県"],
         "kanto": ["東京都", "神奈川県", "埼玉県", "千葉県", "茨城県", "栃木県", "群馬県"]}[REGION]
SHORT = {p: re.sub(r"[都府県]$", "", p) if p != "東京都" else "東京" for p in PREFS}
# usagi と akari で置き場所がちがう
DATA = os.environ.get("KAITEN_DATA") or os.path.join(HERE, "..", "data", "kaiten.json")
SEEN = os.environ.get("KAITEN_SEEN") or os.path.join(HERE, "..", "data", f"kaiten-seen-{REGION}.json")
UA = {"User-Agent": "Mozilla/5.0 (compatible; TownNoteBot/1.0; +https://kanto.townnote.app/)"}
MAXOPEN = 60

# 題で選ぶ・外す言葉
WANT = re.compile(r"オープン|ＯＰＥＮ|OPEN|開店|閉店|出店|新店|移転|開業|グランドオープン|リニューアル")
NOT = re.compile(r"オンライン|ＥＣ|EC|Amazon|楽天市場|TikTok|アプリ|サイト|チャンネル|ウェビナー|セミナー|説明会|募集|求人|採用|大会|"
                 r"出店者|催事|販売開始|発売|予約開始|配信|放送|連載|ラボ|オープンイノベーション|オープンハウス|オープンキャンパス|"
                 r"オープンソース|オープンデータ|オープンAPI|特許|株式|決算|資金調達|提携|受賞|ランキング|調査|アンケート")
SHOPLOC = re.compile(r"店舗・民間施設")


def get(u):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25)
    b = r.read()
    cs = (re.search(rb'charset=["\']?([\w-]+)', b[:4000]) or [None, b"utf-8"])[1].decode().lower()
    return b.decode("cp932" if cs in ("shift_jis", "sjis", "x-sjis") else cs, "replace")


def text(h):
    h = re.sub(r"<script.*?</script>|<style.*?</style>|<svg.*?</svg>", "", h, flags=re.S)
    h = re.sub(r"<br\s*/?>|</p>|</h\d>|</li>|</div>|</tr>|</dd>|</dt>", "\n", h)
    h = re.sub(r"</t[dh]>", " | ", h)
    h = html.unescape(re.sub(r"<[^>]+>", "", h))
    h = re.sub(r"[ \t　\xa0]+", " ", h)
    return re.sub(r"\n\s*\n+", "\n", h)


def z2h(s):
    return s.translate(str.maketrans("０１２３４５６７８９：（）～", "0123456789:()〜"))


def find_date(s, pub):
    """題・本文の「11月20日」「2026年12月4日」を、発表の日に近い未来/過去の日付にする。"""
    s = z2h(s)
    out = []
    for m in re.finditer(r"(?:(20\d\d)\s*年\s*)?(\d{1,2})\s*月\s*(\d{1,2})\s*日", s):
        y = int(m.group(1)) if m.group(1) else pub.year
        try:
            d = datetime.date(y, int(m.group(2)), int(m.group(3)))
        except ValueError:
            continue
        if not m.group(1) and d < pub - datetime.timedelta(days=60):
            d = d.replace(year=y + 1)
        out.append(d)
    for m in re.finditer(r"(20\d\d)[./](\d{1,2})[./](\d{1,2})", s):
        try:
            out.append(datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3))))
        except ValueError:
            pass
    return out


def name_of(title):
    t = title.replace("『", "「").replace("』", "」")
    # 「A」「B」が…オープン → A・B（主語のかぎかっこ）
    m = re.search(r"((?:「[^」]{1,40}」[、・と\s]*)+)(?:が|を|は|、が|の\d)", t)
    if m:
        ns = [x for x in re.findall(r"「([^」]{1,40})」", m.group(1)) if not re.search(r"楽しさ|体感|^初$|^新$", x)]
        if ns:
            return "・".join(ns)[:50]
    # オープン等の直前のかぎかっこ
    m = list(re.finditer(r"「([^」]{2,40})」", t[:max((t.find(w) for w in ("オープン", "OPEN", "開店", "閉店", "出店", "開業") if w in t), default=len(t))]))
    if m:
        return m[-1].group(1)
    for a, b in (("「", "」"), ("『", "』"), ("“", "”")):
        for m in re.finditer(re.escape(a) + r"(.{2,40}?)" + re.escape(b), title):
            n = m.group(1).strip()
            if not re.search(r"^(初|新|話題|待望|ついに)$", n):
                return n
    return ""


def pref_of(s):
    for p in PREFS:
        if p in s:
            return p
    return ""


def kind_of(title):
    if re.search(r"閉店|閉館|営業終了|クローズ", title):
        return "close"
    if re.search(r"期間限定|POP\s*-?\s*UP|ポップアップ|ＰＯＰ", title, re.I):
        return "pop"
    return "open"


def prtimes(seen, have):
    xml = get("https://prtimes.jp/sitemap-news.xml")
    adds, opened = [], 0
    for m in re.finditer(r"<loc>(.*?)</loc>.*?<news:publication_date>(.*?)</news:publication_date>.*?<news:title>(.*?)</news:title>", xml, re.S):
        u, pd, t = m.group(1).strip(), m.group(2)[:10], html.unescape(m.group(3)).strip()
        if u in seen or u in have or not WANT.search(t) or NOT.search(t):
            continue
        if opened >= MAXOPEN:
            break
        seen[u] = TODAY.isoformat()
        opened += 1
        try:
            h = get(u)
        except Exception as e:
            print("ERR", u, str(e)[:80])
            continue
        time.sleep(1.2)
        x = from_release(u, t, datetime.date.fromisoformat(pd), h)
        if x:
            adds.append(x)
    return adds


def from_release(u, t, pub, h):
    i, j = h.find('id="press-release-body"'), h.find("このプレスリリースには")
    body = text(h[i:j] if i > 0 and j > i else h)
    loc = text(h[h.find("位置情報"):h.find("位置情報") + 3000]) if "位置情報" in h else ""
    loc = re.sub(r"\s+", "", loc.split("ダウンロード")[0].split("関連リンク")[0])
    shops = [m.group(1) for m in re.finditer(r"((?:" + "|".join(PREFS) + r")[^（(]{0,12})[（(]店舗・民間施設", loc)]
    # 会社概要・問い合わせより前だけ（本社の住所を拾わない）
    body = re.sub(r"[ \t]*\n[ \t]*\|[ \t]*\n[ \t]*", "：", body)  # 表（項目 | 中身）を「項目：中身」に
    body = re.split(r"【?会社概要】?|■会社概要|＜会社概要＞|会社情報\n|本件に関する(?:お)?問い?合わせ|報道関係者", body)[0]
    addr = ""
    for m in re.finditer(r"(?:住所|所在地|場所|店舗所在地)\s*[:：]?\s*(?:〒?\s*\d{3}-?\d{4}\s*)?([^\n]{6,60})", body):
        a = re.split(r"[:：][^\s:：]{2,8}[:：]", z2h(m.group(1)))[0].strip(" ・:：")
        if re.search(r"代表|運営|は、|が運営|本社", a) or not re.search(r"\d|丁目|番地", a):
            continue
        a = re.split(r"[)）](?!.*[（(])", a)[0] if a.count(")") + a.count("）") > a.count("(") + a.count("（") else a
        if pref_of(a) or (shops and re.match(r"\S+?[市区町村]", a)):
            addr = a
            break
    p = pref_of(addr) or (pref_of(shops[0]) if shops else "")
    if not p:
        return None  # この地方のお店ではない／お店の場所が書いていない
    city = shops[0][len(p):] if shops and pref_of(shops[0]) == p else ""
    pl = addr[len(p):] if addr.startswith(p) else (addr or city)
    pl = re.split(r"\s{2,}|※", pl)[0].strip()[:48]
    st = ""
    m = re.search(r"[「『]?([^\s「」『』、。:：]{1,14}?駅)[」』]?[^\n。]{0,24}?徒歩\s*(?:約)?\s*(\d{1,2})\s*分", z2h(body))
    if m:
        st = f"{m.group(1)}から徒歩{m.group(2)}分"
    tm = ""
    m = re.search(r"営業時間\s*[:：]?\s*([^\n]{3,50})", z2h(body))
    if m:
        tm = re.split(r"※|（L\.?O|\(L\.?O|[:：][^\s:：]{2,8}[:：]", m.group(1))[0].strip(" ・:：")[:40]
    k = kind_of(t)
    ds = [d for d in find_date(t, pub) if pub - datetime.timedelta(days=45) <= d <= pub + datetime.timedelta(days=400)]
    if not ds:
        near = re.search(r"[^\n]{0,60}(?:オープン|開店|閉店|開業|OPEN)[^\n]{0,20}", body)
        ds = [d for d in find_date(near.group(0) if near else "", pub) if pub - datetime.timedelta(days=45) <= d <= pub + datetime.timedelta(days=400)]
    if not ds:
        return None  # 日付の無い発表は載せない（いつか分からない物は「速報」にならない）
    n = name_of(t)
    if not n:
        return None
    pt = re.sub(r"【[^】]*】|\s+", " ", t).strip()
    pt = pt if len(pt) <= 80 else pt[:79] + "…"
    x = {"d": ds[0].isoformat(), "k": k, "p": SHORT[p], "n": n, "pt": pt, "pl": (pl + ("・" + st if st and st not in pl else ""))[:70],
         "tm": tm, "u": u, "added": TODAY.isoformat(), "src": "prtimes", "auto": 1}
    if k == "pop" and len(ds) > 1 and ds[1] > ds[0]:
        x["end"] = ds[1].isoformat()
    if re.search(r"リニューアル", t):
        x["sub"] = "リニューアル"
    return x


def lawson(have):
    u = {"kansai": "https://www.lawson.co.jp/newstore/kinki.html", "kanto": "https://www.lawson.co.jp/newstore/kantou.html"}[REGION]
    t = re.sub(r"\s+", " ", text(get(u)))
    adds = []
    for m in re.finditer(r"(" + "|".join(PREFS) + r") \| (20\d\d)年(\d\d)月(\d\d)日 \| ([^|]{1,40}?) \| ([^|]{4,80}?) \|", t):
        p, d, nm, ad = m.group(1), datetime.date(int(m.group(2)), int(m.group(3)), int(m.group(4))), m.group(5).strip(), z2h(m.group(6).strip())
        n = "ローソン " + nm + ("店" if not nm.endswith("店") else "")
        if (u, n) in have:
            continue
        adds.append({"d": d.isoformat(), "k": "open", "p": SHORT[p], "n": n, "pt": "ローソンの新しいお店（ローソンの新店情報より）。",
                     "pl": (ad[len(p):] if ad.startswith(p) else ad)[:60], "tm": "", "u": u, "added": TODAY.isoformat(), "src": "lawson", "auto": 1, "g": "コンビニ"})
    return adds


def daiso(have):
    u = "https://www.daiso-sangyo.co.jp/infolist/shop"
    h = get(u)
    adds = []
    for m in re.finditer(r'href="(https://www\.daiso-sangyo\.co\.jp/[\w/]+)" class="articleList-link">(.*?)</a>', h, re.S):
        tt = re.sub(r"\s+", " ", text(m.group(2))).strip()
        mm = re.search(r"(20\d\d)\.(\d\d)\.(\d\d).*?((?:DAISO|Standard Products|THREEPPY)[^（(]+?)\s*[（(](\S+?[都府県])[）)]\s*(オープン|改装)", tt)
        if not mm or mm.group(5) not in PREFS:
            continue
        n = mm.group(4).strip()
        if (m.group(1), n) in have:
            continue
        adds.append({"d": f"{mm.group(1)}-{mm.group(2)}-{mm.group(3)}", "k": "open", "p": SHORT[mm.group(5)], "n": n,
                     "pt": ("改装して新しくなりました" if mm.group(6) == "改装" else "新しく開いたお店") + "（大創産業の NEW SHOP のお知らせより）。",
                     "pl": "", "tm": "", "u": m.group(1), "added": TODAY.isoformat(), "src": "daiso", "auto": 1, "g": "100円ショップ",
                     **({"sub": "リニューアル"} if mm.group(6) == "改装" else {})})
    return adds


def main():
    data = json.load(open(DATA, encoding="utf-8"))
    items = data["items"]
    have = {(x["u"], x["n"]) for x in items} | {x["u"] for x in items if x.get("src") == "prtimes"}
    seen = {}
    if os.path.exists(SEEN):
        seen = {k: v for k, v in json.load(open(SEEN, encoding="utf-8")).items() if (TODAY - datetime.date.fromisoformat(v)).days <= 14}
    got = {}
    for nm, fn in (("prtimes", lambda: prtimes(seen, have)), ("lawson", lambda: lawson(have)), ("daiso", lambda: daiso(have))):
        try:
            a = fn()
        except Exception as e:
            print("ERR", nm, str(e)[:120])
            a = []
        # 同じ店（店名と日付）が別の元から2回入らないように
        keys = {(x["n"], x["d"]) for x in items}
        a = [x for x in a if (x["n"], x["d"]) not in keys]
        items += a
        got[nm] = len(a)
    data["items"] = items
    json.dump(data, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(seen, open(SEEN, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(json.dumps({"region": REGION, "added": got, "total": len(items)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
