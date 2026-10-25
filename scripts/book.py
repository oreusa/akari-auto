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
from check import LINK, SLOT_RE, post_problems  # noqa: E402
from lib import (JST, URL_RE, BufferError, a8_link, buffer_gql, amazon_link, append_log, buffer_create, buffer_posts,  # noqa: E402
                 about_item, item_code_from_url, load_json, missing_specs, now_jst, page_check, path,
                 rakuten_item, rakuten_travel_link, save_json, http_raw, fetch_image, koma4_instagram_media,
                 story_local, image_diff, story_boxes, STORY_DIFF_MAX)

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
    if link["type"] == "amazon":
        exp = link.get("expect")
        r = amazon_link(link.get("asin"), exp)
        if r.get("ok"):
            miss = missing_specs(about_item(texts, exp), r.get("name", ""), r.get("caption", ""))
            if miss:
                r = {"ok": False, "why": "文の数字がAmazon確認帳にない（書き違いの可能性）: " + "・".join(miss[:4])}
        return r
    return {"ok": False, "why": "link.type が分からない"}


PAGE_LINE = "AIが比べたおでかけ・宿・お得の一覧：{url}"  # 前の作りの1行（予約済みの物を見分けるのに使う）


def page_line(texts, url, due):
    """投稿の中身に合わせた、HPへ来る理由の1行（10/24 オーナー「HPまで来させたらPRよく見られる。一石二鳥」）。
    おでかけ＝その地域の一覧の数、PR＝比べた表と選んだ理由。数はその時刻にHPに並ぶおでかけの数。"""
    joined = " ".join(texts)
    if "#PR" in joined:
        return f"比べた表と選んだ理由、ほかにうさぎが選んだ物：{url}"
    try:
        import page
        n = page.spot_counts(due) if due else {}
        reg = page.post_region(texts)
    except Exception:  # 数えられない日は前の1行
        return PAGE_LINE.format(url=url)
    if reg and n.get(reg, 0) >= 3:
        return f"{reg}のおでかけ{n[reg]}件、公式ページつきの一覧：{url}"
    if n.get("関東", 0) >= 3 and n.get("関西", 0) >= 3:
        return f"関東{n['関東']}件・関西{n['関西']}件のおでかけ、公式ページつきの一覧：{url}"
    return PAGE_LINE.format(url=url)


def with_page(texts, service, cfg, slot="", due=None):
    """2つ目（最後）の文の最後に、プロフィール用ページのURLを1行足す（10/24 オーナー「HPの宣伝、投稿のURLに一緒に付けとけ。一石二鳥」）。
    X・Threadsとも最後に足す（10/24 オーナー「せめて最後に入れろ」。PRや公式のリンクを先に見せる）。文字数を超えるなら前の短い1行、それも超えるなら足さない。"""
    from lib import threads_len, x_weight
    pg = (cfg.get("page") or {})
    url = pg.get("url")
    if not url or not pg.get("promote", True) or len(texts) < 2 or any(url in t for t in texts):
        return list(texts)
    if slot:  # どの投稿から来たか分かる印（x0715 = Xの7:15の投稿、t0715 = Threadsの7:15）
        url = f"{url}?f={'x' if service == 'twitter' else 't'}{slot.replace(':', '')}"
    for line in dict.fromkeys([page_line(texts, url, due), PAGE_LINE.format(url=url)]):
        new = texts[-1].rstrip() + "\n\n" + line
        fits = (x_weight(new) <= 280) if service == "twitter" else (threads_len(new) <= 500)
        if fits:
            return list(texts[:-1]) + [new]
    return list(texts)


PAGE_HEAD = PAGE_LINE.split("{")[0]


def page_at_head(texts):
    """前の作り（Xはページの行を2つ目の頭に入れていた）で予約した物か。"""
    return len(texts) >= 2 and texts[-1].startswith(PAGE_HEAD)


def strip_page_head(texts):
    return list(texts[:-1]) + [texts[-1].split("\n\n", 1)[1] if "\n\n" in texts[-1] else texts[-1]]


def page_at_tail(texts):
    """前の作り（最後に「AIが比べたおでかけ・宿・お得の一覧」の1行）で予約した物か。"""
    return len(texts) >= 2 and texts[-1].rsplit("\n\n", 1)[-1].startswith(PAGE_HEAD) and "\n\n" in texts[-1]


def strip_page_tail(texts):
    return list(texts[:-1]) + [texts[-1].rsplit("\n\n", 1)[0]]


DELETE_POST = 'mutation($i:DeletePostInput!){deletePost(input:$i){__typename}}'


def delete_post(pid):
    r = (buffer_gql(DELETE_POST, {"i": {"id": pid}}) or {}).get("deletePost") or {}
    if "Error" in str(r.get("__typename", "")):
        raise BufferError(f"消せない: {r.get('__typename')}")


def refresh_page(cfg, state, now):
    """ページのURLを足す仕組みより前に予約した投稿を、URLを足した文で予約し直す（10/24 オーナー「新しい取り組みは即時」）。
    新しい予約が作れてから古い方を消す。出る25分前を切った物・もう出た物には触らない。"""
    url = (cfg.get("page") or {}).get("url")
    if not url or not (cfg.get("page") or {}).get("promote", True):
        return False
    days = {now.date().isoformat(), (now.date() + timedelta(days=1)).isoformat()}
    todo = []
    for key, rec in state.items():
        day, _, slot = key.partition(" ")
        if day not in days or not SLOT_RE.match(slot):
            continue
        for s in SERVICES:
            r = rec.get(s)
            if not isinstance(r, dict) or not r.get("id") or r.get("seen") or len(r.get("texts") or []) < 2:
                continue
            head = page_at_head(r["texts"])  # 頭に入れた物は、最後に入れ直す（10/24 オーナー「せめて最後に入れろ」）
            old = page_at_tail(r["texts"])  # 前の1行（中身に合わせない一覧の1行）の物も入れ直す
            if not head and not old and (r.get("page") or any(url in t for t in r["texts"])):
                continue
            if r.get("page") in ("字数が足りない", "作れない", "消せない"):  # 1回だめだった物は繰り返さない
                continue
            try:
                due = datetime.fromisoformat(f"{day}T{r.get('at') or slot}").replace(tzinfo=JST)
            except ValueError:
                continue
            if due - now >= timedelta(minutes=25):
                todo.append((day, slot, s, r, due))
    if not todo:
        return False
    waiting = {p["id"] for p in buffer_posts(cfg, ["scheduled"], now, now + timedelta(hours=40))}
    changed = False
    for day, slot, s, r, due in todo:
        if r["id"] not in waiting:  # Bufferで予約中でない物（出た・消された）は触らない
            continue
        base = (strip_page_head(r["texts"]) if page_at_head(r["texts"])
                else strip_page_tail(r["texts"]) if page_at_tail(r["texts"]) else r["texts"])
        new = with_page(base, s, cfg, slot, due)
        if new == r["texts"] or new == base:
            r["page"] = "字数が足りない"
            changed = True
            continue
        due_iso = due.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        try:
            p = buffer_create(cfg["channels"][s], s, new, due_iso, topic=r.get("topic") if s == "threads" else None)
        except BufferError as e:
            append_log(day, f"{slot} {s} ページのURLを足した予約し直し×（元の予約のまま）：{str(e)[:120]}")
            r["page"] = "作れない"
            changed = True
            continue
        try:
            delete_post(r["id"])
        except BufferError as e:
            try:  # 古い方を消せないなら、2回出ないよう新しい方を消して元のままにする
                delete_post(p["id"])
                append_log(day, f"{slot} {s} ページのURLを足せない（古い予約を消せない。元の予約のまま）：{str(e)[:100]}")
            except BufferError:
                append_log(day, f"{slot} {s} ×2本予約のおそれ（{r['id']} と {p['id']}）。燈が朝の確認で片方を消す")
            r["page"] = "消せない"
            changed = True
            continue
        r.update({"id": p["id"], "texts": new, "page": "足した"})
        append_log(day, f"{slot} {s} 予約し直しOK（ページのURLを足した）")
        changed = True
    return changed


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
                texts = with_page(xs if s == "twitter" else ths, s, cfg, slot, due)
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
        changed |= refresh_page(cfg, state, now)
    except BufferError as e:
        append_log(now.date().isoformat(), f"ページのURLの予約し直し×：{str(e)[:150]}")
    try:
        changed |= book_koma4(cfg, state, now)
    except BufferError as e:
        append_log(now.date().isoformat(), f"4コマ 予約×：{str(e)[:150]}")
    try:
        changed |= book_extra(cfg, state, now)
    except BufferError as e:
        append_log(now.date().isoformat(), f"1回だけの投稿 予約×：{str(e)[:150]}")
    try:
        changed |= after_check(cfg, state, now)
    except BufferError as e:
        append_log(now.date().isoformat(), f"出たかの確認ができない：{str(e)[:120]}")
    if changed:
        save_json(path("state", "booked.json"), state)
    return 0


KOMA4_SERVICES = ("twitter", "threads", "instagram")
# Instagram の毎日の4コマ（10/23 オーナー「OK」）：スライド4枚（8:00）とストーリー2枚（8:00・8:01）。動画の日はリールも
IG_EXTRA = (("ig_slides", "post", 0), ("ig_story1", "story", 0), ("ig_story2", "story", 1))


IG_V = 2  # 切り方を変えたら上げる（前の切り方のURLを使わない）


def stories_ok(ig, full):
    """wsrv.nl が返したストーリーが、手元で切った見本と同じかを見る（10/24 ずれたまま出た）。"""
    ok = []
    for u, b in zip(ig["stories"], story_boxes(ig["boxes"])):
        try:
            im = fetch_image(u)
            d = image_diff(im, story_local(full, b))
            ok.append(im.size == (1080, 1920) and d <= STORY_DIFF_MAX)
            ig.setdefault("story_diff", []).append(round(d, 1))
        except Exception:
            ok.append(False)
    return ok


def media_problem(url, kind):
    """Bufferが取りに行く絵・動画のURLが、ログインなしで開けるかを見る。だめなら理由を返す。"""
    try:
        st, body, final = http_raw(url)
    except Exception as e:  # 通信の失敗
        return f"{kind}のURLが開けない（{str(e)[:60]}）"
    if st != 200:
        return f"{kind}のURLが開けない（{st}）"
    if "accounts.google.com" in (final or "") or body[:15].lstrip().lower().startswith(b"<!doctype html"):
        return f"{kind}のURLがログイン画面になる（ドライブのフォルダが「リンクを知っている全員」になっていない）"
    return ""


def book_koma4(cfg, state, now):
    """雫が描いた4コマを予約する（10/23から。雫はBufferを使わない）。

    koma4/日付.json：{"slot": "08:00", "episode": 16, "text": "投稿文", "image_url": "…", "video_url": "…"}
    text は燈の夜の回が書く。image_url・video_url は朝の4コマ係（燈）が、雫が保存した絵から入れる。
    X・Threads は画像。Instagram は、縦長1:3の絵がそのまま載らないので、1コマずつ切ったスライド4枚と、
    2コマずつのストーリー2枚を毎日出す（切るのは wsrv.nl。Bufferはその切ったURLを取りに行く）。動画がある日はリールも出す。
    """
    day = now.date().isoformat()
    k = load_json(path("koma4", f"{day}.json"))
    if not k or not k.get("text") or not k.get("image_url"):
        return False
    slot = k.get("slot") or "08:00"
    due = datetime.fromisoformat(f"{day}T{slot}").replace(tzinfo=JST)
    mins = (due - now).total_seconds() / 60
    late_ok = k.get("late_until") and now.strftime("%H:%M") < k["late_until"]  # 手で出し直すとき（燈が入れる）
    if mins > LEAD_MIN or (mins < -6 * 60 and not late_ok):  # 4コマは遅れても、その日の昼までは出す
        return False
    key = f"{day} 4コマ"
    rec = state.setdefault(key, {})
    def open_(s):
        return not rec.get(s, {}).get("id") and rec.get(s, {}).get("tries", 0) < MAX_TRIES
    todo = [s for s in KOMA4_SERVICES if s in cfg["channels"] and open_(s)
            and (s != "instagram" or (k.get("video_url") and k.get("video_ok")))]  # リールは機械の確認（videocheck.py）に通った動画だけ
    ig_todo = [e for e in IG_EXTRA if "instagram" in cfg["channels"] and open_(e[0])]
    if not todo and not ig_todo:
        return False
    bad = media_problem(k["image_url"], "image") or (k.get("video_ok") and media_problem(k["video_url"], "video"))
    if bad:
        if not rec.get("media_error"):
            append_log(day, f"4コマ 第{k.get('episode', '?')}話 予約できない：{bad}")
        rec["media_error"] = bad
        return True
    rec.pop("media_error", None)
    when = due if mins >= 3 else now + timedelta(minutes=3)  # 7:50の直しでも8:00に間に合わせる
    alt = f"4コマ漫画 第{k.get('episode', '')}話"
    jobs = []
    for s in todo:
        jobs.append((s, s, {"image": k["image_url"], "video": k.get("video_url") if s == "instagram" else None, "alt": alt}, when))
    if ig_todo:
        ig = rec.get("ig_media")
        if not ig or ig.get("src") != k["image_url"] or ig.get("v") != IG_V:  # 7:50の直しで絵が変わったら切り直す
            try:
                full = fetch_image(k["image_url"])
                ig = koma4_instagram_media(k["image_url"], full)
                ig["src"], ig["v"] = k["image_url"], IG_V
                bad = media_problem(ig["slides"][0], "Instagram用に切った絵")
                ig["story_ok"] = stories_ok(ig, full)
            except Exception as e:
                ig, bad = None, f"Instagram用に絵を切れない（{str(e)[:80]}）"
            if bad:
                if rec.get("ig_error") != bad:
                    append_log(day, f"4コマ 第{k.get('episode', '?')}話 Instagram 予約できない：{bad}")
                rec["ig_error"] = bad
                ig = None
            else:
                rec.pop("ig_error", None)
                rec["ig_media"] = ig
        for key, t, plus in (ig_todo if ig else []):
            if t == "story" and not ig.get("story_ok", [False, False])[0 if key == "ig_story1" else 1]:
                r = rec.setdefault(key, {"tries": 0})
                if not r.get("error"):
                    r["error"] = "切ったストーリーが見本と違う"
                    r["tries"] = MAX_TRIES  # 違う絵は出さない
                    append_log(day, f"4コマ 第{k.get('episode', '?')}話 {key} 出さない：切った絵が見本と違う（wsrv.nl の切り方を確かめる）")
                continue
            imgs = ig["slides"] if key == "ig_slides" else [ig["stories"][0 if key == "ig_story1" else 1]]
            jobs.append((key, "instagram", {"images": imgs, "ig_type": t, "alt": alt}, when + timedelta(minutes=plus)))
    for s, svc, media, at in jobs:
        r = rec.setdefault(s, {"tries": 0})
        r["tries"] = r.get("tries", 0) + 1
        texts = [k["text"]]
        # おでかけ4コマ（10/24〜）：X・Threads は2つ目に公式ページのURL（text2）とHPの1行を付ける。インスタは1つだけ
        if svc in ("twitter", "threads") and URL_RE.search(k.get("text2") or ""):
            texts = with_page([k["text"], k["text2"].strip()], svc, cfg, slot, due)
        try:
            p = buffer_create(cfg["channels"][svc], svc, texts, at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                              topic=(k.get("topic") or "漫画") if svc == "threads" else None, **media)
            r.update({"id": p["id"], "kind": "4コマ", "at": at.strftime("%H:%M"), "texts": texts,
                      "topic": k.get("topic") or "漫画", "media": media, "svc": svc})
            r.pop("error", None)
            late = "" if when == due else f"（遅れたので {when.strftime('%H:%M')} に）"
            append_log(day, f"4コマ 第{k.get('episode', '?')}話 {s} 予約OK{late}")
        except BufferError as e:
            r["error"] = str(e)[:200]
            append_log(day, f"4コマ 第{k.get('episode', '?')}話 {s} 予約×（{r['tries']}回目）：{str(e)[:150]}")
    return True


def book_extra(cfg, state, now):
    """1回だけの画像投稿（10/25 オーナー「新しいHPの紹介をうさぎにさせたい。3媒体に投稿したい」）。

    extra/日付.json：{"posts": [{"key": "HP紹介", "slot": "21:30", "x": [文1, 文2], "threads": [文1, 文2],
      "instagram": "インスタの文", "images": [誰でも開ける画像URL, ...], "topic": "おでかけ"}]}
    燈がオーナーのOKをもらってから置く。X・Threads・Instagram（スライド）に画像付きで出す。"""
    day = now.date().isoformat()
    ex = load_json(path("extra", f"{day}.json"))
    changed = False
    for e in (ex or {}).get("posts", []):
        slot, imgs = e.get("slot"), e.get("images") or []
        if not slot or not imgs:
            continue
        due = datetime.fromisoformat(f"{day}T{slot}").replace(tzinfo=JST)
        mins = (due - now).total_seconds() / 60
        if (mins > LEAD_MIN or mins < -LATE_MIN) and not e.get("cancel"):
            continue
        rec = state.setdefault(f"{day} 1回 {e.get('key', slot)}", {})
        if e.get("cancel"):  # オーナーが取り消した：予約済みの物を消し、もう予約しない
            for svc, r in rec.items():
                if isinstance(r, dict) and r.get("id") and not r.get("cancelled"):
                    try:
                        delete_post(r["id"])
                        r["cancelled"] = True
                        append_log(day, f"{slot} {svc} 取り消した［1回：{e.get('key', '')}］")
                    except BufferError as err:
                        append_log(day, f"{slot} {svc} 取り消せない［1回：{e.get('key', '')}］：{str(err)[:150]}")
                    changed = True
            continue
        todo = [(svc, e.get(k)) for svc, k in (("twitter", "x"), ("threads", "threads"), ("instagram", "instagram"))
                if svc in cfg["channels"] and e.get(k)
                and not rec.get(svc, {}).get("id") and rec.get(svc, {}).get("tries", 0) < MAX_TRIES]
        if not todo:
            continue
        bad = media_problem(imgs[0], "image")
        if bad:
            if rec.get("media_error") != bad:
                append_log(day, f"{slot} {e.get('key', '')} 予約できない：{bad}")
            rec["media_error"] = bad
            changed = True
            continue
        rec.pop("media_error", None)
        when = due if mins >= 3 else now + timedelta(minutes=3)
        for svc, texts in todo:
            texts = [texts] if isinstance(texts, str) else list(texts)
            r = rec.setdefault(svc, {"tries": 0})
            r["tries"] = r.get("tries", 0) + 1
            pics = imgs[:4] if svc == "twitter" else imgs[:10]
            try:
                p = buffer_create(cfg["channels"][svc], svc, texts, when.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                                  topic=e.get("topic") if svc == "threads" else None,
                                  images=pics, ig_type="post" if svc == "instagram" else None, alt=e.get("alt", ""))
                r.update({"id": p["id"], "kind": "1回", "at": when.strftime("%H:%M"), "texts": texts, "svc": svc,
                          "media": {"images": pics, "alt": e.get("alt", ""), "ig_type": "post" if svc == "instagram" else None}})
                r.pop("error", None)
                append_log(day, f"{slot} {svc} 予約OK［1回：{e.get('key', '')}］")
            except BufferError as err:
                r["error"] = str(err)[:200]
                append_log(day, f"{slot} {svc} 予約×［1回：{e.get('key', '')}］（{r['tries']}回目）：{str(err)[:150]}")
        changed = True
    return changed


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
            day, slot = key.split(" ", 1)  # 1回だけの投稿は「日付 1回 名前」で空白が多い
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
                        svc = r.get("svc", s)
                        p = buffer_create(cfg["channels"][svc], svc, texts, when.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                                          topic=r.get("topic") if svc == "threads" else None, **(r.get("media") or {}))
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
        if not state.get(k) and not state.get(f"{day} 4コマ") and now.hour < 12:
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
        print(st, len(ps))
        for p in sorted(ps, key=lambda p: p["dueAt"] or ""):  # 4コマなど、手で出た物も見分けられるよう全部出す
            print("  ", p["channelService"], p["dueAt"], (p["text"] or "")[:30].replace("\n", " "))
    for st in ("scheduled", "draft"):  # これから出る予約・下書き（手で足された物がないか）
        try:
            ps = buffer_posts(cfg, [st], now - timedelta(days=2), now + timedelta(days=3))
            print(st, len(ps), [(p["channelService"], p["dueAt"], (p["text"] or "")[:30]) for p in ps[:20]])
        except BufferError as e:
            print(st, "×", str(e)[:150])
    return 0


def koma4_test(image_url):
    """絵のURLでBufferに「下書き」を作れるかを試し、すぐ消す（公開はしない）。"""
    from lib import buffer_gql
    cfg = load_json(path("config.json"))
    print("URLの確認:", media_problem(image_url, "image") or "OK")
    due = (now_jst() + timedelta(days=2)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    for s in ("twitter", "threads"):
        try:
            p = buffer_create(cfg["channels"][s], s, ["4コマの絵のテスト（下書き・すぐ消す）", "続きのテスト https://usagi-life-notes.pages.dev/"], due,
                              topic="漫画" if s == "threads" else None, draft=True, image=image_url, alt="テスト")
            print(s, "下書きOK", p)
            try:
                r = buffer_gql('mutation($i:DeletePostInput!){deletePost(input:$i){__typename}}', {"i": {"id": p["id"]}})
                print(s, "消した", r)
            except Exception as e:
                print(s, "消せない（Bufferの下書きから手で消す）", str(e)[:200])
        except Exception as e:
            print(s, "×", str(e)[:300])
    if "instagram" not in cfg["channels"]:
        return 0
    # Instagram：切った絵が本当に絵として返るか（大きさも）を見て、スライドとストーリーの下書きを作って消す
    try:
        ig = koma4_instagram_media(image_url, fetch_image(image_url))
    except Exception as e:
        print("Instagram用に切れない ×", str(e)[:300])
        return 1
    print("コマの位置:", ig["how"], ig["boxes"])
    full = fetch_image(image_url)
    sok = stories_ok(ig, full)
    print("ストーリーが見本と同じか:", sok, "違い", ig.get("story_diff"), f"（{STORY_DIFF_MAX}以下で合格）")
    bad = 0
    for u, want in [(u, tuple(ig["boxes"][0][2:])) for u in ig["slides"]] + [(u, (1080, 1920)) for u in ig["stories"]]:
        try:
            im = fetch_image(u)
            good = im.size == want
            print("切った絵", im.size, "OK" if good else "× 大きさが違う", u[:120])
            bad += not good
        except Exception as e:
            print("切った絵 × 開けない", str(e)[:150], u[:120])
            bad += 1
    for t, imgs in (("story", ig["stories"][:1]), ("post", ig["slides"])):
        try:
            p = buffer_create(cfg["channels"]["instagram"], "instagram", ["4コマのテスト（下書き・すぐ消す）"], due,
                              draft=True, images=imgs, ig_type=t, alt="テスト")
            print("instagram", t, "下書きOK", p)
            try:
                r = buffer_gql('mutation($i:DeletePostInput!){deletePost(input:$i){__typename}}', {"i": {"id": p["id"]}})
                print("instagram", t, "消した", r)
            except Exception as e:
                print("instagram", t, "消せない（Bufferの下書きから手で消す）", str(e)[:200])
        except Exception as e:
            print("instagram", t, "×", str(e)[:300])
            bad += 1
    bad += sok.count(False)
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--koma4-test":
        sys.exit(koma4_test(sys.argv[2]))
    if len(sys.argv) > 1 and sys.argv[1] == "--sent-test":
        sys.exit(sent_test())
    if len(sys.argv) > 2 and sys.argv[1] == "--test":
        sys.exit(test(sys.argv[2]))
    sys.exit(run())
