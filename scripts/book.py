"""予約係。1時間おきに動き、これから2時間半以内に出す投稿を Buffer に予約する。

・PRは予約する直前に楽天に「今も売っているか・同じ商品か」を聞き、楽天が返す正式なリンクを入れる。
  だめなら、その場で代わりの通常投稿（fallback）を予約する。
・期限（until）を過ぎた投稿も代わりにする。
・同じ投稿を2回予約しない（state/booked.json に記録）。
・何をしたかは log/日付.md に1行ずつ書く。燈は毎晩これを読む。

テスト：python scripts/book.py --test <楽天の商品ページURL>
  → その商品のリンクを楽天から受け取り、X・Threads に「下書き」を1本ずつ作る（公開はしない）。
"""
import json
import os
import re
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
LONG_RE = re.compile(r"character limit|too long|exceeds|文字数", re.I)


def post_sig(post):
    """予定表の文の指紋（直されたかを見分ける）。"""
    import hashlib
    body = json.dumps([post.get("x"), post.get("threads"), post.get("fallback"), post.get("link")],
                      ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(body.encode()).hexdigest()[:12]
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
    # 木・金・土は「今週末に行ける」の数で誘う（10/26 オーナー「サイトに誘導が大事」）
    # 「今週末に行ける」は使わない（10/26 オーナー「休みが平日の人もいる」）
    if reg and n.get(reg, 0) >= 3:
        return f"{reg}のおでかけ{n[reg]}件、公式ページつきの一覧：{url}"
    if n.get("関東", 0) >= 3:  # 10/26 HPは関東だけ（オーナー「関東おでかけリスト」）
        return f"関東のおでかけ{n['関東']}件、公式ページつきの一覧：{url}"
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


def rebook_requests(cfg, state, now):
    """state/rebook.json に書いた予約の直し（1行目・Threadsのトピック）を、予約し直しで入れる（10/27 月の書き方を今日の分から）。
    形：[{"day": "YYYY-MM-DD", "slot": "HH:MM", "svc": "threads"|"twitter", "first_line": "新しい1行目", "topic": "東京", "texts": ["全部入れ替える時の文", "…"]}]
    新しい予約が作れてから古い方を消す。出る25分前を切った物・もう出た物・字数をこえる物には触らない。終わった行は消す。"""
    from lib import threads_len, x_weight
    reqs = load_json(path("state", "rebook.json"), [])
    if not reqs:
        return False
    waiting = {p["id"] for p in buffer_posts(cfg, ["scheduled"], now, now + timedelta(hours=40))}
    left = []
    for q in reqs:
        day, slot, s = q.get("day", ""), q.get("slot", ""), q.get("svc", "")
        r = (state.get(f"{day} {slot}") or {}).get(s)
        tag = f"{slot} {s} 直しの予約し直し"
        if not isinstance(r, dict) or not r.get("id") or r["id"] not in waiting:
            append_log(day, f"{tag}：予約中の物がない（やめた）")
            continue
        try:
            due = datetime.fromisoformat(f"{day}T{r.get('at') or slot}").replace(tzinfo=JST)
        except ValueError:
            continue
        if due - now < timedelta(minutes=25):
            append_log(day, f"{tag}：出る25分前を切った（元のまま）")
            continue
        texts = list(r.get("texts") or [])
        if not texts:
            continue
        if q.get("texts"):  # 文を全部入れ替える（10/30 長すぎて代わりの文で出そうになったPRを、縮めた文で入れ直す）
            texts = list(q["texts"])
        if q.get("link") and any("{{LINK}}" in t for t in texts):  # 11/1 通常の枠をPRに入れ替える（オーナー「何がなんでも売上上げろ」）
            res = resolve_link(q["link"], texts)
            if not res.get("ok"):
                append_log(day, f"{tag}：PRのリンク×（元のまま）：{str(res.get('why', ''))[:120]}")
                continue
            texts = [t.replace("{{LINK}}", res["link"]) for t in texts]
        if q.get("first_line"):
            rest = texts[0].split("\n", 1)
            texts[0] = q["first_line"] + ("\n" + rest[1] if len(rest) > 1 else "")
        topic = q.get("topic") or r.get("topic")
        if s == "twitter" and any(x_weight(t) > 280 for t in texts):
            append_log(day, f"{tag}：Xの字数をこえる（元のまま）")
            continue
        if s == "threads" and any(threads_len(t) > 500 for t in texts):
            append_log(day, f"{tag}：Threadsの字数をこえる（元のまま）")
            continue
        if texts == r["texts"] and topic == r.get("topic"):
            continue
        due_iso = due.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        try:
            p = buffer_create(cfg["channels"][s], s, texts, due_iso, topic=topic if s == "threads" else None)
        except BufferError as e:
            append_log(day, f"{tag}×（元の予約のまま）：{str(e)[:120]}")
            continue
        try:
            delete_post(r["id"])
        except BufferError as e:
            try:
                delete_post(p["id"])
                append_log(day, f"{tag}：古い予約を消せない（元のまま）：{str(e)[:100]}")
            except BufferError:
                append_log(day, f"{tag}：×2本予約のおそれ（{r['id']} と {p['id']}）。燈が片方を消す")
            continue
        r.update({"id": p["id"], "texts": texts, "topic": topic})
        append_log(day, f"{tag}OK" + (f"（1行目：{q['first_line'][:40]}）" if q.get("first_line") else "") + (f"（トピック：{topic}）" if q.get("topic") else ""))
    save_json(path("state", "rebook.json"), left)
    return True


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
            # 予定表の文が直されたら、×で止まっていた回数を戻してすぐ予約し直す（10/28 9:15 Threads が3回×のまま止まった）
            sig = post_sig(post)
            for s in SERVICES:
                r0 = rec.get(s)
                if r0 and not r0.get("id") and r0.get("tries", 0) and r0.get("sig") and r0.get("sig") != sig:
                    append_log(day, f"{slot} {s} 文が直されたので予約し直す（前は{r0['tries']}回×）")
                    rec[s] = {"tries": 0}
            todo = [s for s in SERVICES if s in cfg["channels"]
                    and not rec.get(s, {}).get("id") and rec.get(s, {}).get("tries", 0) < MAX_TRIES
                    and not tabi_replaced(state, day, slot, s)]
            if not todo:
                continue
            xs, ths, topic, kind, why = choose(post, day, now)
            if xs is not None:
                topic = threads_topic(topic, (ths or [""])[0], due)
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
                    r["sig"] = sig
                    append_log(day, f"{slot} {s} 予約×（{r['tries']}回目）：{str(e)[:150]}")
                    # 長すぎる×は、同じ文で何度やっても通らない。代わりの文（fallback）でその場で予約する
                    fb = post.get("fallback")
                    if fb and kind != "代わり" and LONG_RE.search(str(e)):
                        fb_texts = with_page(fb["x"] if s == "twitter" else fb["threads"], s, cfg, slot, due)
                        try:
                            p = buffer_create(cfg["channels"][s], s, fb_texts, due_iso,
                                              topic=threads_topic(fb.get("topic") or topic, (fb["threads"] or [""])[0], due)
                                              if s == "threads" else None)
                            r.update({"id": p["id"], "kind": "代わり", "at": when.strftime("%H:%M"),
                                      "texts": fb_texts, "topic": topic})
                            r.pop("error", None)
                            append_log(day, f"{slot} {s} 予約OK［代わり］（文が長すぎたので代わりの文で）")
                        except BufferError as e2:
                            append_log(day, f"{slot} {s} 代わりの文も予約×：{str(e2)[:150]}")
            changed = True
    try:
        changed |= refresh_page(cfg, state, now)
    except BufferError as e:
        append_log(now.date().isoformat(), f"ページのURLの予約し直し×：{str(e)[:150]}")
    try:
        changed |= rebook_requests(cfg, state, now)
    except BufferError as e:
        append_log(now.date().isoformat(), f"直しの予約し直し×：{str(e)[:150]}")
    try:
        changed |= book_koma4(cfg, state, now)
    except BufferError as e:
        append_log(now.date().isoformat(), f"4コマ 予約×：{str(e)[:150]}")
    try:
        changed |= book_outing_reel(cfg, state, now)
        changed |= book_hp_reel(cfg, state, now)
    except BufferError as e:
        append_log(now.date().isoformat(), f"おでかけリール 予約×：{str(e)[:150]}")
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


GENERAL_TOPICS = {"", "おでかけ", "漫画", "関東", "関東おでかけ"}


def threads_topic(topic, text, due):
    """Threadsのトピック（10/27 オーナー「月と同じにしてくれ」）。
    「おでかけ」のような大きい言葉は全国の人の欄に混ざり、行ける関東の人に届きにくい。
    月はおでかけを府県名で出しているので、燈も文から都県が分かれば都県名（東京・群馬など）にする。
    節約・温泉・旅行など、場所でない話題のトピックはそのまま。"""
    t = (topic or "").strip()
    if t not in GENERAL_TOPICS:
        return topic
    try:
        import page
        e = page.spot_match(text, due)
        pref = page._pref(e) if e else page._pref({"title": text, "bullets": []})
    except Exception:
        pref = ""
    if pref in ("東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬"):
        return pref
    return topic or "おでかけ"


KOMA4_SERVICES = ("twitter", "threads", "instagram")
IG_PROFILE = "くわしい場所と公式ページは、プロフィールのリンク「関東おでかけリスト」からどうぞ。"  # 10/26 HPは関東だけ
IG_HEAD = "プロフィールのリンク"  # 予約済みの文に付いているかを見分ける


IG_TAG_WORDS = [("イルミ", "イルミネーション"), ("ライトアップ", "ライトアップ"), ("紅葉", "紅葉"), ("温泉", "温泉"),
                ("クリスマスマーケット", "クリスマスマーケット"), ("カフェ", "カフェ"), ("無料", "無料イベント")]


def ig_tags(k, due):
    """インスタのタグ（10/26 オーナー「インスタもタグ効果あるならとか考えて工夫して」）。
    インスタは探す人がタグから来るので、場所（都道府県＋おでかけ）・地域・中身の言葉・シリーズで5つまで。
    夜の回が koma4 の ig_tags に場所のタグ（例 "#二条城"）を書いた時は、それを先に入れる。"""
    tags = [t if t.startswith("#") else "#" + t for t in (k.get("ig_tags") or [])][:2]
    text = k.get("text", "")
    try:
        import page
        e = page.spot_match(text, due)
        pref = page._pref(e) if e else page._pref({"title": text, "bullets": []})
        reg = page.region(pref)
    except Exception:
        pref = reg = ""
    if pref:
        tags.append(f"#{pref}おでかけ")
    if reg:
        tags.append(f"#{reg}おでかけ")
    for w, tag in IG_TAG_WORDS:
        if w in text:
            tags.append("#" + tag)
            break
    tags.append("#旅先4コマ" if "旅先4コマ" in text else "#おでかけ4コマ")
    return " ".join(dict.fromkeys(tags[:5]))


# 11/2 オーナー「毎日のリールの説明文にも、HPの紹介を1行足す（HPにある機能だけ・日替わり）」
# 11/2 に本物のページを開いて確かめた機能だけ。ページが変わったら直す
HP_LINES = (
    "HPでは、街の名前を入れると、その街のおでかけとイルミネーションがまとめて出ます。",
    "HPの「いまから行ける おでかけ」は、いる場所といまの時刻から、きょう開いている所を近い順に並べます。",
    "HPの「泊まりで行くおでかけ」は、関東の少し遠いおでかけと、近くの評価の高い宿をまとめています。",
    "HPの「いまが買い時の日用品」は、楽天のよく買われる毎日の物の値段を、毎日記録しています。",
    "HPのふるさと納税のページは、返礼品を寄付1万円あたりの量に直して比べています。",
    "HPのおでかけリストは、地図でも探せて、近くの宿も見られます。",
    "HPのおかいものリストは、3つ以上を数字で比べて選んだ、暮らしの物です。",
)


def hp_line(due):
    """日替わりのHPの紹介1行（同じ日の2本のリールは同じ行）。"""
    return HP_LINES[due.toordinal() % len(HP_LINES)]


def ig_profile(texts, due):
    """インスタの文の最後の定型文（10/26 オーナー「ちゃんと考えて定型文つくろ」「みてもどこで詳しく書いてるか分かるわけない」）。
    インスタは文のリンクを押せないので、見た人が次にどこを押せばいいかを書く。
    その催しがHPに載っている時：1行目＝この催しの地図と公式ページの場所、2行目＝同じページにほかに何があるか（件数は書かない）。
    載っていない時（旅先4コマなど）：HPに何があるかだけ（載っていない物を「載っている」と書かない）。"""
    try:
        import page
        reg = page.spot_region(" ".join(texts), due)
        n = page.spot_counts(due)
    except Exception:
        return IG_PROFILE
    if reg and n.get(reg, 0) >= 2:  # 件数は書かない（10/26 オーナー「件数まではいいんじゃない？」）
        return f"くわしい場所と公式ページは、プロフィールのリンク「関東おでかけリスト」からどうぞ。{reg}のおでかけを、ほかにもまとめています。"  # 10/26 オーナーが案10に決定。HPの名前を入れた（月のやり方）
    return IG_PROFILE
# Instagram の毎日の4コマ（10/23 オーナー「OK」）：スライド4枚（8:00）とストーリー2枚（8:05・8:15）。動画の日はリールも
# 10/31 7:30のリール・8:00のスライドとストーリー2枚が30分に4本重なり、スライドとストーリー2枚目がエラー（10/29もスライドがスパムの印）→間をあける
# 11/1 ストーリーは離して出た。スライドは10/29・10/31・11/1とも「スパムの疑い」＝8:00のリールと同じ時刻・同じ文だったため→3時間あけ、1行目を変える
IG_EXTRA = (("ig_slides", "post", 180), ("ig_story1", "story", 5), ("ig_story2", "story", 15))
IG_SLIDES_HEAD = "今朝の4コマを、1コマずつめくって読めます。"


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


# 雫の漫画は1日2本まで（10/25 オーナー「雫をよく使い漫画投稿、お出かけ漫画投稿増やしていい」）。
# 毎日の 8:00 おでかけ4コマ（koma4/D.json）と、水・土の旅先4コマ（koma4/D-tabi.json、12:15）。
KOMA_FILES = (("", "4コマ"), ("-tabi", "旅4コマ"))


def book_koma4(cfg, state, now):
    changed = False
    for suffix, label in KOMA_FILES:
        changed |= _book_koma(cfg, state, now, suffix, label)
    return changed


def tabi_replaced(state, day, slot, svc):
    """旅先4コマがこの時刻の文の投稿の代わりに出るなら True（文の投稿は出さない）。"""
    k = load_json(path("koma4", f"{day}-tabi.json")) or {}
    if k.get("replace") != slot:
        return False
    return bool(state.get(f"{day} 旅4コマ", {}).get(svc, {}).get("id"))


def _replace_text_post(state, day, k):
    """旅先4コマを予約できたら、同じ時刻の文の投稿（予定表の replace の枠）を消す。消せなければ文の投稿は残す（旅4コマを消す）。"""
    slot = k.get("replace")
    if not slot:
        return False
    changed = False
    trec = state.setdefault(f"{day} 旅4コマ", {})
    rec = state.get(f"{day} {slot}", {})
    for svc in SERVICES:
        r, t = rec.get(svc) or {}, trec.get(svc) or {}
        if not t.get("id") or not r.get("id") or r.get("seen") or r.get("replaced"):
            continue
        try:
            delete_post(r["id"])
            r["replaced"], r["seen"] = True, "旅4コマに替えた"
            append_log(day, f"{slot} {svc} 文の投稿を消した（旅4コマ 第{k.get('episode', '?')}話に替えた）")
        except BufferError as e:
            try:  # 2本出ないよう、旅4コマの方を消して文の投稿を残す
                delete_post(t["id"])
                t["id"], t["tries"], t["error"] = None, MAX_TRIES, "文の投稿を消せない"
                append_log(day, f"{slot} {svc} 文の投稿を消せないので、旅4コマを消して文の投稿のまま：{str(e)[:80]}")
            except BufferError:
                append_log(day, f"{slot} {svc} ×2本出るおそれ（文 {r['id']} と旅4コマ {t['id']}）")
        changed = True
    return changed


def _book_koma(cfg, state, now, suffix="", label="4コマ"):
    """雫が描いた4コマを予約する（10/23から。雫はBufferを使わない）。

    koma4/日付.json：{"slot": "08:00", "episode": 16, "text": "投稿文", "image_url": "…", "video_url": "…"}
    text は燈の夜の回が書く。image_url・video_url は朝の4コマ係（燈）が、雫が保存した絵から入れる。
    X・Threads は画像。Instagram は、縦長1:3の絵がそのまま載らないので、1コマずつ切ったスライド4枚と、
    2コマずつのストーリー2枚を毎日出す（切るのは wsrv.nl。Bufferはその切ったURLを取りに行く）。動画がある日はリールも出す。
    """
    day = now.date().isoformat()
    k = load_json(path("koma4", f"{day}{suffix}.json"))
    if not k or not k.get("text") or not k.get("image_url"):
        return False
    slot = k.get("slot") or "08:00"
    due = datetime.fromisoformat(f"{day}T{slot}").replace(tzinfo=JST)
    mins = (due - now).total_seconds() / 60
    late_ok = k.get("late_until") and now.strftime("%H:%M") < k["late_until"]  # 手で出し直すとき（燈が入れる）
    if mins > LEAD_MIN or (mins < -6 * 60 and not late_ok):  # 4コマは遅れても、その日の昼までは出す
        return False
    key = f"{day} {label}"
    rec = state.setdefault(key, {})
    def open_(s):
        return not rec.get(s, {}).get("id") and rec.get(s, {}).get("tries", 0) < MAX_TRIES
    # リールをインスタへ直接（曲つき）出す設定の時は、Buffer でリールを出さない（2本出さない）。直接が失敗した時だけ Buffer で出す
    import igreel
    direct = igreel.direct_ready(cfg) and rec.get("ig_direct", {}).get("state") != "failed"
    todo = [s for s in KOMA4_SERVICES if s in cfg["channels"] and open_(s)
            and (s != "instagram" or (k.get("video_url") and k.get("video_ok") and not direct))]  # リールは機械の確認（videocheck.py）に通った動画だけ
    reel_day = bool(k.get("video_url") and k.get("video_ok"))  # 11/1 オーナー「リール投稿あるから4枚スライドなしにしようか」→リールの日はスライドを出さない
    ig_todo = [e for e in IG_EXTRA if "instagram" in cfg["channels"] and open_(e[0]) and not (e[0] == "ig_slides" and reel_day)]
    if not todo and not ig_todo:
        return _replace_text_post(state, day, k) if suffix == "-tabi" else False
    bad = media_problem(k["image_url"], "image") or (k.get("video_ok") and media_problem(k["video_url"], "video"))
    if bad:
        if not rec.get("media_error"):
            append_log(day, f"{label} 第{k.get('episode', '?')}話 予約できない：{bad}")
        rec["media_error"] = bad
        return True
    rec.pop("media_error", None)
    when = due if mins >= 3 else now + timedelta(minutes=3)  # 7:50の直しでも8:00に間に合わせる
    alt = f"{label}漫画 第{k.get('episode', '')}話"
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
                    append_log(day, f"{label} 第{k.get('episode', '?')}話 Instagram 予約できない：{bad}")
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
                    append_log(day, f"{label} 第{k.get('episode', '?')}話 {key} 出さない：切った絵が見本と違う（wsrv.nl の切り方を確かめる）")
                continue
            imgs = ig["slides"] if key == "ig_slides" else [ig["stories"][0 if key == "ig_story1" else 1]]
            jobs.append((key, "instagram", {"images": imgs, "ig_type": t, "alt": alt}, when + timedelta(minutes=plus)))
    for s, svc, media, at in jobs:
        if s == "instagram" and media.get("video") and os.path.exists(igreel.BGM):
            # Buffer で出すリールは、雫の曲をオーナーのフリー音源に替えた動画にする（10/29）。替えられない時は雫の動画のまま
            bg = rec.get("bgm_video") or {}
            if bg.get("src") != media["video"]:
                url, err = igreel.host_silent(media["video"], f"{day}-bgm-{k.get('episode', 'x')}", bgm=True)
                bg = {"src": media["video"], "url": url, "error": err}
                rec["bgm_video"] = bg
                append_log(day, f"{label} 第{k.get('episode', '?')}話 リールの曲をオーナーの曲に替えた" if url
                           else f"{label} 第{k.get('episode', '?')}話 リールの曲を替えられない（雫の曲のまま）：{err}")
            if bg.get("url"):
                media = dict(media, video=bg["url"])
        r = rec.setdefault(s, {"tries": 0})
        r["tries"] = r.get("tries", 0) + 1
        texts = [k["text"]]
        # おでかけ4コマ（10/24〜）：X・Threads は2つ目に公式ページのURL（text2）とHPの1行を付ける。インスタは1つだけ
        if svc in ("twitter", "threads") and URL_RE.search(k.get("text2") or ""):
            texts = with_page([k["text"], k["text2"].strip()], svc, cfg, slot, due)
        elif svc == "instagram" and media.get("ig_type") != "story" and IG_HEAD not in k["text"]:
            texts = [k["text"].rstrip() + "\n\n" + ig_profile([k["text"]], due) + ("\n" + hp_line(due) if media.get("video") else "") + "\n\n" + ig_tags(k, due)]
            if media.get("ig_type") == "post":  # スライドはリールと同じ文にしない（同じ文が続くとスパムの印）
                texts = [IG_SLIDES_HEAD + "\n\n" + texts[0]]  # インスタの文はリンクを押せないので、HPへの道を1行（10/26 オーナー「プロフィールリンクに詳細あるよね？」）
        try:
            p = buffer_create(cfg["channels"][svc], svc, texts, at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                              topic=threads_topic(k.get("topic") or "漫画", k.get("text", ""), due) if svc == "threads" else None, **media)
            r.update({"id": p["id"], "kind": "4コマ", "at": at.strftime("%H:%M"), "texts": texts,
                      "topic": threads_topic(k.get("topic") or "漫画", k.get("text", ""), due), "media": media, "svc": svc})
            r.pop("error", None)
            late = "" if when == due else f"（遅れたので {when.strftime('%H:%M')} に）"
            append_log(day, f"{label} 第{k.get('episode', '?')}話 {s} 予約OK{late}")
        except BufferError as e:
            r["error"] = str(e)[:200]
            append_log(day, f"{label} 第{k.get('episode', '?')}話 {s} 予約×（{r['tries']}回目）：{str(e)[:150]}")
    if suffix == "-tabi":
        _replace_text_post(state, day, k)
    return True


# 関東のおでかけリール（10/30〜。10/29 オーナー「燈のインスタにも月と同じおでかけ動画」「リールは毎日2本。
# 関西版の関東の版の後に、同じおでかけ先で4コマリール」）。燈の夜の回が reel/D.json を置くと、outing-reel.yml が
# 曲つきの動画を作って Cloudflare に置き、URL を reel/out/D.json に書く。ここではインスタのリールに予約するだけ。
OUTING_KICKER = "街の調査で見つけた、関東おでかけリスト"  # 10/29 オーナー決定（「代わりに調べた」は変なのでやめた）


def book_outing_reel(cfg, state, now):
    day = now.date().isoformat()
    spec = load_json(path("reel", f"{day}.json"))
    if not spec or "instagram" not in cfg["channels"]:
        return False
    if os.path.exists(path("reel-hp", f"{day}.json")):  # 11/2 HPリールの日はおでかけリールを出さない（翌週に回す）
        return False
    slot = spec.get("time") or "07:30"
    due = datetime.fromisoformat(f"{day}T{slot}").replace(tzinfo=JST)
    mins = (due - now).total_seconds() / 60
    if mins > LEAD_MIN or mins < -4 * 60:
        return False
    top = state.setdefault(f"{day} おでかけリール", {})
    rec = top.setdefault("instagram", {"tries": 0})  # ほかの投稿と同じ形（state[日 枠][媒体]）にして、出たかの確認・数字にも乗せる
    if rec.get("id") or rec.get("tries", 0) >= MAX_TRIES:
        return False
    made = load_json(path("reel", "out", f"{day}.json")) or {}  # outing-reel.yml が動画を作って置いた URL
    if made.get("url") and not top.get("url"):
        top["url"] = made["url"]
    mp4 = path("reel", f"{day}.mp4")
    if not top.get("url") and not os.path.exists(mp4):
        if not rec.get("error"):
            rec["error"] = made.get("error") or "動画がない"
            append_log(day, f"おでかけリール 予約できない：{rec['error']}（reel/out/{day}.json。outing-reel.yml を見る）")
            return True
        return False
    import igreel
    if not top.get("url"):
        url, err = igreel.host_bytes(open(mp4, "rb").read(), f"{day}-odekake-{now.strftime('%H%M%S')}")
        if not url:
            rec["tries"] = rec.get("tries", 0) + 1
            rec["error"] = err
            append_log(day, f"おでかけリール 動画を置けない（{rec['tries']}回目）：{err}")
            return True
        top["url"] = url
    cap = (spec.get("caption") or "").strip()
    if not cap.startswith(OUTING_KICKER):
        cap = OUTING_KICKER + "\n" + cap
    if IG_HEAD not in cap:
        cap = cap.rstrip() + "\n\nくわしくはプロフィールのリンクの「関東おでかけリスト」から"
    if not any(l in cap for l in HP_LINES):
        cap = cap.rstrip() + "\n" + hp_line(due)
    tags = " ".join(spec.get("ig_tags") or [])
    if tags and tags not in cap:
        cap += "\n\n" + tags
    when = due if mins >= 3 else now + timedelta(minutes=3)
    rec["tries"] = rec.get("tries", 0) + 1
    try:
        p = buffer_create(cfg["channels"]["instagram"], "instagram", [cap], when.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                          video=top["url"], ig_type="reel", alt=f"関東おでかけリール {spec.get('text', {}).get('place', '')}")
        rec.update({"id": p["id"], "kind": "おでかけリール", "at": when.strftime("%H:%M"), "texts": [cap], "svc": "instagram"})
        rec.pop("error", None)
        append_log(day, f"おでかけリール instagram 予約OK（{when.strftime('%H:%M')}）")
    except BufferError as e:
        rec["error"] = str(e)[:200]
        append_log(day, f"おでかけリール instagram 予約×（{rec['tries']}回目）：{str(e)[:150]}")
    return True


def book_hp_reel(cfg, state, now):
    """週1本のHPの紹介リール（11/2 オーナー「29秒のリールで、HPの本物の画面を順番に見せる」「夕方の枠と入れ替えて出す」）。
    reel-hp/D.json（docs/hp-reel.md）→ hp-reel.yml が動画を作り reel-hp/out/D.json に URL → ここで夕方（time、ふつう18:00）に予約。"""
    day = now.date().isoformat()
    spec = load_json(path("reel-hp", f"{day}.json"))
    if not spec or "instagram" not in cfg["channels"]:
        return False
    slot = spec.get("time") or "18:00"
    due = datetime.fromisoformat(f"{day}T{slot}").replace(tzinfo=JST)
    mins = (due - now).total_seconds() / 60
    if mins > LEAD_MIN or mins < -4 * 60:
        return False
    top = state.setdefault(f"{day} HPリール", {})
    rec = top.setdefault("instagram", {"tries": 0})
    if rec.get("id") or rec.get("tries", 0) >= MAX_TRIES:
        return False
    made = load_json(path("reel-hp", "out", f"{day}.json")) or {}
    if not made.get("url"):
        if not rec.get("error"):
            rec["error"] = made.get("error") or "動画がない"
            append_log(day, f"HPリール 予約できない：{rec['error']}（reel-hp/out/{day}.json。hp-reel.yml を見る）")
            return True
        return False
    cap = (spec.get("caption") or "").strip()
    if IG_HEAD not in cap:
        cap = cap.rstrip() + "\n\nくわしくはプロフィールのリンクから"
    tags = " ".join(spec.get("ig_tags") or [])
    if tags and tags not in cap:
        cap += "\n\n" + tags
    when = due if mins >= 3 else now + timedelta(minutes=3)
    rec["tries"] = rec.get("tries", 0) + 1
    try:
        p = buffer_create(cfg["channels"]["instagram"], "instagram", [cap], when.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                          video=made["url"], ig_type="reel", alt="HPの紹介リール")
        rec.update({"id": p["id"], "kind": "HPリール", "at": when.strftime("%H:%M"), "texts": [cap], "svc": "instagram"})
        rec.pop("error", None)
        append_log(day, f"HPリール instagram 予約OK（{when.strftime('%H:%M')}）")
    except BufferError as e:
        rec["error"] = str(e)[:200]
        append_log(day, f"HPリール instagram 予約×（{rec['tries']}回目）：{str(e)[:150]}")
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
    start, end = now - timedelta(hours=12), now - timedelta(minutes=20)  # 10/26 定時起動が8時間あき、13:45・15:15の「出た」を見落とした
    waiting = []
    for key, rec in state.items():
        if " " not in key:
            continue
        for s, r in rec.items():
            if not isinstance(r, dict) or not r.get("id") or r.get("seen") or r.get("cancelled"):
                continue  # 取り消した投稿は「出たか」を見ない（10/25 取り消し済みを出し直そうとした）
            at = r.get("at") or key.split(" ")[1]
            try:
                due = datetime.fromisoformat(f"{key.split(' ')[0]}T{at}").replace(tzinfo=JST)
            except ValueError:
                continue
            if start <= due <= end:
                waiting.append((key, s, r, due))
    if waiting:
        # 「出た」と「エラー」を1回でまとめて聞く（Bufferは30日で3,000回まで。10/25 回数を半分に）
        got = buffer_posts(cfg, ["sent", "error"], start - timedelta(hours=1), end)
        sent = {p["id"] for p in got if (p.get("status") or "sent").lower() == "sent"}
        errs = {p["id"] for p in got if (p.get("status") or "").lower() == "error"}
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
                ig = r.get("svc", s).startswith("ig") or r.get("svc", s) == "instagram"
                if ig and r["id"] in errs:
                    # 10/29 インスタはBufferが「エラー」でも出ていて、出し直しで2つ並んだ（オーナーが1つ消した）→出し直さない
                    append_log(day, f"{slot} {s} Bufferでエラー（インスタは出ていることがあるので出し直さない）")
                elif r.get("texts") and not r.get("retried") and now - due < timedelta(hours=3):
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
