"""当たり帳。毎朝、数字係のあとに直近7日の数字をまとめ、notes/scoreboard.md に書く。

夜の回は作戦帳の次にこれを読み、当たりの型に寄せ、外れの型をやめる（10/24 オーナー「学習してシステムをアップデートしてくれ」）。
燈の記憶や感想ではなく、機械が数えた数字で決めるための表。
"""
import glob
import os
import re
import statistics
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import load_json, now_jst, path  # noqa: E402

DAYS = 7
SVC = {"threads": "Threads", "twitter": "X", "instagram": "インスタ"}


def views(m):
    v = m.get("views", m.get("impressions"))
    return int(v or 0)


def head_style(first):
    """1行目の形。仮説の○×を機械で付けるための分け方。"""
    t = first.strip()
    if t.startswith("【AIが比べた"):
        return "【AIが比べた〜】"
    if t.startswith("【"):
        return "【〜】（ほか）"
    if re.match(r"^(今日|明日|あす|今週|今夜)?\s*\d{1,2}/\d{1,2}", t) or t.startswith(("今日", "今夜", "今週")):
        return "日付から始める"
    if "昨日わかったこと" in t or "運用日記" in t:
        return "4コマ・日記"
    return "名前などから始める"


def load(today):
    rows = []
    for f in sorted(glob.glob(path("data", "metrics", "*.json"))):
        day = os.path.basename(f)[:-5]
        if not re.match(r"\d{4}-\d{2}-\d{2}$", day) or day < (today - timedelta(days=DAYS)).isoformat():
            continue
        sched = {p.get("slot"): p for p in (load_json(path("schedule", f"{day}.json"), {}) or {}).get("posts", [])}
        for r in (load_json(f, {}) or {}).get("posts", []):
            sp = sched.get(r.get("slot")) or {}
            kind = "PR" if sp.get("link") else (sp.get("topic") or ("4コマ" if r.get("slot") == "4コマ" else "そのほか"))
            first = r.get("first", "")
            rows.append({"day": day, "svc": r.get("service", ""), "slot": r.get("slot", ""), "kind": kind,
                         "first": first, "v": views(r.get("metrics") or {}),
                         "style": head_style(first), "pref": pref_of(" ".join([first] + list(sp.get("threads") or [])[:1])),
                         "wd": "月火水木金土日"[datetime.fromisoformat(day).weekday()]})
    return rows


def pref_of(text):
    """投稿の文から都県（関東おでかけリストと同じ分け方。分からなければ「そのほか」）。"""
    try:
        import page
        return page._pref({"title": text, "bullets": []}) or "そのほか"
    except Exception:
        return "そのほか"


def med(xs):
    return int(statistics.median(xs)) if xs else 0


def table(rows, key, svc):
    groups = {}
    for r in rows:
        if r["svc"] == svc:
            groups.setdefault(r[key], []).append(r["v"])
    out = sorted(groups.items(), key=lambda kv: -med(kv[1]))
    return [f"| {k} | {len(vs)} | {med(vs)} | {max(vs)} |" for k, vs in out]


def main():
    today = now_jst().date()
    rows = [r for r in load(today) if r["svc"] in SVC]
    if not rows:
        print("数字がまだありません")
        return 0
    days = sorted({r["day"] for r in rows})
    L = [f"# 当たり帳（機械が毎朝作る。{days[0]}〜{days[-1]}、{len(rows)}本）", "",
         "夜の回は作戦帳の次にこれを読む。当たり＝その場所の中央値の3倍以上、外れ＝中央値の半分以下。", ""]
    L += ["## 場所ごとの中央値", "| 場所 | 本数 | 中央値 | 当たりの線 |", "|---|---|---|---|"]
    meds = {}
    for s, name in SVC.items():
        vs = [r["v"] for r in rows if r["svc"] == s]
        if vs:
            meds[s] = med(vs)
            L.append(f"| {name} | {len(vs)} | {meds[s]} | {meds[s] * 3} |")
    L += ["", "## 当たり（中央値の3倍以上、多い順に10本）", "| 日 | 場所 | 枠 | 種類 | 閲覧 | 1行目 |", "|---|---|---|---|---|---|"]
    hits = sorted([r for r in rows if meds.get(r["svc"]) is not None and r["v"] >= max(1, meds[r["svc"]]) * 3],
                  key=lambda r: -r["v"])[:10]
    L += [f"| {r['day'][5:]} | {SVC[r['svc']]} | {r['slot']} | {r['kind']} | {r['v']} | {r['first'][:36]} |" for r in hits]
    for s in ("threads", "twitter"):
        L += ["", f"## {SVC[s]}：種類ごと（中央値の高い順）", "| 種類 | 本数 | 中央値 | 最高 |", "|---|---|---|---|"]
        L += table(rows, "kind", s)
        L += ["", f"## {SVC[s]}：1行目の形ごと", "| 形 | 本数 | 中央値 | 最高 |", "|---|---|---|---|"]
        L += table(rows, "style", s)
        L += ["", f"## {SVC[s]}：枠ごと", "| 枠 | 本数 | 中央値 | 最高 |", "|---|---|---|---|"]
        L += sorted(table(rows, "slot", s))
        # 全方向から学ぶ（10/26 オーナー「学習エンジンは全方向からね」）：都県・曜日でも分ける
        L += ["", f"## {SVC[s]}：都県ごと（関東おでかけリストの分け方）", "| 都県 | 本数 | 中央値 | 最高 |", "|---|---|---|---|"]
        L += table(rows, "pref", s)
        L += ["", f"## {SVC[s]}：曜日ごと", "| 曜日 | 本数 | 中央値 | 最高 |", "|---|---|---|---|"]
        L += table(rows, "wd", s)
    st = (load_json(path("data", "page-stats.json"), {}) or {}).get("days", {})
    if st:
        L += ["", "## HP（見られた数・PRが押された数）", "| 日 | 見られた | PRが押された | 押された元 |", "|---|---|---|---|"]
        for d in sorted(st)[-DAYS:]:
            v = st[d]
            src = {}
            for f, items in (v.get("click") or {}).items():
                src[f] = src.get(f, 0) + sum(items.values())
            L.append(f"| {d[5:]} | {v.get('views', 0)} | {v.get('clicks', 0)} | "
                     + "、".join(f"{k} {n}" for k, n in sorted(src.items(), key=lambda kv: -kv[1])) + " |")
    if st:  # HPで押されたカード（直近7日の合計、多い順）。押された種類を次の日の投稿と集め係に使う
        tot = {}
        for d in sorted(st)[-DAYS:]:
            for items in (st[d].get("click") or {}).values():
                for k, n in items.items():
                    tot[k] = tot.get(k, 0) + n
        if tot:
            L += ["", "## HPで押されたカード（7日の合計、多い順に15）", "| 欄｜名前 | 回数 |", "|---|---|"]
            L += [f"| {k[:50]} | {n} |" for k, n in sorted(tot.items(), key=lambda kv: -kv[1])[:15]]
            sec = {}
            for k, n in tot.items():
                sec[k.split("|")[0]] = sec.get(k.split("|")[0], 0) + n
            L += ["", "## HPで押された欄（7日の合計）", "| 欄 | 回数 |", "|---|---|"]
            L += [f"| {k} | {n} |" for k, n in sorted(sec.items(), key=lambda kv: -kv[1])]
    out = path("notes", "scoreboard.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"当たり帳：{len(rows)}本、当たり{len(hits)}本")
    return 0


if __name__ == "__main__":
    sys.exit(main())
