"""予定表（schedule/日付.json）の機械チェック。

燈が書いた予定表が決まりを守っているかを確かめる。守っていない投稿は予約しない（代わりの投稿を出す）。
使い方：python scripts/check.py schedule/2026-10-24.json  （引数なしなら schedule/ の全部）
"""
import glob
import os
import re
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import amazon_checked, load_json, now_jst, path, threads_len, x_weight  # noqa: E402

LINK = "{{LINK}}"
BANNED = [
    (re.compile(r"amazon\.co\.jp|amzn\.(to|asia)", re.I), "AmazonのURLを直接書かない（{{LINK}} と書き、link に type amazon と asin を入れる）"),
    (re.compile(r"a\.r10\.to", re.I), "楽天の短縮リンクは使わない（リンクは予約係が楽天から受け取る）"),
    (re.compile(r"hb\.afl\.rakuten|px\.a8\.net", re.I), "アフィリエイトリンクを直接書かない（{{LINK}} と書き、link に入れる）"),
]
ASOF_RE = re.compile(r"(\d{1,2})/(\d{1,2})時点")
SLOT_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def _texts_problems(texts, where, allow_link):
    out = []
    if not isinstance(texts, list) or not texts or not all(isinstance(t, str) and t.strip() for t in texts):
        return [f"{where}：文が空か、形が違う（[\"1つ目\", \"2つ目\"] の形）"]
    for i, t in enumerate(texts, 1):
        for rx, why in BANNED:
            if rx.search(t):
                out.append(f"{where} {i}つ目：{why}")
        if i == 1 and len(texts) > 1 and (LINK in t or re.search(r"https?://", t)):
            out.append(f"{where} 1つ目：URLは入れない（リンクは2つ目だけ。同じリンクが2回出るのを防ぐ）")
        if LINK in t and not allow_link:
            out.append(f"{where} {i}つ目：{{{{LINK}}}} があるのに link の指定がない（代わりの投稿には使えない）")
        probe = t.replace(LINK, "https://hb.afl.rakuten.co.jp/x")
        if where.startswith("x") and x_weight(probe) > 280:
            out.append(f"{where} {i}つ目：Xの文字数 {x_weight(probe)}/280")
        if where.startswith("threads") and threads_len(probe) > 500:
            out.append(f"{where} {i}つ目：Threadsの文字数 {threads_len(probe)}/500")
    return out


def _head(texts):
    if isinstance(texts, list) and texts and isinstance(texts[0], str) and texts[0].strip():
        return texts[0].strip().splitlines()[0].strip()
    return None


def _same_head(p, where=""):
    hx, ht = _head(p.get("x")), _head(p.get("threads"))
    out = []
    for h in (hx, ht):
        if p.get("link") and h is not None and not h.startswith("【AIが比べた"):
            out.append(f"{where}PRの1行目が「【AIが比べた」で始まっていない（PRの見出しはこの形。10/23 オーナー）")
            break
    if hx is not None and ht is not None and hx != ht:
        out.append(f"{where}XとThreadsで1行目の見出しが違う（見出しと題材は同じにし、長さだけ変える）")
    return out


def post_problems(p):
    out = []
    slot = p.get("slot", "")
    if not SLOT_RE.match(slot):
        out.append(f"slot「{slot}」が HH:MM でない")
    link = p.get("link")
    if link:
        t = link.get("type")
        if t == "ichiba" and not str(link.get("url", "")).startswith("https://item.rakuten.co.jp/"):
            out.append("link.url は楽天市場の商品ページ（https://item.rakuten.co.jp/…）")
        elif t == "travel" and not str(link.get("hotelNo", "")).isdigit():
            out.append("link.hotelNo は楽天トラベルの施設番号（数字）")
        elif t == "a8" and not str(link.get("url", "")).startswith("https://px.a8.net/svt/ejp?a8mat="):
            out.append("link.url はA8のリンク（https://px.a8.net/svt/ejp?a8mat=…。リンク帳にある物だけ）")
        elif t == "amazon":
            asin = str(link.get("asin", "")).upper()
            if not re.match(r"^[A-Z0-9]{10}$", asin):
                out.append("link.asin はAmazonのASIN（英数字10けた）")
            elif asin not in amazon_checked():
                out.append(f"Amazonの {asin} は data/amazon-checked.json にない（凪がブラウザで確かめた物だけ使う）")
        elif t not in ("ichiba", "travel", "a8", "amazon"):
            out.append("link.type は ichiba・travel・a8・amazon のどれか")
    for ch in ("x", "threads"):
        out += _texts_problems(p.get(ch), ch, bool(link))
        texts = p.get(ch) or []
        if link and isinstance(texts, list):
            joined = "\n".join(texts)
            if LINK not in joined:
                out.append(f"{ch}：link があるのに文に {{{{LINK}}}} がない")
            first_last = texts[0].strip().splitlines()[-1] if texts and texts[0].strip() else ""
            if "#PR" not in first_last:
                out.append(f"{ch}：PRなのに1つ目の最後の行に #PR がない")
            if texts and isinstance(texts[0], str) and "選んだ理由：" not in texts[0]:
                out.append(f"{ch}：PRの1つ目に「選んだ理由：」の1行がない（何をいくつ比べ、どの数字で選んだか）")
            for i, t in enumerate(texts, 1):
                if LINK in t and "#PR" not in t:
                    out.append(f"{ch} {i}つ目：リンクがある投稿に #PR がない")
    out += _same_head(p)
    if not p.get("topic"):
        out.append("topic（Threadsのトピック）がない")
    if link or p.get("until"):
        fb = p.get("fallback")
        if not fb:
            out.append("PRか期限つきなのに fallback（代わりの通常投稿）がない")
        else:
            out += ["fallback " + s for s in _texts_problems(fb.get("x"), "x", False)]
            out += ["fallback " + s for s in _texts_problems(fb.get("threads"), "threads", False)]
            out += _same_head(fb, "fallback ")
    return out


def check_file(fp):
    data = load_json(fp)
    probs = []
    if not data or "posts" not in data:
        return [f"{fp}: 読めない、または posts がない"]
    slots = [p.get("slot") for p in data["posts"]]
    for s in set(slots):
        if slots.count(s) > 1:
            probs.append(f"{fp}: 同じ時刻 {s} が2つある")
    try:
        d = date.fromisoformat(data.get("date", ""))
    except ValueError:
        return probs + [f"{fp}: date が YYYY-MM-DD でない"]
    room_urls = {str(r.get("url", "")).split("?")[0].rstrip("/") for r in (data.get("room") or []) if isinstance(r, dict)}
    for p in data["posts"]:
        lk = p.get("link") or {}
        if lk.get("type") == "ichiba" and str(lk.get("url", "")).split("?")[0].rstrip("/") not in room_urls:
            probs.append(f"{fp} {p.get('slot')}: PRで選んだ楽天市場の商品が room にない（PRの商品は必ずROOMにも載せる。10/22 オーナー）")
    for p in data["posts"]:
        for pr in post_problems(p) + asof_problems(p, d):
            probs.append(f"{fp} {p.get('slot', '?')}: {pr}")
    for i, it in enumerate(data.get("room") or [], 1):
        if not str(it.get("url", "")).startswith("https://item.rakuten.co.jp/") or not it.get("expect") or not it.get("comment"):
            probs.append(f"{fp} ROOM {i}件目: url（楽天市場の商品ページ）・expect・comment が要る")
    return probs


def asof_problems(p, d):
    """出どころの「（M/D時点）」が投稿の日から7日より古くないか。1つ目の文には必ず要る。"""
    out = []
    for name, texts in (("x", p.get("x")), ("threads", p.get("threads"))):
        if not isinstance(texts, list) or not texts:
            continue
        found = [m for t in texts for m in ASOF_RE.finditer(t)]
        if not found:
            out.append(f"{name}：出どころの「（M/D時点）」がない")
        for m in found:
            mo, da = int(m.group(1)), int(m.group(2))
            try:
                when = date(d.year if mo <= d.month else d.year - 1, mo, da)
            except ValueError:
                out.append(f"{name}：「{m.group(0)}」の日付がおかしい")
                continue
            if when > d or d - when > timedelta(days=7):
                out.append(f"{name}：出どころが{m.group(0)}で古い（投稿の日から7日以内）")
    return out


def online_problems(fp):
    """楽天に聞いて、PRとROOMの商品を前の夜のうちに確かめる（キーがあるときだけ）。"""
    import book
    from lib import item_code_from_url, missing_specs, rakuten_item
    data = load_json(fp) or {}
    try:
        if date.fromisoformat(data.get("date", "")) < now_jst().date():
            return []
    except ValueError:
        return []
    out = []
    for p in data.get("posts", []):
        link = p.get("link")
        if link:
            r = book.resolve_link(link, list(p.get("x", [])) + list(p.get("threads", [])))
            if not r.get("ok"):
                out.append(f"{fp} {p.get('slot')}: PRの商品が×：{r.get('why', '')}")
            else:
                print(f"  {p.get('slot')} PR OK：{r.get('name', '')[:40]}")
        for texts in (p.get("x", []), p.get("threads", [])):
            prob = book.source_problem(texts)
            if prob:
                out.append(f"{fp} {p.get('slot')}: {prob}")
                break
    for i, it in enumerate(data.get("room") or [], 1):
        code = item_code_from_url(it.get("url", ""))
        r = rakuten_item(code, it.get("expect")) if code else {"ok": False, "why": "商品ページのURLではない"}
        if r.get("ok") and it.get("expect") not in r.get("name", ""):
            r = {"ok": False, "why": f"商品名に「{it.get('expect')}」がない"}
        if r.get("ok"):
            miss = missing_specs([it.get("comment", "")], r.get("name", ""), r.get("caption", ""))
            if miss:
                r = {"ok": False, "why": "コメントの数字が商品ページにない: " + "・".join(miss[:4])}
        if r.get("ok") and (r.get("reviewAverage") or 0) < 4.0:
            r = {"ok": False, "why": f"レビュー平均 {r.get('reviewAverage')}（4.0未満）"}
        if not r.get("ok"):
            out.append(f"{fp} ROOM {i}件目：{r.get('why', '')}")
        else:
            print(f"  ROOM {i} OK：{r.get('name', '')[:40]}")
    return out


def main(argv):
    online = "--online" in argv
    argv = [a for a in argv if a != "--online"]
    files = argv[1:] or sorted(glob.glob(path("schedule", "*.json")))
    if not argv[1:]:
        today = now_jst().date().isoformat()
        files = [f for f in files if os.path.basename(f)[:10] >= today]  # 過ぎた日は見ない
    allp = []
    for fp in files:
        allp += check_file(fp)
        if online and os.environ.get("RAKUTEN_APP_ID"):
            allp += online_problems(fp)
    for p in allp:
        print("×", p)
    if not allp:
        print(f"OK（{len(files)}ファイル）")
    return 1 if allp else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
