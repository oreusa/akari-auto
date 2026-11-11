"""関東の成長の帳面（notes/seichou.md・data/seichou.json）を作る。11/11 月（オーナー「月と燈も全部」「結果・数字と報告だけ見たい」）。

元は data/page-stats.json（scripts/pagestats.py が KV から写した物）。この7日と前の7日をくらべ、
「HPが見られた数・投稿から来て押した数（来た元 x0715・t0715 など）・相談や査定へ押された数」と、いちばん弱い所を1つ出す。
数は機械や自分たちの分を分けられないので、小さい数は「未確認」と読む。使い方：python3 scripts/seichou.py [YYYY-MM-DD]
"""
import json, os, re, sys
from datetime import date, timedelta

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
today = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
days = json.load(open(os.path.join(ROOT, "data", "page-stats.json"), encoding="utf-8")).get("days", {})
POST = re.compile(r"^[xt]\d{4}$")
ASK = ("申し込み", "査定", "売りたい", "相談")
SKIP_SRC = ("okaimono", "menu", "x")  # 操作と試しの分


def week(a, b):
    """a < 日 <= b の合計"""
    o = {"views": 0, "come": 0, "cost": 0, "open": 0, "sent": 0, "post": 0, "ask": 0, "buy": 0, "slots": {}, "days": 0}
    for d, v in days.items():
        if not (a.isoformat() < d <= b.isoformat()):
            continue
        o["days"] += 1
        o["views"] += int(v.get("views", 0) or 0)
        for src, n in (v.get("view") or {}).items():
            if POST.match(src):
                o["come"] += n
                o["slots"][src] = o["slots"].get(src, 0) + n
        for src, items in (v.get("click") or {}).items():
            n = sum(items.values())
            if POST.match(src):
                o["post"] += n
            if src in SKIP_SRC:
                continue
            for k, c in items.items():
                if any(w in k for w in ASK):
                    o["ask"] += c
                if k.startswith("表示：解体・片付けの費用"):
                    o["cost"] += c
                if k.endswith("表示：お申し込み"):
                    o["open"] += c
                if k.endswith("申し込み｜送信"):
                    o["sent"] += c
                if k.startswith(("buy", "goods", "tanka", "yado", "furusato")):
                    o["buy"] += c
    return o


end = today - timedelta(days=1)
now, prev = week(end - timedelta(days=7), end), week(end - timedelta(days=14), end - timedelta(days=7))
slots = sorted(now["slots"].items(), key=lambda x: -x[1])[:5]
if now["views"] < 1500:
    weak, nxt = "HPに来る人が少ない", "来た元が多い枠の型を明日もう1本。検索から来る入口ページの題と説明を1つ直す"
elif now["come"] < 50:
    weak, nxt = "投稿からHPに来る人が少ない", "投稿の2つ目の行き先を、その話の答えが出るページ（街・費用・地図）に替える"
else:
    weak, nxt = "来た人が相談・査定まで行かない", "いちばん見られた入口の上に、次に押す所を1つだけ置く"
out = {"date": today.isoformat(), "now": {k: now[k] for k in ("views", "come", "post", "ask", "cost", "open", "sent", "buy", "days")},
       "prev": {k: prev[k] for k in ("views", "come", "post", "ask", "cost", "open", "sent", "buy", "days")},
       "slots": [{"name": k, "n": n} for k, n in slots], "weak": weak, "next": nxt}
json.dump(out, open(os.path.join(ROOT, "data", "seichou.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
L = [f"# 関東の成長の帳面（{today.isoformat()} 朝）", "",
     "毎朝、機械が作り直します。燈は夜の回の「2 育てる」でこれを先に読み、次の一手を1つだけやります。", "",
     "| 物差し | この7日 | 前の7日 |", "|---|---|---|",
     f"| HPが見られた数 | {now['views']} | {prev['views']} |",
     f"| 投稿からHPに来た数（11/11 夜から数え始め） | {now['come']} | {prev['come']} |",
     f"| 投稿から来て押した数 | {now['post']} | {prev['post']} |",
     f"| 相談・査定へ押された数 | {now['ask']} | {prev['ask']} |",
     f"| 解体・片付けの費用ページを見た数（11/11 夜に公開） | {now['cost']} | {prev['cost']} |",
     f"| 申し込みページを開いた数（11/11 夜から数え始め） | {now['open']} | {prev['open']} |",
     f"| 送信された相談（反響。11/11 夜から数え始め） | {now['sent']} | {prev['sent']} |",
     f"| 買い物・宿のリンクが押された数 | {now['buy']} | {prev['buy']} |", "",
     "投稿の枠ごと（HPに来た数、多い順。x＝X、t＝Threads、数字は時刻）：" + ("、".join(f"{k} {n}" for k, n in slots) or "0"), "",
     f"いちばん弱い所：{weak}", f"次の一手：{nxt}", ""]
open(os.path.join(ROOT, "notes", "seichou.md"), "w", encoding="utf-8").write("\n".join(L))
print("\n".join(L))
