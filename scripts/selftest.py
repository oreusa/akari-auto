"""予約係の自己テスト（本物のBuffer・楽天にはつながない）。check.yml で毎回動く。"""
import os
import sys
import tempfile
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import book  # noqa: E402
import lib  # noqa: E402
from check import check_file, post_problems  # noqa: E402

fails = []


def ok(cond, msg):
    if not cond:
        fails.append(msg)
        print("×", msg)


# 文字数
ok(lib.x_weight("abc") == 3, "x_weight 半角")
ok(lib.x_weight("あいう") == 6, "x_weight 全角")
ok(lib.x_weight("見て https://example.com/aaaa") == 4 + 1 + 23, "x_weight URL")

FB = {"x": ["【AIが比べた代わり】代わりの文\n公式より（10/23時点）\n#節約"], "threads": ["【AIが比べた代わり】代わりの文\n公式より（10/23時点）"], "topic": "節約"}
PR = {
    "slot": "18:15", "topic": "暮らし",
    "x": ["【AIが比べた着る毛布】比べました\n選んだ理由：5枚を比べ、レビュー件数がいちばん多かったためです\n楽天市場より（10/23時点）\n#暮らし #PR", "商品ページはこちらです\n{{LINK}}\n#PR"],
    "threads": ["【AIが比べた着る毛布】比べました\n選んだ理由：5枚を比べ、レビュー件数がいちばん多かったためです\n楽天市場より（10/23時点）\n#暮らし #PR", "商品ページはこちらです\n{{LINK}}\n#PR"],
    "link": {"type": "ichiba", "url": "https://item.rakuten.co.jp/low-ya/vg-groony/", "expect": "グルーニー"},
    "fallback": FB,
}
ok(post_problems(PR) == [], f"正しいPRが合格しない: {post_problems(PR)}")
bad = dict(PR, x=["#PRなし", "{{LINK}}"])
ok(any("#PR" in p for p in post_problems(bad)), "#PRなしを見逃した")
ok(any("Amazon" in p for p in post_problems(dict(PR, x=["a\n#PR", "https://amazon.co.jp/dp/x #PR {{LINK}}"]))), "Amazonを見逃した")
ok(any("短縮" in p for p in post_problems(dict(PR, threads=["a\n#PR", "https://a.r10.to/abc #PR {{LINK}}"]))), "短縮リンクを見逃した")
ok(any("fallback" in p for p in post_problems({k: v for k, v in PR.items() if k != "fallback"})), "fallbackなしを見逃した")
ok(any("選んだ理由" in p for p in post_problems(dict(PR, x=["【AIが比べた着る毛布】比べました\n#暮らし #PR", "{{LINK}} #PR"]))), "選んだ理由なしのPRを見逃した")
ok(any("【AIが比べた" in p for p in post_problems(dict(PR, x=["【着る毛布】比べました\n選んだ理由：a\n#暮らし #PR", "{{LINK}} #PR"]))), "AIが比べたでない見出しを見逃した")
ok(not any("【AIが比べた" in p for p in post_problems({"slot": "13:45", "topic": "おでかけ", "x": ["今日10/24から、京都駅でPOP UP\n公式より（10/23時点）\n#おでかけ"], "threads": ["今日10/24から、京都駅でPOP UP\n公式より（10/23時点）"]})), "PR以外の見出しを×にした")
ok(any("見出し" in p for p in post_problems(dict(PR, threads=["【別の見出し】\n#PR", "{{LINK}} #PR"]))), "XとThreadsの見出し違いを見逃した")
ok(any("URLは入れない" in p for p in post_problems(dict(PR, threads=["【AIが比べた着る毛布】比べました\n{{LINK}}\n#PR", "{{LINK}} #PR"]))), "1つ目のURLを見逃した")
ok(any("文字数" in p for p in post_problems(dict(PR, x=["あ" * 141 + "\n#PR", "{{LINK}} #PR"]))), "X文字数超えを見逃した")

# アフィリエイトの形のURLから商品ページを取り出せる
u = "https://hb.afl.rakuten.co.jp/hgc/g00pxdho.m2lhf999.g00pxdho.m2lhfa00/?pc=https%3A%2F%2Fitem.rakuten.co.jp%2Flow-ya%2Fvg-groony%2F&m=x"
ok("/low-ya/vg-groony/" in lib._plain_url({"itemUrl": u}), "商品ページURLの取り出し")

# 出どころのページはまね（ネットにつながない）
book.page_check = lambda u: ("ended", "ページに「このイベントは終了しました」") if "ended" in u else ("ok", "")
ok(lib.missing_specs(["140×80cm・3.2L"], "サイズ 140×80 cm", "タンク3.2L") == [], "同じ数字を×にした")
ok(lib.missing_specs(["188×130cm"], "サイズ 140×80cm") == ["130cm"], "大きさの違いを見逃した")
ok(lib.about_item(["◇ A社 X1：80W\n◇ JBK551G：55W\n◇ どちらも約188×130cm"], "JBK551G") == ["◇ JBK551G：55W", "◇ どちらも約188×130cm"], "選んだ商品の行の取り出し")
# 日付の古い出どころ
from check import asof_problems  # noqa: E402
from datetime import date  # noqa: E402
ok(any("古い" in p for p in asof_problems({"x": ["a（9/25時点）"], "threads": ["a（10/23時点）"]}, date(2026, 10, 24))), "古い出どころを見逃した")
ok(asof_problems({"x": ["a（10/23時点）"], "threads": ["a（10/20時点）"]}, date(2026, 10, 24)) == [], "新しい出どころを×にした")
# 終わったイベント → 代わり
ev = {"slot": "12:15", "topic": "おでかけ", "x": ["a（10/23時点）", "https://example.com/ended"], "threads": ["a（10/23時点）", "https://example.com/ended"],
      "until": "2026-10-30T23:59", "fallback": FB}
ok(book.choose(ev, "2026-10-24", None)[3] == "代わり", "終わったイベントで代わりにならない")
ok(book.choose(dict(ev, fallback=None), "2026-10-24", None)[3] == "中止", "終わったイベント（代わりなし）が中止にならない")

# 楽天が「売り切れ」→ 代わりになる
book.rakuten_item = lambda *a, **k: {"ok": False, "why": "売り切れ・販売停止"}
xs, ths, topic, kind, why = book.choose(PR, "2026-10-24", None)
ok(kind == "代わり" and xs == FB["x"], "売り切れで代わりにならない")
# 別の商品 → 代わり
book.rakuten_item = lambda *a, **k: {"ok": True, "name": "別の毛布", "link": "https://hb.afl.rakuten.co.jp/hgc/abc/?pc=x"}
ok(book.choose(PR, "2026-10-24", None)[3] == "代わり", "商品名違いで代わりにならない")
# 合格 → リンクが入る
book.rakuten_item = lambda *a, **k: {"ok": True, "name": "LOWYA グルーニー 着る毛布", "reviewCount": 46917,
                                  "reviewAverage": 4.5, "link": "https://hb.afl.rakuten.co.jp/hgc/abc/?pc=x"}
xs, ths, topic, kind, why = book.choose(PR, "2026-10-24", None)
big = dict(PR, x=["【AIが比べた着る毛布】グルーニーは188×130cm\n選んだ理由：5枚を比べ、レビュー件数がいちばん多かったためです\n楽天市場より（10/23時点）\n#暮らし #PR", "{{LINK}}\n#PR"])
book.rakuten_item = lambda *a, **k: {"ok": True, "name": "LOWYA グルーニー 着る毛布 140×80cm", "caption": "",
                                  "link": "https://hb.afl.rakuten.co.jp/hgc/abc/?pc=x"}
ok(book.choose(big, "2026-10-24", None)[3] == "代わり", "大きさの書き違いで代わりにならない")
book.rakuten_item = lambda *a, **k: {"ok": True, "name": "LOWYA グルーニー 着る毛布", "reviewCount": 46917,
                                  "reviewAverage": 4.5, "link": "https://hb.afl.rakuten.co.jp/hgc/abc/?pc=x"}
ok(kind == "PR" and "hb.afl.rakuten" in xs[1] and "{{LINK}}" not in "".join(xs + ths), "合格なのにリンクが入らない")
# 期限切れ → 代わり
exp = dict(PR, until="2026-10-24T09:59")
ok(book.choose(exp, "2026-10-24", None)[3] == "代わり", "期限切れで代わりにならない")

# 予約の流れ（Bufferはまね）
calls = []
book.buffer_posts = lambda cfg, st, a, b, channel_ids=None: []
book.buffer_create = lambda ch, s, texts, due, topic=None, draft=False: calls.append((s, due, texts)) or {"id": f"p{len(calls)}", "status": "scheduled"}
with tempfile.TemporaryDirectory() as d:
    lib.ROOT = d
    book.path = lambda *a: os.path.join(d, *a)
    book.load_json = lib.load_json
    book.append_log = lambda day, line: print("  log:", line)
    lib.save_json(os.path.join(d, "config.json"), {"channels": {"twitter": "T", "threads": "H"}})
    lib.save_json(os.path.join(d, "schedule", "2026-10-24.json"), {"date": "2026-10-24", "room": [{"url": PR["link"]["url"], "expect": "グルーニー", "comment": "a"}], "posts": [
        PR, {"slot": "23:00", "topic": "旅行", "x": ["a 10/24から\n公式より（10/23時点）\n#旅行", "公式ページ\nhttps://example.com/a"], "threads": ["a 10/24から\n公式より（10/23時点）", "公式ページ\nhttps://example.com/a"]}]})
    ok(check_file(os.path.join(d, "schedule", "2026-10-24.json")) == [], "予定表の見本が不合格")
    bad = {"date": "2026-10-24", "posts": [{"slot": "21:00", "topic": "a", "x": ["a 10/29から\n公式より（10/23時点）"], "threads": ["a 10/29から\n公式より（10/23時点）"]}]}
    lib.save_json(os.path.join(d, "schedule", "bad.json"), bad)
    ok(any("公式ページのURL" in s for s in check_file(os.path.join(d, "schedule", "bad.json"))), "公式ページのURLが無い投稿が通る")
    now = datetime(2026, 10, 24, 16, 30, tzinfo=lib.JST)
    book.run(now)
    ok(len(calls) == 2 and calls[0][1] == "2026-10-24T09:15:00.000Z", f"18:15の予約がおかしい: {calls}")
    book.run(now)
    ok(len(calls) == 2, "同じ投稿を2回予約した")
    # 遅れた回：18:40 に動いた → 18:55 に出す、23:00 はまだ先
    calls.clear()
    lib.save_json(os.path.join(d, "state", "booked.json"), {})
    book.run(datetime(2026, 10, 24, 18, 40, tzinfo=lib.JST))
    ok(len(calls) == 2 and calls[0][1] == "2026-10-24T09:55:00.000Z", f"遅れたときの時刻がおかしい: {calls}")

    # 出たかの確認：Bufferでエラー → 1回だけ出し直す
    calls.clear()
    st = {"2026-10-24 18:15": {"twitter": {"id": "E1", "at": "18:15", "texts": ["a", "b"], "kind": "通常"}}}
    lib.save_json(os.path.join(d, "state", "booked.json"), st)
    book.buffer_posts = lambda cfg, sts, a, b, channel_ids=None: [{"id": "E1", "channelService": "twitter", "status": "error"}] if "error" in sts else []
    book.run(datetime(2026, 10, 24, 18, 50, tzinfo=lib.JST))
    redo = lambda: [c for c in calls if c[2] == ["a\n", "b"]]  # noqa: E731
    ok(len(redo()) == 1 and redo()[0][0] == "twitter", f"出なかった投稿を出し直さない: {calls}")
    book.run(datetime(2026, 10, 24, 19, 50, tzinfo=lib.JST))
    ok(len(redo()) == 1, "出し直しを2回以上した")

    # 長すぎる×：Threadsは同じ文で通らない → その場で代わりの文で予約する
    calls.clear()
    lib.save_json(os.path.join(d, "state", "booked.json"), {})
    book.buffer_posts = lambda cfg, st, a, b, channel_ids=None: []
    def long_err(ch, s, texts, due, topic=None, draft=False, **kw):
        if s == "threads" and "{{LINK}}" not in "".join(texts) and "hb.afl" in "".join(texts):
            raise lib.BufferError("Invalid post: Thread item 2 exceeds the 500 character limit.")
        calls.append((s, due, texts))
        return {"id": f"L{len(calls)}"}
    book.buffer_create = long_err
    book.run(now)
    st = lib.load_json(os.path.join(d, "state", "booked.json"))
    ok(st["2026-10-24 18:15"]["threads"].get("kind") == "代わり" and st["2026-10-24 18:15"]["threads"].get("id"),
       f"長すぎる×で代わりの文にならない: {st.get('2026-10-24 18:15')}")
    # 予定表の文を直したら、×で止まっていた回数を戻す
    st["2026-10-24 18:15"]["threads"] = {"tries": 3, "error": "x", "sig": "old"}
    lib.save_json(os.path.join(d, "state", "booked.json"), st)
    book.buffer_create = lambda ch, s, texts, due, topic=None, draft=False, **kw: calls.append((s, due, texts)) or {"id": f"R{len(calls)}"}
    book.run(now)
    st = lib.load_json(os.path.join(d, "state", "booked.json"))
    ok(st["2026-10-24 18:15"]["threads"].get("id", "").startswith("R"), f"文を直しても予約し直さない: {st.get('2026-10-24 18:15')}")
    book.buffer_create = lambda ch, s, texts, due, topic=None, draft=False: calls.append((s, due, texts)) or {"id": f"p{len(calls)}", "status": "scheduled"}

    # 4コマ：絵のURLがあれば X・Threads は画像、Instagram は動画があるときだけリール
    kc = []
    book.media_problem = lambda u, k: ""
    book.buffer_create = lambda ch, s, texts, due, topic=None, draft=False, **kw: kc.append((s, due, texts, topic, kw)) or {"id": f"k{len(kc)}"}
    book.buffer_posts = lambda cfg, st, a, b, channel_ids=None: []
    lib.save_json(os.path.join(d, "config.json"), {"channels": {"twitter": "T", "threads": "H", "instagram": "I"}})
    lib.save_json(os.path.join(d, "state", "booked.json"), {})
    lib.save_json(os.path.join(d, "koma4", "2026-10-25.json"), {"slot": "08:00", "episode": 18, "text": "t"})
    book.run(datetime(2026, 10, 25, 7, 40, tzinfo=lib.JST))
    ok(not kc, f"絵がないのに4コマを予約した: {kc}")
    lib.save_json(os.path.join(d, "koma4", "2026-10-25.json"), {"slot": "08:00", "episode": 18, "text": "t", "image_url": "https://i/x"})
    from PIL import Image
    book.fetch_image = lambda u: Image.new("RGB", (1080, 1920) if "h=1920" in u else (724, 2172), "white")
    book.run(datetime(2026, 10, 25, 7, 40, tzinfo=lib.JST))
    xt = [c for c in kc if c[0] != "instagram"]
    ok(sorted(c[0] for c in xt) == ["threads", "twitter"] and all(c[4]["image"] == "https://i/x" for c in xt)
       and xt[0][1] == "2026-10-24T23:00:00.000Z" and [c[3] for c in xt if c[0] == "threads"] == ["漫画"],
       f"4コマの予約がおかしい: {kc}")
    ig = [c for c in kc if c[0] == "instagram"]
    ok([c[4].get("ig_type") for c in ig] == ["post", "story", "story"] and len(ig[0][4]["images"]) == 4
       and all(len(c[4]["images"]) == 1 for c in ig[1:]) and [c[1] for c in ig] == ["2026-10-24T23:00:00.000Z"] * 2 + ["2026-10-24T23:01:00.000Z"]
       and all(u.startswith("https://wsrv.nl/?url=https%3A%2F%2Fi%2Fx&cx=") for c in ig for u in c[4]["images"])
       and "h=1920" in ig[1][4]["images"][0] and "precrop=1" in ig[1][4]["images"][0], f"Instagramのスライド・ストーリーがおかしい: {ig}")
    lib.save_json(os.path.join(d, "koma4", "2026-10-25.json"), {"slot": "08:00", "episode": 18, "text": "t", "image_url": "https://i/x", "video_url": "https://v/y"})
    book.run(datetime(2026, 10, 25, 7, 45, tzinfo=lib.JST))
    ok(not [c for c in kc if c[4].get("video")], "確かめていない動画でリールを予約した")
    lib.save_json(os.path.join(d, "koma4", "2026-10-25.json"), {"slot": "08:00", "episode": 18, "text": "t", "image_url": "https://i/x", "video_url": "https://v/y", "video_ok": "07:30"})
    book.run(datetime(2026, 10, 25, 7, 50, tzinfo=lib.JST))
    reel = [c for c in kc if c[0] == "instagram" and c[4].get("video")]
    ok(len(kc) == 6 and len(reel) == 1 and reel[0][4]["video"] == "https://v/y", f"Instagramのリールがおかしい／二重予約: {kc}")
    # ストーリー：wsrv.nl が見本と違う絵を返したら出さない（10/24 ずれたまま出た）
    lib.save_json(os.path.join(d, "state", "booked.json"), {})
    n0 = len(kc)
    book.fetch_image = lambda u: Image.new("RGB", (1080, 1920), "black") if "h=1920" in u else Image.new("RGB", (724, 2172), "white")
    book.run(datetime(2026, 10, 25, 7, 40, tzinfo=lib.JST))
    ok(not any(c[4].get("ig_type") == "story" for c in kc[n0:]) and any(c[4].get("ig_type") == "post" for c in kc[n0:]),
       f"見本と違うストーリーを出した: {kc[n0:]}")
    # おでかけ4コマ（10/24〜）：X・Threads は2つ目に公式ページとHPの1行、インスタは1つだけ
    lib.save_json(os.path.join(d, "state", "booked.json"), {})
    lib.save_json(os.path.join(d, "config.json"), {"channels": {"twitter": "T", "threads": "H", "instagram": "I"},
                                                   "page": {"url": "https://usagi-life-notes.pages.dev/", "promote": True}})
    lib.save_json(os.path.join(d, "koma4", "2026-10-25.json"), {"slot": "08:00", "episode": 19, "text": "今日10/25から、上野でマーケット",
                                                                "text2": "https://example.jp/event", "image_url": "https://i/x"})
    book.fetch_image = lambda u: Image.new("RGB", (1080, 1920) if "h=1920" in u else (724, 2172), "white")
    n0 = len(kc)
    book.run(datetime(2026, 10, 25, 7, 40, tzinfo=lib.JST))
    xt = {c[0]: c[2] for c in kc[n0:] if c[0] != "instagram"}
    ok(set(xt) == {"twitter", "threads"} and all(len(t) == 2 and t[1].startswith("https://example.jp/event")
                                                 and "usagi-life-notes.pages.dev/?f=" in t[1] for t in xt.values())
       and all(len(c[2]) == 1 for c in kc[n0:] if c[0] == "instagram"), f"おでかけ4コマの2つ目がおかしい: {kc[n0:]}")
    # 旅先4コマ（10/29〜 水・土の15:15）：2本目の漫画。予約できたら同じ時刻の文の投稿を消し、まだなら文の投稿を予約しない
    lib.save_json(os.path.join(d, "state", "booked.json"), {"2026-10-25 15:15": {"twitter": {"id": "TXT1", "at": "15:15"}}})
    lib.save_json(os.path.join(d, "koma4", "2026-10-25-tabi.json"), {"slot": "15:15", "episode": 1, "replace": "15:15",
                                                                     "text": "今日10/25、草津温泉の湯畑へ", "text2": "https://example.jp/kusatsu", "image_url": "https://i/t"})
    lib.save_json(os.path.join(d, "schedule", "2026-10-25.json"), {"date": "2026-10-25", "posts": [
        {"slot": "15:15", "topic": "おでかけ", "x": ["文の投稿\n公式より（10/24時点）\n#おでかけ", "https://example.jp/a"],
         "threads": ["文の投稿\n公式より（10/24時点）", "https://example.jp/a"]}]})
    deleted, real_delete = [], book.delete_post
    book.delete_post = lambda pid: deleted.append(pid)
    n0 = len(kc)
    book.run(datetime(2026, 10, 25, 13, 30, tzinfo=lib.JST))
    tabi = [c for c in kc[n0:] if c[4].get("alt", "").startswith("旅4コマ")]
    txt = [c for c in kc[n0:] if c[2] and c[2][0].startswith("文の投稿")]
    st = lib.load_json(os.path.join(d, "state", "booked.json"))
    ok({c[0] for c in tabi} >= {"twitter", "threads"} and all(c[1] == "2026-10-25T06:15:00.000Z" for c in tabi if c[0] != "instagram"),
       f"旅先4コマを15:15に予約しない: {kc[n0:]}")
    tid = {c[0]: f"k{kc.index(c) + 1}" for c in txt}
    ok(sorted(deleted) == sorted(["TXT1"] + list(tid.values())) and all(st["2026-10-25 15:15"][s].get("replaced") for s in ("twitter", "threads")),
       f"旅先4コマの時刻の文の投稿を消さない: deleted={deleted} txt={txt}")
    n1 = len(kc)
    book.run(datetime(2026, 10, 25, 14, 30, tzinfo=lib.JST))
    ok(not [c for c in kc[n1:] if c[2] and c[2][0].startswith("文の投稿")], f"旅先4コマに替えた文の投稿をまた予約した: {kc[n1:]}")
    book.delete_post = real_delete
    os.remove(os.path.join(d, "koma4", "2026-10-25-tabi.json"))
    # 4コマの位置：第16話と同じ並びの絵から、4つのコマを見つける
    im = Image.new("RGB", (724, 2172), "white")
    for y in (81, 603, 1125, 1647):
        im.paste((40, 30, 60), (8, y, 717, y + 512))
    bx, how = lib.koma4_boxes(im)
    ok(how == "見つけた" and bx == [(8, y, 709, 512) for y in (81, 603, 1125, 1647)], f"4コマの位置がおかしい: {bx} {how}")

# Amazon：凪が確かめた物だけ、うちのタグで
lib.http = lambda *a, **k: (200, "ショッピングを続ける", "")
now = datetime(2026, 10, 24, 13, 0, tzinfo=lib.JST)
items = {"B0TESTTEST": {"name": "アイリスオーヤマ 電気毛布 140×80cm", "reviews": 5200, "stars": 4.2, "checkedAt": "2026-10-23T20:30:00+09:00", "specs": "140×80cm"}}
r = lib.amazon_link("B0TESTTEST", "電気毛布", now, items)
ok(r.get("ok") and r["link"] == "https://www.amazon.co.jp/dp/B0TESTTEST?tag=aiusagichan-22", f"Amazonの合格がおかしい: {r}")
ok(not lib.amazon_link("B0NOTCHECK", "", now, items).get("ok"), "確認帳にないAmazonを通した")
ok(not lib.amazon_link("B0TESTTEST", "", datetime(2026, 10, 25, 13, 0, tzinfo=lib.JST), items).get("ok"), "古い確認のAmazonを通した")
ok(not lib.amazon_link("B0TESTTEST", "加湿器", now, items).get("ok"), "商品名の違うAmazonを通した")
low = {"B0TESTTEST": dict(items["B0TESTTEST"], reviews=300)}
ok(not lib.amazon_link("B0TESTTEST", "", now, low).get("ok"), "レビューの少ないAmazonを通した")
lib.http = lambda *a, **k: (200, "有効なページではありません", "")
ok(not lib.amazon_link("B0TESTTEST", "", now, items).get("ok"), "ページ切れのAmazonを通した")

# 季節の切り替え（seasons.json）：日付で時期と項目が変わる
import page  # noqa: E402
lib.ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 上の試しで仮の場所にしたので戻す
for md, want in [((1, 3), "お正月"), ((1, 20), "冬の暮らし"), ((10, 24), "冬じたく"), ((11, 20), "ブラックフライデー"),
                 ((12, 10), "クリスマスと年末"), ((12, 30), "お正月"), ((7, 15), "暑さ対策")]:
    got = page.period(datetime(2026, md[0], md[1], 9, 0, tzinfo=lib.JST)).get("name")
    ok(got == want, f"{md[0]}/{md[1]} の時期が「{got}」（{want} のはず）")
ok(page._cat("NERUS ふわとろ毛布", page.cats(datetime(2026, 10, 24, tzinfo=lib.JST))) == "winter", "毛布が冬じたくに入らない")
ok(page._cat("NERUS ふわとろ毛布", page.cats(datetime(2026, 7, 1, tzinfo=lib.JST))) == "life", "夏に毛布が季節の項目に入った")

# ページの宣伝：2つ目の最後にページのURLを1行足す（超えるなら足さない）
pcfg = {"page": {"url": "https://usagi-life-notes.pages.dev/"}}
two = ["【AIが比べた】見出し\n本文", "公式で確かめてください\nhttps://example.com/a"]
wx = book.with_page(two, "twitter", pcfg)
ok(wx[1].startswith("公式で") and wx[1].endswith("pages.dev/"), "Xでページの行が最後に入らない（10/24 オーナー「せめて最後に」）")
old = ["見出し", "AIが比べたおでかけ・宿・お得の一覧：https://usagi-life-notes.pages.dev/?f=x1345\n\n公式です\nhttps://example.com/a"]
ok(book.page_at_head(old) and book.with_page(book.strip_page_head(old), "twitter", pcfg, "13:45")[1].startswith("公式です"), "頭に入れた予約を最後へ直せない")
wt = book.with_page(two, "threads", pcfg)
ok(wt[1].startswith("公式で") and wt[1].endswith("pages.dev/"), "Threadsでページの行が最後に入らない")
ok(book.with_page(["見出し", "あ" * 130], "twitter", pcfg)[1] == "あ" * 130, "Xの280を超えるのにページの行を足した")
ok("pages.dev/?f=x1345" in book.with_page(two, "twitter", pcfg, "13:45")[1], "Xの投稿の印（?f=x1345）が付かない")
ok("pages.dev/?f=t0715" in book.with_page(two, "threads", pcfg, "07:15")[1], "Threadsの投稿の印（?f=t0715）が付かない")
ok(book.with_page(["1つだけ"], "twitter", pcfg) == ["1つだけ"], "1つだけの投稿に足した")
ok(book.with_page(two, "twitter", {"page": {"url": "https://usagi-life-notes.pages.dev/", "promote": False}}) == two, "promote false でも足した")

# 予約し直し：ページのURLがない予約を、足した文で作り直し、古い方を消す（出る25分前を切った物は触らない）
rc, rd = [], []
book.buffer_posts = lambda cfg, st, a, b, channel_ids=None: [{"id": "OLD1"}, {"id": "OLD2"}] if st == ["scheduled"] else []
book.buffer_create = lambda ch, s, texts, due, topic=None, **kw: rc.append((s, due, texts)) or {"id": f"N{len(rc)}"}
book.buffer_gql = lambda q, v=None: rd.append(v["i"]["id"]) or {"deletePost": {"__typename": "DeletePostSuccess"}}
book.append_log = lambda day, line: None
now0 = datetime(2026, 10, 24, 7, 0, tzinfo=lib.JST)
st0 = {"2026-10-24 09:15": {"twitter": {"id": "OLD1", "at": "09:15", "texts": ["見出し", "公式です\nhttps://example.com/a"], "topic": "おでかけ"}},
       "2026-10-24 07:15": {"twitter": {"id": "OLD2", "at": "07:15", "texts": ["見出し", "公式です\nhttps://example.com/b"]}}}
pc = {"channels": {"twitter": "c1", "threads": "c2"}, "page": {"url": "https://usagi-life-notes.pages.dev/"}}
ok(book.refresh_page(pc, st0, now0) and rc and rd == ["OLD1"], f"予約し直しが違う（作った {len(rc)}・消した {rd}）")
ok(st0["2026-10-24 09:15"]["twitter"]["id"] == "N1" and "?f=x0915" in st0["2026-10-24 09:15"]["twitter"]["texts"][1], "新しい予約が記録に入らない")
ok(st0["2026-10-24 07:15"]["twitter"]["id"] == "OLD2", "出る25分前を切った予約を作り直した")
ok(not book.refresh_page(pc, st0, now0), "2回目も作り直した")

# ページの数（KVのキー → 日ごとの数）
import pagestats  # noqa: E402
ps = pagestats.parse([{"name": "2026-10-24|v|x0715", "metadata": {"n": 3}}, {"name": "2026-10-24|v|direct", "metadata": {"n": 2}},
                      {"name": "2026-10-24|c|x0715|buy-winter|着る毛布", "metadata": {"n": 1}}, {"name": "2026-10-24|stop"}])
ok(ps.get("2026-10-24", {}).get("views") == 5 and ps["2026-10-24"]["clicks"] == 1, f"ページの数の読み方が違う: {ps}")
ok(ps["2026-10-24"]["click"]["x0715"] == {"buy-winter|着る毛布": 1}, "押された物が投稿ごとに分かれない")

# 選んだ理由（10/25 オーナー「クチコミ数と評価だけで内容ペラペラ」）
from check import goods_problems, thin_reason  # noqa: E402
ok(thin_reason("選んだ理由：3足を比べ、レビュー件数（5,800件）と評価（4.59）がどちらもいちばん上だったためです"), "件数と評価だけの理由が通る")
ok(thin_reason("選んだ理由：4軒を比べ、評価4.5以上で口コミ1,000件を超えたのは望雲だけだったためです"), "足切りだけの理由が通る")
ok(not thin_reason("選んだ理由：12枚を比べ、1時間の電気代が0.74円でいちばん安かったためです"), "決め手の数字がある理由が×になる")
ok(not thin_reason("選んだ理由：3つを比べ、重さ180gで充電は約4回分、いちばん軽かったためです"), "重さで選んだ理由が×になる")
ok(goods_problems("選んだ理由：3つを比べ、1mあたり0.6円でいちばん安かったためです\nただし、やわらかさは2番目の方が上でした\n置き場所が少ない家に向いています", "g") == [], "3行のHP商品が×になる")
ok(len(goods_problems("選んだ理由：3枚を比べ、レビュー3,834件・評価4.73でいちばん上でした\n寒い夜に。", "g")) >= 2, "ペラペラのHP商品が通る")

# インスタのリールを直接（曲つき）：動画を送る→時刻で公開。Buffer のリールは出さない
import igreel  # noqa: E402
with tempfile.TemporaryDirectory() as d:
    for m in (lib, book, igreel):
        m.path = lambda *a: os.path.join(d, *a)
    igreel.load_json = book.load_json = lib.load_json
    igreel.save_json = lib.save_json
    igreel.append_log = book.append_log = lambda day, line: print("  log:", line)
    lib.save_json(os.path.join(d, "config.json"), {"channels": {"instagram": "I"}, "ig_direct": True, "ig_audio_id": "123"})
    os.makedirs(os.path.join(d, "ig"))
    open(os.path.join(d, "ig", "page_token.enc"), "w").write("x")
    lib.save_json(os.path.join(d, "ig", "setup.json"), {"ig_user_id": "999"})
    lib.save_json(os.path.join(d, "koma4", "2026-10-30.json"), {"slot": "08:00", "episode": 9, "text": "4コマ\nプロフィールのリンク",
                  "image_url": "https://x/i", "video_url": "https://x/v", "video_ok": "07:10"})
    calls_ig = []
    def fake_call(method, url, token, params=None, data=None, headers=None, timeout=120):
        calls_ig.append((method, url, params))
        if url == "999/media":
            return {"id": "C1", "uri": "https://rupload.facebook.com/x"}
        if url.startswith("https://rupload"):
            return {"success": True}
        if url == "C1":
            return {"status_code": "FINISHED"}
        if url == "999/media_publish":
            return {"id": "M1"}
        if url == "M1":
            return {"permalink": "https://instagram.com/reel/abc"}
        return {}
    igreel.call = fake_call
    igreel.download = lambda url: b"video"
    igreel.silence = lambda v: (v + b"-muted", None)
    igreel.host_silent = lambda u, n: ("https://akari-reels.pages.dev/" + n + ".mp4", None)
    os.environ["IG_PAGE_TOKEN"] = "T"
    t = [datetime(2026, 10, 30, 7, 10, tzinfo=lib.JST)]
    igreel.now_jst = lambda: t[0]
    igreel.run(t[0])
    st = lib.load_json(os.path.join(d, "state", "booked.json"))
    dd = st["2026-10-30 4コマ"]["ig_direct"]
    ok(dd.get("state") == "uploaded" and dd.get("container") == "C1", f"リールの動画を送らない: {dd}")
    ok(any(c[1] == "999/media" and "audio_id" in (c[2] or {}).get("audio_configuration", "") for c in calls_ig), "曲が付かない")
    t[0] = datetime(2026, 10, 30, 8, 7, tzinfo=lib.JST)
    igreel.run(t[0])
    dd = lib.load_json(os.path.join(d, "state", "booked.json"))["2026-10-30 4コマ"]["ig_direct"]
    ok(dd.get("state") == "published" and dd.get("permalink"), f"リールを公開しない: {dd}")
    cfg = lib.load_json(os.path.join(d, "config.json"))
    ok(igreel.direct_ready(cfg), "直接の準備ができているのに ready にならない")
    del os.environ["IG_PAGE_TOKEN"]

print("自己テスト：", "OK" if not fails else f"×{len(fails)}")
sys.exit(1 if fails else 0)
