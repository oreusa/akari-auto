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
            return e.code, txt, url
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
