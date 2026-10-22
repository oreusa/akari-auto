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

FB = {"x": ["代わりの文\n#節約"], "threads": ["代わりの文"], "topic": "節約"}
PR = {
    "slot": "18:15", "topic": "暮らし",
    "x": ["【着る毛布】比べました\n#暮らし #PR", "商品ページはこちらです\n{{LINK}}\n#PR"],
    "threads": ["【着る毛布】比べました\n#暮らし #PR", "商品ページはこちらです\n{{LINK}}\n#PR"],
    "link": {"type": "ichiba", "url": "https://item.rakuten.co.jp/low-ya/vg-groony/", "expect": "グルーニー"},
    "fallback": FB,
}
ok(post_problems(PR) == [], f"正しいPRが合格しない: {post_problems(PR)}")
bad = dict(PR, x=["#PRなし", "{{LINK}}"])
ok(any("#PR" in p for p in post_problems(bad)), "#PRなしを見逃した")
ok(any("Amazon" in p for p in post_problems(dict(PR, x=["a\n#PR", "https://amazon.co.jp/dp/x #PR {{LINK}}"]))), "Amazonを見逃した")
ok(any("短縮" in p for p in post_problems(dict(PR, threads=["a\n#PR", "https://a.r10.to/abc #PR {{LINK}}"]))), "短縮リンクを見逃した")
ok(any("fallback" in p for p in post_problems({k: v for k, v in PR.items() if k != "fallback"})), "fallbackなしを見逃した")
ok(any("文字数" in p for p in post_problems(dict(PR, x=["あ" * 141 + "\n#PR", "{{LINK}} #PR"]))), "X文字数超えを見逃した")

# 楽天が「売り切れ」→ 代わりになる
book.rakuten_item = lambda code: {"ok": False, "why": "売り切れ・販売停止"}
xs, ths, topic, kind, why = book.choose(PR, "2026-10-24", None)
ok(kind == "代わり" and xs == FB["x"], "売り切れで代わりにならない")
# 別の商品 → 代わり
book.rakuten_item = lambda code: {"ok": True, "name": "別の毛布", "link": "https://hb.afl.rakuten.co.jp/hgc/abc/?pc=x"}
ok(book.choose(PR, "2026-10-24", None)[3] == "代わり", "商品名違いで代わりにならない")
# 合格 → リンクが入る
book.rakuten_item = lambda code: {"ok": True, "name": "LOWYA グルーニー 着る毛布", "reviewCount": 46917,
                                  "reviewAverage": 4.5, "link": "https://hb.afl.rakuten.co.jp/hgc/abc/?pc=x"}
xs, ths, topic, kind, why = book.choose(PR, "2026-10-24", None)
ok(kind == "PR" and "hb.afl.rakuten" in xs[1] and "{{LINK}}" not in "".join(xs + ths), "合格なのにリンクが入らない")
# 期限切れ → 代わり
exp = dict(PR, until="2026-10-24T09:59")
ok(book.choose(exp, "2026-10-24", None)[3] == "代わり", "期限切れで代わりにならない")

# 予約の流れ（Bufferはまね）
calls = []
book.buffer_create = lambda ch, s, texts, due, topic=None, draft=False: calls.append((s, due, texts)) or {"id": f"p{len(calls)}", "status": "scheduled"}
with tempfile.TemporaryDirectory() as d:
    lib.ROOT = d
    book.path = lambda *a: os.path.join(d, *a)
    book.load_json = lib.load_json
    book.append_log = lambda day, line: print("  log:", line)
    lib.save_json(os.path.join(d, "config.json"), {"channels": {"twitter": "T", "threads": "H"}})
    lib.save_json(os.path.join(d, "schedule", "2026-10-24.json"), {"date": "2026-10-24", "posts": [
        PR, {"slot": "23:00", "topic": "旅行", "x": ["a\n#旅行"], "threads": ["a"]}]})
    ok(check_file(os.path.join(d, "schedule", "2026-10-24.json")) == [], "予定表の見本が不合格")
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

print("自己テスト：", "OK" if not fails else f"×{len(fails)}")
sys.exit(1 if fails else 0)
