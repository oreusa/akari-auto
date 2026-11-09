"""予定表（schedule/日付.json）の機械チェック。

燈が書いた予定表が決まりを守っているかを確かめる。守っていない投稿は予約しない（代わりの投稿を出す）。
使い方：python scripts/check.py schedule/2026-10-24.json  （引数なしなら schedule/ の全部）
"""
import glob
import os
import re
import urllib.parse
import sys
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import amazon_checked, load_json, now_jst, path, threads_len, x_weight  # noqa: E402

LINK = "{{LINK}}"
AFL_LONG = "https://hb.afl.rakuten.co.jp/" + "x" * 252  # 楽天のアフィリエイトリンクは rafcid 付きで約270字（10/30 9:15 は268字で500字を超えた）
BANNED = [
    (re.compile(r"amazon\.co\.jp|amzn\.(to|asia)", re.I), "AmazonのURLを直接書かない（{{LINK}} と書き、link に type amazon と asin を入れる）"),
    (re.compile(r"a\.r10\.to", re.I), "楽天の短縮リンクは使わない（リンクは予約係が楽天から受け取る）"),
    (re.compile(r"hb\.afl\.rakuten|px\.a8\.net", re.I), "アフィリエイトリンクを直接書かない（{{LINK}} と書き、link に入れる）"),
    (re.compile(r"(?<!ガス)燈(?=が|は|の|も|で|に|と|より)"), "中の名前（燈）をお客さんに見せない（11/9 オーナー「燈？」「頭悪いやろこれ」。「毎日記録しています」のように主語なしで書く）"),
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
        # Threadsは楽天のリンクを長いまま数える（10/28 9:15 が約220字のリンクで500字を超えた）
        tprobe = t.replace(LINK, AFL_LONG)
        if where.startswith("x") and x_weight(probe) > 280:
            out.append(f"{where} {i}つ目：Xの文字数 {x_weight(probe)}/280")
        if where.startswith("threads") and threads_len(tprobe) > 500:
            out.append(f"{where} {i}つ目：Threadsの文字数 {threads_len(tprobe)}/500（リンクは長いまま280字で数える）")
    return out


OFFICIAL_FROM = date(2026, 10, 24)
REASON_FROM = date(2026, 10, 26)  # この日から、選んだ理由に「件数・評価以外の決め手の数字」を要る（10/25 オーナー「クチコミ数と評価だけで内容ペラペラ」）
SHORT_FROM = date(2026, 10, 28)  # この日から ◇ の行と下げた行を短く（10/27 オーナー「月と同じ決まり。1行に1つ、◇ は25字くらい」）
SHORT_MAX = 30
SYMBOL_FROM = date(2026, 10, 30)  # この日から行頭の記号は ✦・◎・⊹・✧（10/29 オーナー「燈もそれにさせて！」。◇・※ は使わない）


def short_line_problems(texts, where):
    """◇ の行・全角スペースで下げた行が長すぎないか（25字くらいが目安、30字をこえたら×）。"""
    out = []
    for i, t in enumerate(texts or [], 1):
        if not isinstance(t, str):
            continue
        for ln in t.splitlines():
            if (ln.startswith(("◇", "✦", "◎")) or ln.startswith("　")) and len(ln.strip()) > SHORT_MAX:
                out.append(f"{where} {i}つ目：◇・下げた行が{len(ln.strip())}字（25字くらいまで。カッコに詰めず、名前の下に1字下げた短い行を2〜3行。入らない分は2つ目へ）「{ln.strip()[:20]}…」")
    return out


def symbol_problems(texts, where):
    """行頭に古い記号（◇・※）が残っていないか（10/30〜 ✦・◎・⊹・✧）。"""
    out = []
    for i, t in enumerate(texts or [], 1):
        if not isinstance(t, str):
            continue
        for ln in t.splitlines():
            h = ln.strip()[:1]
            if h in ("◇", "※"):
                out.append(f"{where} {i}つ目：行頭の「{h}」は使わない（中身は ✦、注意は ✧。10/29 オーナー「※嫌だな」）「{ln.strip()[:20]}…」")
    return out


PLACE_FROM = date(2026, 10, 25)  # この日から、おでかけ・お店の投稿に place（HPの「地図」で探す名前）を要る
PLACE_TOPICS = {"おでかけ", "イルミネーション", "温泉", "紅葉", "無料", "イベント", "週末旅", "旅行", "グルメ", "カフェ", "新店"}  # この日の予定表から「2つ目に公式ページ」を見る


def _official_problems(texts, where):
    """PRでない投稿は、2つ目に公式ページのURLを置く（10/23 オーナー「公式ページどこ？」）。"""
    if not isinstance(texts, list) or not texts:
        return []
    if len(texts) < 2 or not any(re.search(r"https?://", t or "") for t in texts[1:]):
        return [f"{where}：2つ目に公式ページのURLがない（「公式で確かめて」と書くならリンクを置く。10/23 オーナー）"]
    return []


REVIEW_NUM_RE = re.compile(
    r"[\d,，]+\s*件|[\d,，]+\s*(つ|枚|足|軒|個|本|品|台|種類?|社|店|ブランド)(の中|を|で|と|から|比べ)|"
    r"(評価|★|星)\s*[\d.]+|[0-5][.．]\d{1,2}|[\d.]+\s*以上")


def thin_reason(line):
    """選んだ理由が、レビュー件数・評価・比べた数だけで、決め手の数字（1mあたりの値段・重さ・電気代など）が無いか。"""
    rest = REVIEW_NUM_RE.sub("", line.replace("選んだ理由：", ""))
    return not re.search(r"[0-9０-９]", rest)


def reason_line(text):
    for ln in (text or "").splitlines():
        if "選んだ理由：" in ln:
            return ln.strip()
    return ""


def reason_problems(text, where):
    """10/26から：選んだ理由は件数・評価の足切りではなく、使う場面で効く数字で書く。"""
    ln = reason_line(text)
    if ln and thin_reason(ln):
        return [f"{where}：選んだ理由がレビュー件数・評価だけ。件数・評価は足切りの条件なので、使う場面で効く数字（1mあたりの値段・重さ・1時間の電気代・洗えるか など）で選んだ理由を書く（10/25 オーナー「内容ペラペラ」）"]
    return []


def goods_problems(comment, where):
    """HPだけの商品（page_goods）の comment は3行：選んだ理由（決め手の数字）／ただし（負けた所）／向いている人。"""
    lines = [ln.strip() for ln in (comment or "").splitlines() if ln.strip()]
    out = []
    if not lines or not lines[0].startswith("選んだ理由："):
        return [f"{where}：comment の1行目は「選んだ理由：」"]
    out += reason_problems(lines[0], where)
    if len(lines) < 3 or not lines[1].startswith("ただし"):
        out.append(f"{where}：2行目は「ただし、」で始めて、比べた他の物の方が良かった所を1つ書く")
    if len(lines) < 3 or "向いて" not in lines[2]:
        out.append(f"{where}：3行目は「〜に向いています」の形で、どんな家・人に合うかを書く")
    return out


def _head(texts):
    if isinstance(texts, list) and texts and isinstance(texts[0], str) and texts[0].strip():
        return texts[0].strip().splitlines()[0].strip()
    return None


def _same_head(p, where=""):
    hx, ht = _head(p.get("x")), _head(p.get("threads"))
    out = []
    for h in (hx, ht):
        # 9:15のおでかけに付ける持ち物（link.mochimono）は、おでかけの見出しのまま（10/27 オーナー「1個目おでかけ、2こめURL+PR」）
        if p.get("link") and not p["link"].get("mochimono") and h is not None and not h.startswith("【AIが比べた"):
            out.append(f"{where}PRの1行目が「【AIが比べた」で始まっていない（PRの見出しはこの形。10/23 オーナー）")
            break
    if hx is not None and ht is not None and hx != ht:
        out.append(f"{where}XとThreadsで1行目の見出しが違う（見出しと題材は同じにし、長さだけ変える）")
    return out


AFL = "https://hb.afl.rakuten.co.jp/hgc/58b50f43.00cd84ff.58b50f44.4872e82d/?pc="


def comment_problems(p):
    """伸びたら貼る「行くときの持ち物」（10/27 オーナー「伸びてからじゃなくて最初から貼るのね？」→伸びてから）。
    9:15のおでかけに "comment" を付けると、20:20に凪が、Threadsで150以上見られていたときだけコメントに貼る。"""
    c = p.get("comment")
    if not c:
        return []
    out = []
    if p.get("slot") != "09:15" or p.get("link"):
        out.append("comment（持ち物）は 09:15 のPRでないおでかけだけ")
    t = str(c.get("text", ""))
    url = str(c.get("item", ""))
    if not url.startswith("https://item.rakuten.co.jp/"):
        out.append("comment.item は楽天市場の商品ページ（https://item.rakuten.co.jp/…）")
    for need in ("行くときの持ち物：", "選んだ理由：", "#PR"):
        if need not in t:
            out.append(f"comment.text に「{need}」がない")
    links = re.findall(r"https://\S+", t)
    if len(links) != 1 or not links[0].startswith(AFL) or urllib.parse.unquote(links[0][len(AFL):].split("&")[0]) != url:
        out.append("comment.text のURLは1つだけ、comment.item を楽天アフィリエイトの形（" + AFL + "＋商品ページをURLエンコード）にした物")
    if "！" in t or "!" in t:
        out.append("comment.text に「！」がある")
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
            if link.get("mochimono"):
                if p.get("slot") != "09:15":
                    out.append(f"{ch}：持ち物（mochimono）は 09:15 のおでかけだけ")
                if LINK in texts[0] or "#PR" in texts[0]:
                    out.append(f"{ch}：持ち物は2つ目に入れる（1つ目はPRなしのおでかけのまま）")
                if len(texts) < 2 or LINK not in texts[1] or "選んだ理由：" not in texts[1] or not any(k in texts[1] for k in ("行くときの持ち物：", "今日の楽天売れ筋：")):
                    out.append(f"{ch}：2つ目に「行くときの持ち物：」か「今日の楽天売れ筋：」と「選んだ理由：」{{{{LINK}}}} を入れる")
            elif "#PR" not in first_last:
                out.append(f"{ch}：PRなのに1つ目の最後の行に #PR がない")
            if not link.get("mochimono") and texts and isinstance(texts[0], str) and "選んだ理由：" not in texts[0]:
                out.append(f"{ch}：PRの1つ目に「選んだ理由：」の1行がない（何をいくつ比べ、どの数字で選んだか）")
            for i, t in enumerate(texts, 1):
                if LINK in t and "#PR" not in t:
                    out.append(f"{ch} {i}つ目：リンクがある投稿に #PR がない")
    out += _same_head(p)
    out += comment_problems(p)
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


# オーナーに外すよう言われた言葉（ミス帳 notes/mistakes.md）
BANNED_WORDS = {
    "あしたから行ける": "10/24 オーナー「意味わからない」で削除したシリーズ名",
}


REPEAT_FROM = date(2026, 10, 28)  # 10/27 オーナー「同じ投稿してる？」（マラソンを夜22:15と朝7:15で続けて出した）
REPEAT_DAYS = 3


def _post_urls(p):
    """投稿の2つ目以降（公式ページなど）に書いたURL。fallback は数えない。"""
    out = set()
    for ch in ("x", "threads"):
        for t in (p.get(ch) or [])[1:]:
            for u in re.findall(r"https?://[^\s）)」]+", t if isinstance(t, str) else ""):
                out.add(u.split("?")[0].rstrip("/"))
    return out


def _at(day, slot):
    try:
        h, m = (int(x) for x in str(slot).split(":"))
    except ValueError:
        h, m = 0, 0
    return datetime(day.year, day.month, day.day, h, m)


def _first(p):
    t = (p.get("x") or [""])[0]
    return re.sub(r"\s", "", t if isinstance(t, str) else "")[:20]


def repeat_problems(fp, data, d):
    """同じ公式ページの話を続けて出さない（10/27 オーナー「せめて文章変えるとか、違う投稿の後とかにしたい」）。
    ×：前の投稿から24時間たたないうちに同じページを使う／1行目の書き出しが前の回と同じ。"""
    if d < REPEAT_FROM:
        return []
    used = {}
    for k in range(REPEAT_DAYS, 0, -1):
        prev = d - timedelta(days=k)
        pd = load_json(os.path.join(os.path.dirname(fp) or ".", f"{prev.isoformat()}.json"), {}) or {}
        for p in pd.get("posts", []):
            for u in _post_urls(p):
                used[u] = (_at(prev, p.get("slot")), _first(p), f"{prev.month}/{prev.day} {p.get('slot')}")
    out = []
    for p in sorted(data["posts"], key=lambda p: str(p.get("slot"))):
        at, first = _at(d, p.get("slot")), _first(p)
        for u in sorted(_post_urls(p)):
            if u in used:
                pat, pfirst, where = used[u]
                if at - pat < timedelta(hours=24):
                    out.append(f"{fp} {p.get('slot')}: 同じページを {where} にも使った。24時間あけて、ほかの投稿をはさむ（10/27 オーナー）: {u}")
                elif first == pfirst:
                    out.append(f"{fp} {p.get('slot')}: {where} と同じページで、1行目の書き出しも同じ。文を変える（10/27 オーナー「せめて文章変える」）: {u}")
            used[u] = (at, first, f"{d.month}/{d.day} {p.get('slot')}")
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
    probs += repeat_problems(fp, data, d)
    for p in data["posts"]:
        lk = p.get("link") or {}
        if lk.get("type") == "ichiba" and str(lk.get("url", "")).split("?")[0].rstrip("/") not in room_urls:
            probs.append(f"{fp} {p.get('slot')}: PRで選んだ楽天市場の商品が room にない（PRの商品は必ずROOMにも載せる。10/22 オーナー）")
    for p in data["posts"]:
        extra = []
        if not p.get("link") and d >= OFFICIAL_FROM:
            extra = _official_problems(p.get("x"), "x") + _official_problems(p.get("threads"), "threads")
        if not p.get("link") and d >= PLACE_FROM and p.get("topic") in PLACE_TOPICS and not str(p.get("place", "")).strip():
            extra.append("place がない（HPの「地図」で探す施設名。例 \"なんばパークス\"。1か所に決まらない催しは \"-\"。10/24 オーナー「地図おしたらマップ」）")
        for w in BANNED_WORDS:
            if any(w in t for t in (p.get("x") or []) + (p.get("threads") or [])):
                extra.append(f"「{w}」は使わない（{BANNED_WORDS[w]}）")
        if d >= SHORT_FROM:
            fb = p.get("fallback") or {}
            for ch in ("x", "threads"):
                extra += short_line_problems(p.get(ch), ch) + short_line_problems(fb.get(ch), "fallback " + ch)
        if d >= SYMBOL_FROM:
            fb = p.get("fallback") or {}
            for ch in ("x", "threads"):
                extra += symbol_problems(p.get(ch), ch) + symbol_problems(fb.get(ch), "fallback " + ch)
        if p.get("link") and d >= REASON_FROM:
            for ch in ("x", "threads"):
                t = (p.get(ch) or [""])[0]
                extra += reason_problems(t if isinstance(t, str) else "", ch)
        for pr in post_problems(p) + asof_problems(p, d) + extra:
            probs.append(f"{fp} {p.get('slot', '?')}: {pr}")
    for i, it in enumerate(data.get("room") or [], 1):
        if not str(it.get("url", "")).startswith("https://item.rakuten.co.jp/") or not it.get("expect") or not it.get("comment"):
            probs.append(f"{fp} ROOM {i}件目: url（楽天市場の商品ページ）・expect・comment が要る")
    if d >= REASON_FROM:
        for i, it in enumerate(data.get("page_goods") or [], 1):
            if isinstance(it, dict):
                probs += [f"{fp} {pr}" for pr in goods_problems(it.get("comment"), f"HPだけの商品 {i}件目")]
    return probs


def asof_problems(p, d):
    """出どころの「（M/D時点）」が投稿の日から7日より古くないか。x・threads のどこか（ふつうは2つ目のURLの行）に必ず要る。"""
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


def store_problems():
    """集め係が足す data/page-goods.json と data/page-spots.json の形（10/27から足した物）。"""
    out = []
    g = load_json(path("data", "page-goods.json"), {}) or {}
    urls = set()
    for i, it in enumerate(g.get("items", []), 1):
        where = f"data/page-goods.json {i}件目（{it.get('expect', '')}）"
        if it.get("url") in urls:
            out.append(f"{where}：同じ商品が2つ")
        urls.add(it.get("url"))
        if (it.get("added") or "") < "2026-10-27":
            continue
        if not str(it.get("url", "")).startswith("https://item.rakuten.co.jp/") or not it.get("expect"):
            out.append(f"{where}：url（楽天市場の商品ページ）と expect が要る")
        out += goods_problems(it.get("comment"), where)
    sp = load_json(path("data", "page-spots.json"), {}) or {}
    for i, it in enumerate(sp.get("items", []), 1):
        if (it.get("checked") or "") < "2026-10-27":
            continue
        where = f"data/page-spots.json {i}件目（{it.get('title', '')}）"
        need = ["title", "pref", "place", "url", "checked"] + (["open"] if it.get("kind") == "shop" else ["start", "ends", "when"])
        miss = [k for k in need if not it.get(k)]
        if miss:
            out.append(f"{where}：{'・'.join(miss)} が無い")
        if it.get("pref") and it["pref"] not in ("東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬"):
            out.append(f"{where}：HPは関東だけ（pref は東京・神奈川・埼玉・千葉・茨城・栃木・群馬）")
        if not str(it.get("url", "")).startswith("https://"):
            out.append(f"{where}：url は https の公式ページ")
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
    if not argv[1:] or any("page-" in f for f in argv[1:]):
        allp += store_problems()
    for p in allp:
        print("×", p)
    if not allp:
        print(f"OK（{len(files)}ファイル）")
    return 1 if allp else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
