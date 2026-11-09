"""申し込み・業者さまの控え（KV mos|…）が今日いくつ届いたかだけを数える（11/9 オーナー「ない」＝メールが届いていない時の確かめ）。
公開リポジトリのログに出るので、名前・メール・電話・本文は出さない。出すのは時刻・サイト・ページ・種類だけ。"""
import json
import sys
sys.path.insert(0, "scripts")
import pagestats as P

ns = P.find_ns(create=False)
if not ns:
    print("KVが見つからない"); sys.exit(0)
day = sys.argv[1] if len(sys.argv) > 1 else P.now_jst().date().isoformat()
keys = P.list_keys(ns, f"mos|{day}") or []
print(f"{day} の控え：{len(keys)}件")
for k in keys:
    name = k.get("name", "")
    r = P._wr(["kv", "key", "get", name, f"--namespace-id={ns}"])
    try:
        d = json.loads(r.stdout[r.stdout.find("{"):])
    except ValueError:
        d = {}
    print("-", d.get("at", name.split("|")[1] if "|" in name else ""), d.get("site", ""), d.get("page", ""), d.get("kind", ""), "メールあり" if d.get("email") else "メールなし")
