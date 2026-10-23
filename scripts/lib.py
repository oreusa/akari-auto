"""燈の自動係で共通に使う部品（Buffer・楽天・文字数・ファイル）。

外部のライブラリは使わない（GitHub Actions の Python だけで動く）。
キーは GitHub の「秘密の値（Secrets）」から環境変数で受け取り、ファイルや記録には書かない。
"""
import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "akari-auto/1.0 (+https://github.com/oreusa/akari-auto)"


def now_jst():
    return datetime.now(JST)


def path(*parts):
    return os.path.join(ROOT, *parts)


def load_json(p, default=None):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save_json(p, data):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def append_log(day, line):
    """人が読む記録。燈は毎晩これを読んで、実際に何が出たかを知る。"""
    p = path("log", f"{day}.md")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    stamp = now_jst().strftime("%H:%M")
    with open(p, "a", encoding="utf-8") as f:
        f.write(f"- {stamp} {line}\n")
    print(line)


# ---------------------------------------------------------------- 文字数

URL_RE = re.compile(r"https?://\S+")


def x_weight(text):
    """X の数え方：URLは23、半角や一部の記号は1、それ以外（日本語など）は2。上限280。"""
    total = 0
    rest = URL_RE.sub(lambda m: "\x00", text)
    total += 23 * rest.count("\x00")
    for ch in unicodedata.normalize("NFC", rest.replace("\x00", "")):
        cp = ord(ch)
        if (0 <= cp <= 4351 or 8192 <= cp <= 8205 or 8208 <= cp <= 8223
                or 8242 <= cp <= 8247):
            total += 1
        else:
            total += 2
    return total


def threads_len(text):
    return len(text)


# ---------------------------------------------------------------- HTTP

def http(method, url, headers=None, body=None, timeout=30, retries=3):
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    last = None
    for i in range(retries):
        req = urllib.request.Request(url, data=data, method=method,
                                     headers={"User-Agent": UA, **(headers or {})})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.read().decode("utf-8", "replace"), r.geturl()
        except urllib.error.HTTPError as e:
            txt = e.read().decode("utf-8", "replace")
            if e.code in (429, 500, 502, 503, 504) and i < retries - 1:
                time.sleep(2 ** (i + 1))
                last = (e.code, txt, url)
                continue
            return e.code, txt, (e.geturl() if hasattr(e, "geturl") else None) or url
        except Exception as e:  # 通信の一時的な失敗
            last = (0, str(e), url)
            if i < retries - 1:
                time.sleep(2 ** (i + 1))
    return last


# ---------------------------------------------------------------- Buffer

BUFFER_URL = "https://api.buffer.com"


class BufferError(Exception):
    pass


def http_raw(url, timeout=60):
    """中身を文字にせずに受け取る（絵・動画のURLの確かめ用）。戻り値：(状態, 中身の頭, 最後のURL)"""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(4096), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, b"", url


def buffer_gql(query, variables=None):
    key = os.environ.get("BUFFER_API_KEY")
    if not key:
        raise BufferError("BUFFER_API_KEY がありません（GitHub の Secrets に入れてください）")
    key = key.strip()
    if not key.isascii() or " " in key:
        raise BufferError(f"BUFFER_API_KEY の中身がキーではありません（日本語や空白が入っています。{len(key)}文字）。"
                          "Bufferでキーを作り直して、Secretを入れ直してください")
    status, txt, _ = http("POST", BUFFER_URL,
                          headers={"Authorization": f"Bearer {key}",
                                   "Content-Type": "application/json"},
                          body={"query": query, "variables": variables or {}})
    try:
        data = json.loads(txt)
    except Exception:
        raise BufferError(f"Buffer の返事が読めません（{status}）: {txt[:200]}")
    if data.get("errors"):
        raise BufferError("Buffer: " + "; ".join(e.get("message", "") for e in data["errors"])[:300])
    return data["data"]


CREATE_POST = """
mutation($input: CreatePostInput!) {
  createPost(input: $input) {
    __typename
    ... on PostActionSuccess { post { id status dueAt } }
    ... on MutationError { message }
  }
}
"""


def buffer_create(channel_id, service, thread, due_utc, topic=None, draft=False, image=None, video=None, alt="",
                  images=None, ig_type=None):
    """thread = [文1, 文2, ...]。1つ目がそのまま投稿、2つ目以降は続き（スレッド）。

    image / video は誰でも開けるURL（Bufferが取りに行く）。付けたときは「AIで作った」の表示もONにする。
    images は絵のURLの並び（Instagramのスライド＝カルーセル）。
    Instagram は ig_type（post / story / reel）。なければ video があればリール、なければ画像の投稿。"""
    items = [{"text": t} for t in thread]
    meta = {}
    if service == "twitter":
        meta["twitter"] = {"thread": items} if len(items) > 1 else {}
    elif service == "threads":
        m = {"type": "post"}
        if len(items) > 1:
            m["thread"] = items
        if topic:
            m["topic"] = topic
        meta["threads"] = m
    elif service == "instagram":
        t = ig_type or ("reel" if video else "post")
        meta["instagram"] = {"type": t, "shouldShareToFeed": t != "story", "isAiGenerated": True}
    if (image or video or images) and service == "twitter":
        meta["twitter"]["isAiGenerated"] = True
    inp = {
        "channelId": channel_id,
        "text": thread[0],
        "schedulingType": "automatic",
        "mode": "customScheduled",
        "dueAt": due_utc,
        "metadata": {k: v for k, v in meta.items() if v} or None,
        "source": "akari-auto",
    }
    if video and service == "instagram":
        inp["assets"] = [{"video": {"url": video}}]
    elif images:
        inp["assets"] = [{"image": {"url": u, "metadata": {"altText": alt or "4コマ漫画"}}} for u in images]
    elif image:
        inp["assets"] = [{"image": {"url": image, "metadata": {"altText": alt or "4コマ漫画"}}}]
    if draft:
        inp["saveToDraft"] = True
    if inp["metadata"] is None:
        del inp["metadata"]
    res = buffer_gql(CREATE_POST, {"input": inp})["createPost"]
    if res["__typename"] != "PostActionSuccess":
        raise BufferError(f"{res['__typename']}: {res.get('message', '')}")
    return res["post"]


# ---------------------------------------------------------------- 4コマを切る（Instagram用）

KOMA4_SPEC = (724, 2172)  # 全体の大きさ（オーナー確定）。各コマ 709x512、間隔10
KOMA4_PANEL = (709, 512)


def koma4_boxes(img):
    """4コマの絵（Pillowの画像）から、4つのコマの位置 (左, 上, 幅, 高さ) を探す。
    白い行で区切られた、高さ350〜700の塊がちょうど4つならそれを使う。違えば決まりの大きさから出す。"""
    w, h = img.size
    g = img.convert("L")
    xs = range(min(100, w // 4), max(w - 100, w * 3 // 4), 4)
    white = [sum(g.getpixel((x, y)) for x in xs) / len(xs) > 245 for y in range(h)]
    runs, y = [], 0
    while y < h:
        if white[y]:
            y += 1
            continue
        y0 = y
        while y < h and not white[y]:
            y += 1
        if 350 <= y - y0 <= 700:
            runs.append((y0, y))
    if len(runs) == 4:
        boxes = []
        for y0, y1 in runs:
            ym = (y0 + y1) // 2
            cols = [x for x in range(w) if g.getpixel((x, ym)) < 245]
            x0, x1 = (cols[0], cols[-1] + 1) if cols else ((w - KOMA4_PANEL[0]) // 2, (w + KOMA4_PANEL[0]) // 2)
            boxes.append((x0, y0, x1 - x0, y1 - y0))
        ph = round(KOMA4_PANEL[1] * h / KOMA4_SPEC[1])
        if all(abs(bh - ph) <= 12 for _, _, _, bh in boxes):  # コマの下の白い縁で数pxずれるので、決まりの高さにそろえる
            boxes = [(x, y, bw, ph) for x, y, bw, _ in boxes]
        return boxes, "見つけた"
    pw, ph = KOMA4_PANEL
    sx, sy = w / KOMA4_SPEC[0], h / KOMA4_SPEC[1]
    x0 = round((w - pw * sx) / 2)
    bottom = h - 13 * sy  # 第16話の絵で下の余白は13px
    boxes = [(x0, round(bottom - ((ph + 10) * (3 - i) + ph) * sy), round(pw * sx), round(ph * sy)) for i in range(4)]
    return boxes, "決まりの位置"


def wsrv_url(src, box, size=None):
    """絵の一部を切り出したURL（wsrv.nl が切って返す。Bufferはこれを取りに行く）。
    size=(幅, 高さ) なら、その大きさの白い台紙の真ん中に置く（ストーリー用 1080x1920）。"""
    x, y, bw, bh = box
    q = {"url": src, "cx": x, "cy": y, "cw": bw, "ch": bh, "output": "jpg", "q": 92}
    if size:
        q.update({"w": size[0], "h": size[1], "fit": "contain", "cbg": "white"})
    return "https://wsrv.nl/?" + urllib.parse.urlencode(q)


def koma4_instagram_media(src, img):
    """Instagram用：スライド4枚（1コマずつ）と、ストーリー2枚（2コマずつ・9:16）。"""
    boxes, how = koma4_boxes(img)
    slides = [wsrv_url(src, b) for b in boxes]
    stories = []
    for a, b in ((0, 1), (2, 3)):
        x0, y0 = min(boxes[a][0], boxes[b][0]), boxes[a][1]
        x1 = max(boxes[a][0] + boxes[a][2], boxes[b][0] + boxes[b][2])
        y1 = boxes[b][1] + boxes[b][3]
        stories.append(wsrv_url(src, (x0, y0, x1 - x0, y1 - y0), (1080, 1920)))
    return {"slides": slides, "stories": stories, "how": how, "boxes": boxes}


def fetch_image(url, timeout=60):
    """絵をまるごと受け取って Pillow の画像にする。"""
    from io import BytesIO
    from PIL import Image
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return Image.open(BytesIO(r.read()))


# ---------------------------------------------------------------- 楽天

RAKUTEN_ITEM_URL = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"


def rakuten_env():
    need = ["RAKUTEN_APP_ID", "RAKUTEN_ACCESS_KEY", "RAKUTEN_AFFILIATE_ID"]
    miss = [k for k in need if not os.environ.get(k)]
    if miss:
        raise RuntimeError("楽天のキーがありません: " + ", ".join(miss))
    return {k: os.environ[k] for k in need}


def _rakuten_search(params):
    env = rakuten_env()
    base = {
        "format": "json", "formatVersion": 2,
        "applicationId": env["RAKUTEN_APP_ID"],
        "accessKey": env["RAKUTEN_ACCESS_KEY"],
        "affiliateId": env["RAKUTEN_AFFILIATE_ID"],
    }
    base.update(params)
    origin = os.environ.get("RAKUTEN_ORIGIN") or "https://github.com"  # 空のときも github.com
    url = RAKUTEN_ITEM_URL + "?" + urllib.parse.urlencode(base)
    status, txt, _ = http("GET", url, headers={"Origin": origin, "Referer": origin + "/"})
    if status != 200:
        return None, f"楽天API {status}: {txt[:150]}"
    items = json.loads(txt).get("Items") or []
    return [it.get("Item", it) for it in items], ""


def _plain_url(it):
    """アフィリエイトIDつきで聞くと itemUrl もリンクの形で返るので、中の商品ページURLを取り出す。"""
    u = (it.get("itemUrl") or "") + "/"
    for _ in range(2):
        u = urllib.parse.unquote(u)
    return u


def _item_image(it):
    """商品の写真のURL（楽天の画像サーバー）。大きめ（300px）で返す。無ければ空。"""
    imgs = it.get("mediumImageUrls") or it.get("smallImageUrls") or []
    u = imgs[0] if imgs else ""
    if isinstance(u, dict):
        u = u.get("imageUrl", "")
    return re.sub(r"\?_ex=\d+x\d+$", "", u) + "?_ex=300x300" if u else ""


def rakuten_item(item_code, keyword=None):
    """楽天市場の商品を1つ確かめる。返すもの：販売中か・商品名・レビュー・正式なアフィリエイトリンク。

    item_code は「お店のID:商品のID」（例 low-ya:vg-groony）。
    商品ページのURL https://item.rakuten.co.jp/お店/商品/ からも作れる。
    楽天が item_code を受け付けないときは、お店の中を keyword で探し、商品ページのURLが同じ物を選ぶ。
    """
    env = rakuten_env()
    items, err = _rakuten_search({"itemCode": item_code, "hits": 1})
    if items is None and "itemCode" in err:
        shop, _, slug = item_code.partition(":")
        items, err2 = _rakuten_search({"shopCode": shop, "keyword": keyword or slug, "hits": 30})
        if items is None:
            return {"ok": False, "why": err2}
        want = f"/{shop}/{slug}/"
        found = items
        items = [it for it in items if want in _plain_url(it)]
        if not items:
            seen = "; ".join(f"{it.get('itemCode')} {(it.get('itemUrl') or '')[:60]}" for it in found[:5])
            return {"ok": False, "why": f"お店の中で同じ商品ページが見つからない（{len(found)}件中）: {seen}"}
    elif items is None:
        return {"ok": False, "why": err}
    if not items:
        return {"ok": False, "why": "商品が見つからない（販売終了かも）"}
    it = items[0]
    aff = it.get("affiliateUrl") or ""
    res = {
        "ok": bool(it.get("availability") == 1 and aff),
        "name": it.get("itemName", ""),
        "code": it.get("itemCode"),
        "price": it.get("itemPrice"),
        "reviewCount": it.get("reviewCount"),
        "reviewAverage": it.get("reviewAverage"),
        "itemUrl": _plain_url(it).rstrip("/") + "/",
        "caption": it.get("itemCaption") or "",
        "link": aff,
        "image": _item_image(it),
    }
    if it.get("availability") != 1:
        res["why"] = "売り切れ・販売停止"
    elif not aff.startswith("https://hb.afl.rakuten.co.jp/"):
        # 楽天は affiliateId を渡したときだけ affiliateUrl を返す（IDは g00… の形に変えて入る）
        res["ok"] = False
        res["why"] = "楽天のアフィリエイトリンクの形ではない"
    return res


def item_code_from_url(url):
    m = re.match(r"https?://item\.rakuten\.co\.jp/([^/]+)/([^/?#]+)", url)
    return f"{m.group(1)}:{m.group(2)}" if m else None


RAKUTEN_HOTEL_URL = "https://openapi.rakuten.co.jp/engine/api/Travel/HotelDetailSearch/20170426"


def _hotel_info(data):
    """楽天トラベルAPIの返事から hotelBasicInfo を1つ取り出す（入れ子の形が版で違うので探して取る）。"""
    if isinstance(data, dict):
        if "hotelBasicInfo" in data:
            return data["hotelBasicInfo"]
        if "hotelNo" in data and "hotelName" in data:
            return data
        vals = data.values()
    elif isinstance(data, list):
        vals = data
    else:
        return None
    for v in vals:
        r = _hotel_info(v)
        if r:
            return r
    return None


def rakuten_travel_api(hotel_no):
    """楽天トラベルの施設を楽天API（HotelDetailSearch）で確かめる。

    楽天トラベルのページは GitHub の機械からは全部 503 になる（10/23 probe で確認）ので、APIで確かめる。
    """
    env = rakuten_env()
    params = {
        "format": "json", "formatVersion": 2, "hotelNo": int(hotel_no),
        "applicationId": env["RAKUTEN_APP_ID"], "accessKey": env["RAKUTEN_ACCESS_KEY"],
        "affiliateId": env["RAKUTEN_AFFILIATE_ID"],
    }
    origin = os.environ.get("RAKUTEN_ORIGIN") or "https://github.com"
    status, txt, _ = http("GET", RAKUTEN_HOTEL_URL + "?" + urllib.parse.urlencode(params),
                          headers={"Origin": origin, "Referer": origin + "/"})
    if status == 404 and "not_found" in (txt or ""):
        return {"ok": False, "why": "楽天トラベルに施設がない（掲載終了かも）"}
    if status != 200:
        return {"ok": False, "why": f"楽天トラベルAPI {status}: {(txt or '')[:120]}"}
    info = _hotel_info(json.loads(txt))
    if not info or str(info.get("hotelNo")) != str(int(hotel_no)):
        return {"ok": False, "why": "楽天トラベルAPIの返事に施設がない"}
    return info


def rakuten_travel_link(hotel_no):
    """楽天トラベルの施設へのアフィリエイトリンクを作り、施設が載っているか楽天APIで確かめる。"""
    env = rakuten_env()
    info = rakuten_travel_api(hotel_no)
    if info.get("ok") is False:
        return info
    page = f"https://travel.rakuten.co.jp/HOTEL/{int(hotel_no)}/"
    enc = urllib.parse.quote(page, safe="")
    link = f"https://hb.afl.rakuten.co.jp/hgc/{env['RAKUTEN_AFFILIATE_ID']}/?pc={enc}&m={enc}"
    res = {"ok": True, "name": info.get("hotelName", ""), "itemUrl": page, "link": link,
           "image": info.get("hotelImageUrl") or info.get("hotelThumbnailUrl") or "",
           "reviewCount": info.get("reviewCount"), "reviewAverage": info.get("reviewAverage")}
    return res


# ---------------------------------------------------------------- 数字・ページの確かめ

SPEC_RE = re.compile(r"(\d[\d,.]*)\s*(cm|mm|kg|g|W|L|mAh|ml|mL|畳)(?![a-zA-Z])")


def _norm(t):
    return unicodedata.normalize("NFKC", t or "").replace(",", "").replace(" ", "").lower()


def spec_numbers(texts):
    """PRの文に出てくる「数字＋単位」（例 140cm・3.2L・45W）を取り出す。値段と日付は入れない。"""
    out = []
    for t in texts:
        for m in SPEC_RE.finditer(unicodedata.normalize("NFKC", t)):
            tok = (m.group(1).replace(",", "") + m.group(2)).lower()
            if tok not in out:
                out.append(tok)
    return out


ALL_RE = re.compile(r"どちらも|いずれも|すべて|全部|[2-9２-９]つとも|[2-9２-９]台とも|[2-9２-９]枚とも")


def about_item(texts, expect):
    """比べる投稿では、選んだ商品（expect が入る行）と「どちらも」などの行だけを、その商品の数字として見る。"""
    if not expect:
        return list(texts)
    out = []
    for t in texts:
        for line in t.splitlines():
            if expect in line or ALL_RE.search(line):
                out.append(line)
    return out


def missing_specs(texts, *sources):
    """文の「数字＋単位」のうち、商品名・商品説明のどこにも無いものを返す（大きさの書き違いを止める）。"""
    src = "".join(_norm(s) for s in sources)
    return [tok for tok in spec_numbers(texts) if tok not in src]


END_WORDS = ["このイベントは終了しました", "イベントは終了しました", "開催は終了しました", "受付は終了しました",
             "受付を終了しました", "販売を終了しました", "販売は終了しました", "キャンペーンは終了しました",
             "本キャンペーンは終了", "公開を終了しました", "掲載は終了しました", "お探しのページは見つかりません",
             "ページが見つかりません", "404 Not Found"]


def page_check(url):
    """出どころのページが開けるか、「終了」「ページがない」と出ていないかを確かめる。

    返すもの：("ok"|"dead"|"ended"|"unknown", 説明)。unknown は開けなかった（時間切れなど）。止めはしない。
    """
    status, txt, final = http("GET", url, headers={"Accept-Language": "ja-JP,ja;q=0.9", "Accept": "text/html"},
                              timeout=20, retries=2)
    if status in (404, 410):
        return "dead", f"ページがない（{status}）"
    if status != 200:
        return "unknown", f"開けない（{status}）"
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", txt, flags=re.S)
    for w in END_WORDS:
        if w in body:
            return "ended", f"ページに「{w}」"
    return "ok", ""


# ---------------------------------------------------------------- Buffer：出たかどうか

SENT_Q = """query($o: OrganizationId!, $ch: [ChannelId!], $s: DateTime, $e: DateTime) {
  posts(first: 50, input: {organizationId: $o,
        filter: {channelIds: $ch, status: [STATUSES], dueAt: {start: $s, end: $e}}}) {
    edges { node { id channelService dueAt status text } } } }"""


def buffer_posts(cfg, statuses, start, end, channel_ids=None):
    q = SENT_Q.replace("STATUSES", ", ".join(statuses))
    d = buffer_gql(q, {"o": cfg["organizationId"], "ch": channel_ids or list(cfg["channels"].values()),
                            "s": start.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
                            "e": end.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")})
    return [e["node"] for e in (d["posts"]["edges"] or [])]


# ---------------------------------------------------------------- A8

BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
JP2 = ("co.jp", "ne.jp", "or.jp", "ac.jp", "go.jp", "ed.jp", "lg.jp", "gr.jp")


def base_domain(host):
    """www.nta.co.jp → nta.co.jp、shop.example.com → example.com"""
    h = (host or "").lower().split(":")[0].strip(".")
    parts = h.split(".")
    n = 3 if any(h.endswith("." + x) for x in JP2) else 2
    return ".".join(parts[-n:])


def a8_link(url, expect_host):
    """A8のリンク（https://px.a8.net/svt/ejp?a8mat=…）を開き、広告主のページに着くかを確かめる。
    広告主の側でロボット確認（202・403）が出ても、広告主のドメインに着いていれば着いたとみなす。
    A8が一時的に403を返すことがあるので、ブラウザの名乗りで間をあけてもう1回試す。"""
    if not re.match(r"^https://px\.a8\.net/svt/ejp\?a8mat=[0-9A-Za-z+]+$", url or ""):
        return {"ok": False, "why": "A8のリンクの形ではない（https://px.a8.net/svt/ejp?a8mat=…）"}
    why = "A8のリンク先が開けない"
    for i, ua in enumerate((None, BROWSER_UA, BROWSER_UA)):
        if i:
            time.sleep(4 * i)
        h = {"Accept-Language": "ja-JP,ja;q=0.9", "Accept": "text/html"}
        if ua:
            h["User-Agent"] = ua
        status, txt, final = http("GET", url, headers=h, timeout=25, retries=2)
        host = urllib.parse.urlparse(final or "").netloc
        if not status or "a8.net" in host or not host:
            why = f"A8のリンクが広告主のページに着かない（{status}。提携切れ・終了か、A8の一時的な拒否）"
            continue
        if expect_host and base_domain(expect_host) != base_domain(host):
            return {"ok": False, "why": f"A8のリンク先が {host}（{expect_host} ではない）"}
        if status >= 500 or status in (404, 410):
            why = f"広告主のページが開けない（{status}）"
            continue
        break
    else:
        return {"ok": False, "why": why}
    title = re.search(r"<title[^>]*>(.*?)</title>", txt or "", re.S)
    return {"ok": True, "name": title.group(1).strip()[:60] if title else host, "itemUrl": final, "link": url}


# ---- Amazon（10/23 オーナー「Amazonも使おう」）----
# 機械からはAmazonの商品ページが開けない（「ショッピングを続ける」の画面で止まる）。
# そこで、凪（ChatGPT）が前の晩にブラウザで開いて確かめた物（ドライブ「Amazon確認帳」→ 燈が data/amazon-checked.json に写す）だけを使う。
AMAZON_TAG = os.environ.get("AMAZON_TAG", "aiusagichan-22")
AMAZON_CHECKED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "amazon-checked.json")
AMAZON_MAX_AGE_H = 36


def amazon_checked(path=None):
    try:
        with open(path or AMAZON_CHECKED, encoding="utf-8") as f:
            return (json.load(f) or {}).get("items", {})
    except (OSError, ValueError):
        return {}


def amazon_link(asin, expect="", now=None, items=None):
    """凪が確かめた Amazon の商品だけ合格にして、うちのタグ付きリンクを返す。"""
    asin = str(asin or "").strip().upper()
    if not re.match(r"^[A-Z0-9]{10}$", asin):
        return {"ok": False, "why": "ASIN の形ではない（英数字10けた）"}
    it = (items if items is not None else amazon_checked()).get(asin)
    if not it:
        return {"ok": False, "why": "Amazon確認帳にない（凪がブラウザで確かめていない）"}
    now = now or datetime.now(JST)
    try:
        at = datetime.fromisoformat(str(it.get("checkedAt")))
        if at.tzinfo is None:
            at = at.replace(tzinfo=JST)
    except ValueError:
        return {"ok": False, "why": "Amazon確認帳の確認時刻が読めない"}
    if now - at > timedelta(hours=AMAZON_MAX_AGE_H):
        return {"ok": False, "why": f"Amazon確認帳の確認が古い（{AMAZON_MAX_AGE_H}時間より前）"}
    if it.get("ok") is False:
        return {"ok": False, "why": "凪の確認で×（ページ切れ・在庫なしなど）"}
    name = str(it.get("name", ""))
    if expect and expect not in name:
        return {"ok": False, "why": f"商品名に「{expect}」がない（別の商品の可能性）: {name[:40]}"}
    try:
        rv, st = int(it.get("reviews") or 0), float(it.get("stars") or 0)
    except (TypeError, ValueError):
        rv, st = 0, 0.0
    if rv < 1000 or st < 4.0:
        return {"ok": False, "why": f"厳選の条件に届かない（レビュー{rv}件・★{st}。1,000件以上・4.0以上）"}
    page = f"https://www.amazon.co.jp/dp/{asin}"
    # 開けたときだけ、ページ切れの文字を見る（止められる画面なら凪の確認を信じる）
    status, txt, _ = http("GET", page, headers={"User-Agent": BROWSER_UA, "Accept-Language": "ja-JP,ja;q=0.9"}, timeout=20, retries=1)
    if status in (404, 410) or (txt and "有効なページではありません" in txt):
        return {"ok": False, "why": f"Amazonの商品ページがない（{status}）"}
    return {"ok": True, "name": name, "reviewCount": rv, "reviewAverage": st, "price": it.get("price"),
            "itemUrl": page, "link": f"{page}?tag={AMAZON_TAG}", "caption": str(it.get("specs", ""))}
