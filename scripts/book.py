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
from lib import (JST, URL_RE, BufferError, a8_link, append_log, buffer_create, buffer_posts,  # noqa: E402
                 about_item, item_code_from_url, load_json, missing_specs, now_jst, page_check, path,
                 rakuten_item, rakuten_travel_link, save_json)

LEAD_MIN = int(os.environ.get("LEAD_MIN", "150"))   # 何分先までを予約するか
LATE_MIN = 90                                       # 時刻を過ぎていても、この分までなら15分後に出す
MAX_TRIES = 3
SERVICES = ("twitter", "threads")


def resolve_link(link, texts=()):
    """PRのリンクを確かめる。texts はPRの文（大きさ・重さなどの数字が商品ページと同じかを見る）。"""
    if link["type"] == "ichiba":
        code = item_code_from_url(link["url"])
        if not code:
            return {"ok": False, "why": "商品ページのURLから商品番号が取れない"}
        r = rakuten_item(code, link.get("expect"))
        exp = link.get("expect")
        if r.get("ok") and exp and exp not in r.get("name", ""):
            r = {"ok": False, "why": f"商品名に「{exp}」がない（別の商品の可能性）: {r.get('name', '')[:40]}"}
        if r.get("ok"):
            miss = missing_specs(about_item(texts, exp), r.get("name", ""), r.get("caption", ""))
            if miss:
                r = {"ok": False, "why": "文の数字が商品ページにない（書き違いの可能性）: " + "・".join(miss[:4])}
        return r
    if link["type"] == "travel":
        return rakuten_travel_link(link["hotelNo"])
    if link["type"] == "a8":
        return a8_link(link["url"], link.get("expect_host", ""))
    return {"ok": False, "why": "link.type が分からない"}


def source_problem(texts):
    """文の中の出どころURLを開き、ページがない・「終了」と出ているなら理由を返す。開けないだけなら止めない。"""
    seen = set()
    for t in texts:
        for u in URL_RE.findall(t):
            u = u.rstrip("）)」。、")
            if u in seen or "hb.afl.rakuten" in u or "px.a8.net" in u or "{{" in u:
                continue
            seen.add(u)
            st, why = page_check(u)
            if st in ("dead", "ended"):
                return f"出どころ {u[:60]} が{why}"
    return ""


def choose(post, day, now):
    """出す中身を決め、出どころのページも確かめる。"""
    xs, ths, topic, kind, why = _choose(post, day, now)
    if xs is None:
        return xs, ths, topic, kind, why
    prob = source_problem(list(xs) + list(ths))
    if not prob:
        return xs, ths, topic, kind, why
    fb = post.get("fallback")
    if kind != "代わり" and fb:
        if not source_problem(list(fb["x"]) + list(fb["threads"])):
            return fb["x"], fb["threads"], fb.get("topic") or post.get("topic"), "代わり", prob
    return None, None, None, "中止", prob


def _choose(post, day, now):
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
        r = resolve_link(link, list(post["x"]) + list(post["threads"]))
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
    # 翌日の分は0時を過ぎてから予約する（夜の回や朝の確認が予定表を直した後の内容で出すため）
    for d in (now.date(),):
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
                    r.update({"id": p["id"], "kind": kind, "at": when.strftime("%H:%M"),
                              "texts": texts, "topic": topic})
                    r.pop("error", None)
                    late = "" if when == due else f"（遅れたので {when.strftime('%H:%M')} に）"
                    append_log(day, f"{slot} {s} 予約OK［{kind}］{late} {why}".rstrip())
                except BufferError as e:
                    r["error"] = str(e)[:200]
                    append_log(day, f"{slot} {s} 予約×（{r['tries']}回目）：{str(e)[:150]}")
            changed = True
    try:
        changed |= after_check(cfg, state, now)
    except BufferError as e:
        append_log(now.date().isoformat(), f"出たかの確認ができない：{str(e)[:120]}")
    if changed:
        save_json(path("state", "booked.json"), state)
    return 0


def after_check(cfg, state, now):
    """予約した投稿が本当に出たかを Buffer に聞く。出ていなければ記録し、1回だけ出し直す。
    朝8:30すぎには、雫の4コマが出たかも見る。"""
    changed = False
    start, end = now - timedelta(hours=6), now - timedelta(minutes=20)
    waiting = []
    for key, rec in state.items():
        if " " not in key:
            continue
        for s, r in rec.items():
            if not isinstance(r, dict) or not r.get("id") or r.get("seen"):
                continue
            at = r.get("at") or key.split(" ")[1]
            try:
                due = datetime.fromisoformat(f"{key.split(' ')[0]}T{at}").replace(tzinfo=JST)
            except ValueError:
                continue
            if start <= due <= end:
                waiting.append((key, s, r, due))
    if waiting:
        sent = {p["id"] for p in buffer_posts(cfg, ["sent"], start - timedelta(hours=1), end)}
        errs = {p["id"] for p in buffer_posts(cfg, ["error"], start - timedelta(hours=1), end)}
        for key, s, r, due in waiting:
            day, slot = key.split(" ")
            if r["id"] in sent:
                r["seen"] = "出た"
                append_log(day, f"{slot} {s} 出た")
                changed = True
            elif r["id"] in errs or now - due > timedelta(minutes=60):
                why = "Bufferでエラー" if r["id"] in errs else "時刻を60分過ぎても出ていない"
                r["seen"] = "出ない：" + why
                changed = True
                if r.get("texts") and not r.get("retried") and now - due < timedelta(hours=3):
                    r["retried"] = True
                    when = (now + timedelta(minutes=15)).astimezone(timezone.utc)
                    try:
                        texts = list(r["texts"])
                        texts[0] = texts[0].rstrip() + "\n"  # Bufferの「同じ投稿」はねを避ける
                        p = buffer_create(cfg["channels"][s], s, texts, when.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                                          topic=r.get("topic") if s == "threads" else None)
                        append_log(day, f"{slot} {s} 出なかった（{why}）→ 15分後に出し直しを予約 {p['id']}")
                        r["id"], r["seen"], r["at"] = p["id"], None, (now + timedelta(minutes=15)).strftime("%H:%M")
                    except BufferError as e:
                        append_log(day, f"{slot} {s} 出なかった（{why}）。出し直しも×：{str(e)[:100]}")
                else:
                    append_log(day, f"{slot} {s} 出なかった（{why}）")
    # 雫の4コマ（8:00）が出たか
    day = now.date().isoformat()
    k = f"koma4 {day}".replace(" ", ":")
    if now.hour >= 8 and now.minute >= 30 or now.hour >= 9:
        if not state.get(k) and now.hour < 12:
            ours = {r.get("id") for key, rec in state.items() if " " in key for r in rec.values() if isinstance(r, dict)}
            t0 = now.replace(hour=7, minute=30, second=0, microsecond=0)
            t1 = now.replace(hour=8, minute=45, second=0, microsecond=0)
            found = [p for p in buffer_posts(cfg, ["sent"], t0, t1) if p["id"] not in ours]
            svc = sorted({p["channelService"] for p in found})
            state[k] = {"found": svc}
            append_log(day, "4コマ（雫）出た：" + "・".join(svc) if svc else "4コマ（雫）が8:45までに出ていない")
            changed = True
    return changed


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


def sent_test():
    """Bufferに「出た・エラー」の投稿を聞けるかを確かめる（何も予約しない）。"""
    cfg = load_json(path("config.json"))
    now = now_jst()
    for st in ("sent", "error"):
        ps = buffer_posts(cfg, [st], now - timedelta(days=1), now)
        print(st, len(ps), [(p["channelService"], p["dueAt"][11:16]) for p in ps[:5]])
    for st in ("scheduled", "draft"):  # これから出る予約・下書き（手で足された物がないか）
        try:
            ps = buffer_posts(cfg, [st], now - timedelta(days=2), now + timedelta(days=3))
            print(st, len(ps), [(p["channelService"], p["dueAt"], (p["text"] or "")[:30]) for p in ps[:20]])
        except BufferError as e:
            print(st, "×", str(e)[:150])
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--sent-test":
        sys.exit(sent_test())
    if len(sys.argv) > 2 and sys.argv[1] == "--test":
        sys.exit(test(sys.argv[2]))
    sys.exit(run())
