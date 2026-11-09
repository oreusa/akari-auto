"""夜の提案（11/9）：5つの変更を入れて、4つの出力（X・Threads・Web・インスタ画像の字）に変更漏れ・古い値の残り・募集終了の残りが無いかを数える。
python3 samples/fudosan-sns/test_changes.py"""
import copy, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make  # noqa: E402

d = json.load(open(os.path.join(make.D, "properties.json"), encoding="utf-8"))
co = d["company"]
CHANGES = [("A", "rent", 95000), ("A", "fee", 6000), ("B", "deposit", "1か月"), ("C", "walk", 6), ("B", "status", "終了")]
t0, total = time.time(), 0
for pid, k, v in CHANGES:
    it = next(x for x in d["items"] if x["id"] == pid)
    old = copy.deepcopy(it)
    it[k] = v
    it["updated"] = "2026-11-10"
    bad = make.check(it, co, old)
    total += len(bad)
    print(f"{pid} {k}: {old[k]} → {v}｜欠け・残り {len(bad)}", bad[:3])
print(f"5つの変更 合計の欠け・残り：{total}｜かかった秒：{time.time() - t0:.3f}")
sys.exit(1 if total else 0)
