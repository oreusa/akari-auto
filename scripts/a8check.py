"""A8のリンクが広告主のページに着くかを確かめる（投稿はしない）。
使い方：python3 scripts/a8check.py "https://px.a8.net/svt/ejp?a8mat=…|domain" …"""
import sys
import lib

bad = 0
for arg in sys.argv[1:]:
    url, _, dom = arg.partition("|")
    r = lib.a8_link(url.strip(), dom.strip())
    print(("OK " if r["ok"] else "× ") + dom + "  " + (r.get("name") or r.get("why") or ""))
    bad += 0 if r["ok"] else 1
print(f"A8確認：{len(sys.argv) - 1 - bad}件OK／×{bad}件")
