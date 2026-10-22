"""予定表（schedule/日付.json）の機械チェック。

燈が書いた予定表が決まりを守っているかを確かめる。守っていない投稿は予約しない（代わりの投稿を出す）。
使い方：python scripts/check.py schedule/2026-10-24.json  （引数なしなら schedule/ の全部）
"""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import load_json, path, threads_len, x_weight  # noqa: E402

LINK = "{{LINK}}"
BANNED = [
    (re.compile(r"amazon\.co\.jp|amzn\.(to|asia)", re.I), "AmazonのURLは使わない（確かめる道具がないため止めている）"),
    (re.compile(r"a\.r10\.to", re.I), "楽天の短縮リンクは使わない（リンクは予約係が楽天から受け取る）"),
    (re.compile(r"hb\.afl\.rakuten", re.I), "アフィリエイトリンクを直接書かない（{{LINK}} と書く）"),
]
SLOT_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def _texts_problems(texts, where, allow_link):
    out = []
    if not isinstance(texts, list) or not texts or not all(isinstance(t, str) and t.strip() for t in texts):
        return [f"{where}：文が空か、形が違う（[\"1つ目\", \"2つ目\"] の形）"]
    for i, t in enumerate(texts, 1):
        for rx, why in BANNED:
            if rx.search(t):
                out.append(f"{where} {i}つ目：{why}")
        if LINK in t and not allow_link:
            out.append(f"{where} {i}つ目：{{{{LINK}}}} があるのに link の指定がない（代わりの投稿には使えない）")
        probe = t.replace(LINK, "https://hb.afl.rakuten.co.jp/x")
        if where.startswith("x") and x_weight(probe) > 280:
            out.append(f"{where} {i}つ目：Xの文字数 {x_weight(probe)}/280")
        if where.startswith("threads") and threads_len(probe) > 500:
            out.append(f"{where} {i}つ目：Threadsの文字数 {threads_len(probe)}/500")
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
        elif t not in ("ichiba", "travel"):
            out.append("link.type は ichiba か travel")
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
            for i, t in enumerate(texts, 1):
                if LINK in t and "#PR" not in t:
                    out.append(f"{ch} {i}つ目：リンクがある投稿に #PR がない")
    if not p.get("topic"):
        out.append("topic（Threadsのトピック）がない")
    if link or p.get("until"):
        fb = p.get("fallback")
        if not fb:
            out.append("PRか期限つきなのに fallback（代わりの通常投稿）がない")
        else:
            out += ["fallback " + s for s in _texts_problems(fb.get("x"), "x", False)]
            out += ["fallback " + s for s in _texts_problems(fb.get("threads"), "threads", False)]
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
    for p in data["posts"]:
        for pr in post_problems(p):
            probs.append(f"{fp} {p.get('slot', '?')}: {pr}")
    return probs


def main(argv):
    files = argv[1:] or sorted(glob.glob(path("schedule", "*.json")))
    allp = []
    for fp in files:
        allp += check_file(fp)
    for p in allp:
        print("×", p)
    if not allp:
        print(f"OK（{len(files)}ファイル）")
    return 1 if allp else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
