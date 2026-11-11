"""プロフィール用ページで押されたアフィリエイトのリンクの数を Cloudflare の KV から読み、data/page-stats.json に書く。

functions/_middleware.js が数えた物。キーは「日付|c|来た元|項目|名前」（押した）。
来た元は投稿の印：x0715 = Xの7:15の投稿、t0715 = Threadsの7:15、direct = 印なし（プロフィールのリンクなど）。
使い方（page.yml の中）：python3 scripts/pagestats.py ns → KVのID（なければ作る）／ python3 scripts/pagestats.py <KVのID>  … wrangler で読む。IDがなければ何もしない。
"""
import json
import os
import subprocess
import sys
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import load_json, now_jst, path, save_json  # noqa: E402

KEEP_DAYS = 30
UI_SRC = ("okaimono", "menu")  # 11/10 お金にならない操作（おかいものの探す・メニュー）。_middleware.js の UI と同じ
UI_STOP_AT = 100  # 操作は1日100で止める（買うボタンの300の枠を食べないように）
STOP_AT = 300  # 操作を除いた 押された数が1日にこの数を超えたら、その日は数えるのをやめる（KVの書き込みは無料で1日1,000回。開いた数は _middleware.js が1日500で止める）
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
    for d in out.values():  # 11/11 合計 all がある日は、投稿の印ごとの数（x0715 など）を合計に足さない（all に入っている）
        if "all" in d["view"]:
            d["views"] = d["view"]["all"]
    return out


NS_TITLE = "usagi-life-notes-clicks"  # wrangler は頭に「worker-」を付けて作る


def _json_list(text):
    """wrangler の出力（前に「[WARNING]」などの文が付く）から JSON の配列を取り出す。"""
    dec = json.JSONDecoder()
    i = text.find("[")
    while i >= 0:
        try:
            v, _ = dec.raw_decode(text[i:])
            if isinstance(v, list):
                return v
        except ValueError:
            pass
        i = text.find("[", i + 1)
    return None


def _wr(args):
    return subprocess.run(WRANGLER + args, capture_output=True, text=True, timeout=180)


def find_ns(create=True):
    """数える場所（KV）のIDを返す。なければ作る。作れないときは ""。"""
    for i in range(2):
        got = _json_list(_wr(["kv", "namespace", "list"]).stdout) or []
        for n in got:
            if isinstance(n, dict) and str(n.get("title", "")).endswith(NS_TITLE):
                return n.get("id", "")
        if i == 0 and create:
            _wr(["kv", "namespace", "create", NS_TITLE])
    return ""


def list_keys(ns, prefix):
    r = _wr(["kv", "key", "list", f"--namespace-id={ns}", f"--prefix={prefix}"])
    got = _json_list(r.stdout) if r.returncode == 0 else None
    if got is None:
        print("KVを読めない：", (r.stderr or r.stdout)[-300:])
    return got


OWNER_CUT = "2026-10-26"  # この日の reset より前の数には、オーナーの端末の分が入っている（10/26 オーナー「オーナーと燈がカウント入ってたらやり直して」）
KEEP_FLAGS = ("since", "owner_in")


def reset_today(ns):
    """今日の数を消して0から数え直す（オーナーの端末に印を付け終えた後の、人だけの数にする）。"""
    now = now_jst()
    day = now.date().isoformat()
    keys = list_keys(ns, day + "|") or []
    for k in keys:
        if k.get("name", "").endswith("|stop"):
            continue
        _wr(["kv", "key", "delete", f"--namespace-id={ns}", k["name"]])
    fp = path("data", "page-stats.json")
    data = load_json(fp, {}) or {}
    days = data.get("days", {})
    for d, v in days.items():
        if d < day:
            v["owner_in"] = True
    days[day] = {"views": 0, "clicks": 0, "view": {}, "click": {}, "since": now.strftime("%H:%M")}
    data["days"] = days
    save_json(fp, data)
    print(f"{day} の数を消した（{len(keys)}件）。{now.strftime('%H:%M')} から数え直す")


def main():
    if sys.argv[1:] == ["ns"]:  # page.yml が公開の前に使う：IDだけを出す
        print(find_ns())
        return 0
    if len(sys.argv) == 3 and sys.argv[1] == "reset":
        reset_today(sys.argv[2])
        sys.argv = sys.argv[:1] + sys.argv[2:]
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
    for d, v in parse(keys).items():
        old = days.get(d, {})
        for f in KEEP_FLAGS:
            if f in old:
                v[f] = old[f]
        days[d] = v
    cut = (now.date() - timedelta(days=KEEP_DAYS)).isoformat()
    days = {d: v for d, v in sorted(days.items()) if d >= cut}
    save_json(fp, {"about": "プロフィール用ページで押されたアフィリエイトのリンク(click)。"
                            "元 x0715=Xの7:15の投稿・t0715=Threadsの7:15・direct=印なし。項目 buy-winter=冬じたくの欄のPR など",
                   "at": now.strftime("%m/%d %H:%M"), "days": days})
    t = days.get(now.date().isoformat(), {})
    ui = sum(sum(t.get("click", {}).get(s, {}).values()) for s in UI_SRC)
    money = t.get("clicks", 0) - ui
    if money >= STOP_AT:
        _wr(["kv", "key", "put", f"--namespace-id={ns}", f"{now.date().isoformat()}|stop", "1", "--ttl=172800"])
        print(f"今日は {STOP_AT} を超えたので、数えるのを止めた（ページはそのまま）")
    if ui >= UI_STOP_AT:
        _wr(["kv", "key", "put", f"--namespace-id={ns}", f"{now.date().isoformat()}|stopui", "1", "--ttl=172800"])
        print(f"今日の操作（おかいもの・メニュー）は {UI_STOP_AT} を超えたので止めた")
    print(f"今日 押された {t.get('clicks', 0)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
