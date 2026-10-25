"""今月の GitHub Actions の分数を数えて notes/actions-minutes.md に書く（10/25 オーナー「制限を把握しよう」）。

無料枠は月2,000分で、月（うさぎちゃん不動産）の分と合わせた数。燈の分はここで数え、
月の分は 10/25 の請求画面の値（月に約420分）で見込む。1回ずつ1分単位に切り上げて数える。"""
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
LIMIT, TSUKI = 2000, 450


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
    total, n, page, last7 = 0, 0, 1, 0
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
            if now - s <= timedelta(days=7):
                last7 += m
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
    text = (f"# GitHub Actions の分数（{now.astimezone(JST):%Y-%m-%d %H:%M} に数えた）\n\n"
            f"- 今月の燈：{total}分（{n}回）／直近の1日あたり {per_day:.0f}分\n- 月末の見込み：燈 {est}分＋月 約{TSUKI}分＝{est + TSUKI}分／{LIMIT}分\n"
            f"- 判定：{warn}\n")
    os.makedirs("notes", exist_ok=True)
    open("notes/actions-minutes.md", "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
