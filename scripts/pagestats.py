"""プロフィール用ページの数（開いた数・押された数）を Cloudflare の KV から読み、data/page-stats.json に書く。

functions/_middleware.js が数えた物。キーは「日付|v|来た元」（開いた）と「日付|c|来た元|項目|名前」（押した）。
来た元は投稿の印：x0715 = Xの7:15の投稿、t0715 = Threadsの7:15、direct = 印なし（プロフィールのリンクなど）。
使い方（page.yml の中）：python3 scripts/pagestats.py <KVのID>  … wrangler で読む。IDがなければ何もしない。
"""
import json
import os
import subprocess
import sys
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import load_json, now_jst, path, save_json  # noqa: E402

KEEP_DAYS = 30
STOP_AT = 600  # 1日にこの数を数えたら、その日は数えるのをやめる（KVの書き込みは無料で1日1,000回。月と同じアカウントなので4割は残す）
WRANGLER = ["npx", "-y", "wrangler@3.80.0"]


def parse(keys):
    """KVのキーの一覧 → {日付: {"views": 合計, "clicks": 合計, "view": {元: n}, "click": {元: {"項目|名前": n}}}}"""
    out = {}
    for k in keys:
        name, n = k.get("name", ""), int((k.get("metadata") or {}).get("n") or 0)
        parts = name.split("|")
        if len(parts) < 3 or not n or parts[1] not in ("v", "c"):
            continue
        d = out.setdefault(parts[0], {"views": 0, "clicks": 0, "view": {}, "click": {}})
        if parts[1] == "v":
            d["view"][parts[2]] = d["view"].get(parts[2], 0) + n
            d["views"] += n
        elif parts[1] == "c" and len(parts) >= 5:
            c = d["click"].setdefault(parts[2], {})
            item = f"{parts[3]}|{parts[4]}"
            c[item] = c.get(item, 0) + n
            d["clicks"] += n
    return out


def list_keys(ns, prefix):
    r = subprocess.run(WRANGLER + ["kv", "key", "list", f"--namespace-id={ns}", f"--prefix={prefix}"],
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0 or "[" not in r.stdout:
        print("KVを読めない：", (r.stderr or r.stdout)[-300:])
        return None
    return json.loads(r.stdout[r.stdout.find("["):])


def main():
    ns = sys.argv[1] if len(sys.argv) > 1 else ""
    if not ns:
        print("KVのIDがないので数えない")
        return 0
    now = now_jst()
    keys = []
    for i in range(3):  # 今日・昨日・おととい（キーの頭が日付なので日ごとに読む）
        got = list_keys(ns, (now.date() - timedelta(days=i)).isoformat() + "|")
        if got is None:
            return 0
        keys += got
    fp = path("data", "page-stats.json")
    days = (load_json(fp, {}) or {}).get("days", {})
    days.update(parse(keys))
    cut = (now.date() - timedelta(days=KEEP_DAYS)).isoformat()
    days = {d: v for d, v in sorted(days.items()) if d >= cut}
    save_json(fp, {"about": "プロフィール用ページを開いた数(view)と、ページの中で押された数(click)。"
                            "元 x0715=Xの7:15の投稿・t0715=Threadsの7:15・direct=印なし。押した項目 buy=PR・go=おでかけの公式ページ",
                   "at": now.strftime("%m/%d %H:%M"), "days": days})
    t = days.get(now.date().isoformat(), {})
    if t.get("views", 0) + t.get("clicks", 0) >= STOP_AT:
        subprocess.run(WRANGLER + ["kv", "key", "put", f"--namespace-id={ns}", f"{now.date().isoformat()}|stop", "1",
                                   "--ttl=172800"], capture_output=True, text=True, timeout=180)
        print(f"今日は {STOP_AT} を超えたので、数えるのを止めた（ページはそのまま）")
    print(f"今日 開いた {t.get('views', 0)}・押した {t.get('clicks', 0)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
