"""今月の GitHub Actions の分数を数えて notes/actions-minutes.md に書く（10/25 オーナー「制限を把握しよう」）。

無料枠は月2,000分で、月（うさぎちゃん不動産）の分と合わせた数。燈の分はここで数え、
月の分は 10/25 の請求画面の値（月に約420分）で見込む。1回ずつ1分単位に切り上げて数える。"""
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
# 10/30 オーナー「月は非公開じゃない」：公開リポジトリの分数は無料で2,000分に入らないので、月の分は0で見込む
LIMIT, TSUKI = 2000, 0


def get(url):
    h = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        h["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    repo = os.environ.get("GITHUB_REPOSITORY", "oreusa/akari-auto")
    now = datetime.now(timezone.utc)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total, n, page, last7, last1 = 0, 0, 1, 0, 0
    by = {}  # 直近7日の機械ごとの分数
    while page <= 30:
        d = get(f"https://api.github.com/repos/{repo}/actions/runs?per_page=100&page={page}"
                f"&created=%3E%3D{start.strftime('%Y-%m-%d')}")
        runs = d.get("workflow_runs") or []
        for r in runs:
            if not r.get("run_started_at") or r.get("status") != "completed":
                continue
            s = datetime.fromisoformat(r["run_started_at"].replace("Z", "+00:00"))
            e = datetime.fromisoformat(r["updated_at"].replace("Z", "+00:00"))
            m = max(1, -(-int((e - s).total_seconds()) // 60))
            total += m
            if now - s <= timedelta(days=1):
                last1 += m
            if now - s <= timedelta(days=7):
                last7 += m
                k = r.get("name", "?").split("（")[0]
                by[k] = by.get(k, 0) + m
            n += 1
        if len(runs) < 100:
            break
        page += 1
    # 直近7日の1日あたり × 残りの日数 ＋ 今までの分 で月末を見込む
    nxt = (start + timedelta(days=32)).replace(day=1)
    left = (nxt - now).total_seconds() / 86400
    per_day = last7 / min(7, max(1, (now - start).days + 1))
    est = round(total + per_day * left)
    warn = "×1,600分を超えそう。HPの公開を1日2回に減らす" if est + TSUKI > 1600 else "○余裕あり"
    # 11/8 燈のリポジトリも公開（public）。公開リポジトリの標準の機械は無料で、月2,000分の枠に入らない。分数は記録だけする
    try:
        public = get(f"https://api.github.com/repos/{repo}").get("visibility") == "public"
    except Exception:
        public = False
    if public:
        warn = "○公開リポジトリなので無料（2,000分の枠に入らない。記録だけ）"
    days7 = min(7, max(1, (now - start).days + 1))
    # 来月は直近24時間の使い方で見込む（直した機械の分が7日の平均に残るため。10/29 check を main だけにした）
    nov = round(last1 * 30) + TSUKI
    rows = "".join(f"| {k} | {v} | {v / days7:.0f} |\n" for k, v in sorted(by.items(), key=lambda x: -x[1]))
    text = (f"# GitHub Actions の分数（{now.astimezone(JST):%Y-%m-%d %H:%M} に数えた）\n\n"
            f"- 今月の燈：{total}分（{n}回）／直近の1日あたり {per_day:.0f}分\n- 月末の見込み：燈 {est}分＋月 約{TSUKI}分＝{est + TSUKI}分／{LIMIT}分\n"
            f"- 判定：{warn}\n"
            f"- 来月（30日）の見込み：燈 {round(last1 * 30)}分（直近24時間 {last1}分×30）＋月 約{TSUKI}分＝{nov}分／{LIMIT}分 {'○（公開なので無料）' if public else ('×' if nov > LIMIT else '○')}\n\n"
            f"## 機械ごと（直近{days7}日）\n| 機械 | 分 | 1日あたり |\n|---|---|---|\n{rows}")
    os.makedirs("notes", exist_ok=True)
    open("notes/actions-minutes.md", "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
