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
    ok(any("公式ページのURL" in s for s in post_problems({"slot": "21:00", "topic": "a", "x": ["a 10/29から\n公式より（10/22時点）"], "threads": ["a 10/29から\n公式より（10/22時点）"]})), "公式ページのURLが無い投稿が通る")
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
    book.buffer_posts = lambda cfg, sts, a, b, channel_ids=None: [{"id": "E1", "channelService": "twitter"}] if "error" in sts else []
    book.run(datetime(2026, 10, 24, 18, 50, tzinfo=lib.JST))
    redo = lambda: [c for c in calls if c[2] == ["a\n", "b"]]  # noqa: E731
    ok(len(redo()) == 1 and redo()[0][0] == "twitter", f"出なかった投稿を出し直さない: {calls}")
    book.run(datetime(2026, 10, 24, 19, 50, tzinfo=lib.JST))
    ok(len(redo()) == 1, "出し直しを2回以上した")

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
    book.run(datetime(2026, 10, 25, 7, 40, tzinfo=lib.JST))
    ok(sorted(c[0] for c in kc) == ["threads", "twitter"] and all(c[4]["image"] == "https://i/x" for c in kc)
       and kc[0][1] == "2026-10-24T23:00:00.000Z" and [c[3] for c in kc if c[0] == "threads"] == ["漫画"],
       f"4コマの予約がおかしい: {kc}")
    lib.save_json(os.path.join(d, "koma4", "2026-10-25.json"), {"slot": "08:00", "episode": 18, "text": "t", "image_url": "https://i/x", "video_url": "https://v/y"})
    book.run(datetime(2026, 10, 25, 7, 50, tzinfo=lib.JST))
    ig = [c for c in kc if c[0] == "instagram"]
    ok(len(kc) == 3 and len(ig) == 1 and ig[0][4]["video"] == "https://v/y", f"Instagramのリールがおかしい／二重予約: {kc}")

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

print("自己テスト：", "OK" if not fails else f"×{len(fails)}")
sys.exit(1 if fails else 0)
