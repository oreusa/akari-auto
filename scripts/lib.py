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


def buffer_create(channel_id, service, thread, due_utc, topic=None, draft=False):
    """thread = [文1, 文2, ...]。1つ目がそのまま投稿、2つ目以降は続き（スレッド）。"""
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
    inp = {
        "channelId": channel_id,
        "text": thread[0],
        "schedulingType": "automatic",
        "mode": "customScheduled",
        "dueAt": due_utc,
        "metadata": {k: v for k, v in meta.items() if v} or None,
        "source": "akari-auto",
    }
    if draft:
        inp["saveToDraft"] = True
    if inp["metadata"] is None:
        del inp["metadata"]
    res = buffer_gql(CREATE_POST, {"input": inp})["createPost"]
    if res["__typename"] != "PostActionSuccess":
        raise BufferError(f"{res['__typename']}: {res.get('message', '')}")
    return res["post"]


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


def rakuten_travel_link(hotel_no):
    """楽天トラベルの施設ページへのアフィリエイトリンクを作り、施設ページが開けるか確かめる。"""
    env = rakuten_env()
    page = f"https://travel.rakuten.co.jp/HOTEL/{int(hotel_no)}/"
    status, txt, final = http("GET", page)
    if status != 200 or "お探しのページは見つかりません" in txt:
        return {"ok": False, "why": f"施設ページが開けない（{status}）"}
    enc = urllib.parse.quote(page, safe="")
    link = f"https://hb.afl.rakuten.co.jp/hgc/{env['RAKUTEN_AFFILIATE_ID']}/?pc={enc}&m={enc}"
    title = re.search(r"<title>(.*?)</title>", txt, re.S)
    return {"ok": True, "name": (title.group(1).strip() if title else ""), "itemUrl": page, "link": link}


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
