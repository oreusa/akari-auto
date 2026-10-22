"""予約係。1時間おきに動き、これから2時間半以内に出す投稿を Buffer に予約する。

・PRは予約する直前に楽天に「今も売っているか・同じ商品か」を聞き、楽天が返す正式なリンクを入れる。
  だめなら、その場で代わりの通常投稿（fallback）を予約する。
・期限（until）を過ぎた投稿も代わりにする。
・同じ投稿を2回予約しない（state/booked.json に記録）。
・何をしたかは log/日付.md に1行ずつ書く。燈は毎晩これを読む。

テスト：python scripts/book.py --test <楽天の商品ページURL>
  → その商品のリンクを楽天から受け取り、X・Threads に「下書き」を1本ずつ作る（公開はしない）。
"""
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check import LINK, post_problems  # noqa: E402
from lib import (JST, BufferError, append_log, buffer_create, item_code_from_url,  # noqa: E402
                 load_json, now_jst, path, rakuten_item, rakuten_travel_link, save_json)

LEAD_MIN = int(os.environ.get("LEAD_MIN", "150"))   # 何分先までを予約するか
LATE_MIN = 90                                       # 時刻を過ぎていても、この分までなら15分後に出す
MAX_TRIES = 3
SERVICES = ("twitter", "threads")


def resolve_link(link, day, slot):
    if link["type"] == "ichiba":
        code = item_code_from_url(link["url"])
        if not code:
            return {"ok": False, "why": "商品ページのURLから商品番号が取れない"}
        r = rakuten_item(code, link.get("expect"))
        exp = link.get("expect")
        if r.get("ok") and exp and exp not in r.get("name", ""):
            r = {"ok": False, "why": f"商品名に「{exp}」がない（別の商品の可能性）: {r.get('name', '')[:40]}"}
        return r
    if link["type"] == "travel":
        return rakuten_travel_link(link["hotelNo"])
    return {"ok": False, "why": "link.type が分からない"}


def choose(post, day, now):
    """出す中身を決める。戻り値：(x文, threads文, topic, 種類, 理由)"""
    probs = post_problems(post)
    fb = post.get("fallback")
    if probs:
        if fb:
            return fb["x"], fb["threads"], fb.get("topic") or post.get("topic"), "代わり", "チェック×: " + probs[0]
        return None, None, None, "中止", "チェック×（代わりなし）: " + probs[0]
    until = post.get("until")
    if until:
        lim = datetime.fromisoformat(until).replace(tzinfo=JST)
        due = datetime.fromisoformat(f"{day}T{post['slot']}").replace(tzinfo=JST)
        if due > lim:
            return fb["x"], fb["threads"], fb.get("topic") or post["topic"], "代わり", f"期限 {until} を過ぎる"
    link = post.get("link")
    if not link:
        return post["x"], post["threads"], post["topic"], "通常", ""
    try:
        r = resolve_link(link, day, post["slot"])
    except Exception as e:  # 楽天につながらない
        r = {"ok": False, "why": f"楽天に確かめられない: {e}"[:120]}
    if not r.get("ok"):
        return fb["x"], fb["threads"], fb.get("topic") or post["topic"], "代わり", "PR不合格: " + r.get("why", "")
    url = r["link"]
    xs = [t.replace(LINK, url) for t in post["x"]]
    ths = [t.replace(LINK, url) for t in post["threads"]]
    note = f"PR合格: {r.get('name', '')[:30]}"
    if r.get("reviewCount") is not None:
        note += f"（レビュー{r['reviewCount']}件・{r.get('reviewAverage')}）"
    return xs, ths, post["topic"], "PR", note


def run(now=None):
    now = now or now_jst()
    cfg = load_json(path("config.json"))
    if not cfg or not cfg.get("channels"):
        print("config.json がありません。先に「最初の設定（setup）」を動かしてください。")
        return 0  # キーを入れる前は何もしない（毎時間の失敗メールを出さない）
    state = load_json(path("state", "booked.json"), {})
    changed = False
    for d in (now.date(), now.date() + timedelta(days=1)):
        day = d.isoformat()
        sched = load_json(path("schedule", f"{day}.json"))
        if not sched:
            continue
        for post in sched.get("posts", []):
            slot = post.get("slot", "")
            try:
                due = datetime.fromisoformat(f"{day}T{slot}").replace(tzinfo=JST)
            except ValueError:
                continue
            mins = (due - now).total_seconds() / 60
            if mins > LEAD_MIN or mins < -LATE_MIN:
                continue
            key = f"{day} {slot}"
            rec = state.setdefault(key, {})
            todo = [s for s in SERVICES if s in cfg["channels"]
                    and not rec.get(s, {}).get("id") and rec.get(s, {}).get("tries", 0) < MAX_TRIES]
            if not todo:
                continue
            xs, ths, topic, kind, why = choose(post, day, now)
            if xs is None:
                append_log(day, f"{slot} 中止：{why}")
                for s in todo:
                    rec[s] = {"tries": MAX_TRIES, "error": why}
                changed = True
                continue
            when = due if mins >= 15 else now + timedelta(minutes=15)
            due_utc = when.astimezone(timezone.utc)
            due_iso = due_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            for s in todo:
                texts = xs if s == "twitter" else ths
                r = rec.setdefault(s, {"tries": 0})
                r["tries"] = r.get("tries", 0) + 1
                try:
                    p = buffer_create(cfg["channels"][s], s, texts, due_iso,
                                      topic=topic if s == "threads" else None)
                    r.update({"id": p["id"], "kind": kind, "at": when.strftime("%H:%M")})
                    r.pop("error", None)
                    late = "" if when == due else f"（遅れたので {when.strftime('%H:%M')} に）"
                    append_log(day, f"{slot} {s} 予約OK［{kind}］{late} {why}".rstrip())
                except BufferError as e:
                    r["error"] = str(e)[:200]
                    append_log(day, f"{slot} {s} 予約×（{r['tries']}回目）：{str(e)[:150]}")
            changed = True
    if changed:
        save_json(path("state", "booked.json"), state)
    return 0


def test(item_url):
    cfg = load_json(path("config.json"))
    code = item_code_from_url(item_url)
    r = rakuten_item(code, os.environ.get("ITEM_KEYWORD")) if code else {"ok": False, "why": "URLが楽天市場の商品ページではない"}
    print("楽天の結果:", {k: v for k, v in r.items() if k != "link"})
    if not r.get("ok"):
        return 1
    print("リンクの頭:", r["link"][:60], "…")
    due = (now_jst() + timedelta(days=2)).astimezone(timezone.utc)
    due_iso = due.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    texts = ["【テスト】燈の予約係のテストです（公開しません）\n#PR", f"商品ページはこちらです\n{r['link']}\n#PR"]
    for s in SERVICES:
        if s in cfg["channels"]:
            p = buffer_create(cfg["channels"][s], s, texts, due_iso,
                              topic="テスト" if s == "threads" else None, draft=True)
            print(s, "下書きを作成:", p["id"], p["status"])
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--test":
        sys.exit(test(sys.argv[2]))
    sys.exit(run())
