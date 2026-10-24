"""プロフィール用ページが見られた数を Cloudflare の分析（読むだけ・KVに書かない）から取る。

Cloudflare Web Analytics（ページに小さな計測の印を入れる・無料・保存の回数を使わない）。
python3 scripts/cfviews.py test … 鍵で何が読めるか試す
python3 scripts/cfviews.py tag  … 計測の印（site_tag）を出す。なければ作る
python3 scripts/cfviews.py      … 直近3日の見られた数を data/page-stats.json の days[日付].views に入れる
"""
import json
import os
import sys
import urllib.request
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import load_json, now_jst, path, save_json  # noqa: E402

HOST = "usagi-life-notes.pages.dev"
API = "https://api.cloudflare.com/client/v4"


def req(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": "Bearer " + os.environ.get("CLOUDFLARE_API_TOKEN", ""),
        "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=30) as res:
            return json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode())
        except Exception:
            return {"success": False, "errors": [{"message": f"HTTP {e.code}"}]}
    except Exception as e:
        return {"success": False, "errors": [{"message": str(e)[:200]}]}


def account():
    r = req("GET", API + "/accounts")
    got = r.get("result") or []
    return got[0]["id"] if got else ""


def site(acc, create=True):
    r = req("GET", f"{API}/accounts/{acc}/rum/site_info/list")
    for s in r.get("result") or []:
        if s.get("host") == HOST or (s.get("ruleset") or {}).get("zone_name") == HOST:
            return s.get("site_tag", ""), s.get("site_token", ""), r
    if create:
        c = req("POST", f"{API}/accounts/{acc}/rum/site_info", {"host": HOST, "auto_install": False})
        res = c.get("result") or {}
        return res.get("site_tag", ""), res.get("site_token", ""), c
    return "", "", r


def views(acc, tag, start, end):
    q = """query($a:String!,$t:String!,$s:Date!,$e:Date!){viewer{accounts(filter:{accountTag:$a}){
      rumPageloadEventsAdaptiveGroups(limit:100,filter:{siteTag:$t,date_geq:$s,date_leq:$e,bot:0}){count sum{visits} dimensions{date}}}}}"""
    r = req("POST", API + "/graphql", {"query": q, "variables": {"a": acc, "t": tag, "s": start, "e": end}})
    try:
        rows = r["data"]["viewer"]["accounts"][0]["rumPageloadEventsAdaptiveGroups"]
    except Exception:
        print("分析を読めない：", json.dumps(r.get("errors"), ensure_ascii=False)[:300])
        return None
    return {x["dimensions"]["date"]: {"views": x["count"], "visits": (x.get("sum") or {}).get("visits", 0)} for x in rows}


def main():
    if not os.environ.get("CLOUDFLARE_API_TOKEN"):
        print("鍵がない")
        return 0
    acc = account()
    if sys.argv[1:] == ["test"]:
        print("account:", bool(acc))
        tag, tok, r = site(acc, create=True)
        print("site:", bool(tag), bool(tok), json.dumps(r.get("errors"), ensure_ascii=False)[:300])
        if tag:
            d = now_jst().date()
            print("views:", views(acc, tag, (d - timedelta(days=2)).isoformat(), d.isoformat()))
        return 0
    if sys.argv[1:] == ["tag"]:
        tag, tok, _ = site(acc)
        print(tok)
        return 0
    tag, _, _ = site(acc, create=False)
    if not tag:
        print("計測の印がまだない")
        return 0
    d = now_jst().date()
    got = views(acc, tag, (d - timedelta(days=2)).isoformat(), d.isoformat())
    if got is None:
        return 0
    fp = path("data", "page-stats.json")
    o = load_json(fp, {}) or {}
    days = o.setdefault("days", {})
    for day, v in got.items():
        days.setdefault(day, {"views": 0, "clicks": 0, "view": {}, "click": {}}).update(views=v["views"], visits=v["visits"])
    save_json(fp, o)
    print("見られた数：", {k: v["views"] for k, v in sorted(got.items())})
    return 0


if __name__ == "__main__":
    sys.exit(main())
