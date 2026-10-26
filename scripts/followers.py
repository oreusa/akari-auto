"""フォロワー数の記録（X・Threads・インスタ）。毎朝、数字係のあとに動き、data/followers.json に1日1行足す。

10/26 オーナー「Threads、インスタも インプとフォロワー」。燈のBufferのカギ（GitHub Actions の BUFFER_API_KEY）だけを使う。
Buffer のAPIにフォロワーの欄があるかは、まず型の一覧（introspection）で確かめ、見つかった欄だけを聞く。
見つからない日は「取れない」と1行残すだけで、ほかの係は止めない。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import buffer_gql, load_json, now_jst, path, save_json  # noqa: E402

WORDS = ("follow", "audience", "fan", "subscriber")


def type_fields(name):
    d = buffer_gql('query($n: String!) { __type(name: $n) { fields { name args { name } type { name kind ofType { name kind ofType { name } } } } } }', {"n": name})
    return (d.get("__type") or {}).get("fields") or []


def base(t):
    while t and not t.get("name"):
        t = t.get("ofType")
    return (t or {}).get("name"), (t or {}).get("kind")


def find_paths():
    """Channel の中で、フォロワーらしい数の欄を探す（2段まで）。"""
    out = []
    for f in type_fields("Channel"):
        n, k = base(f["type"])
        if any(w in f["name"].lower() for w in WORDS) and k in ("SCALAR", None) and not f["args"]:
            out.append(f["name"])
        elif k == "OBJECT" and not f["args"]:
            for g in type_fields(n):
                gn, gk = base(g["type"])
                if any(w in g["name"].lower() for w in WORDS) and gk == "SCALAR" and not g["args"]:
                    out.append(f"{f['name']} {{ {g['name']} }}")
    return out


def main():
    cfg = load_json(path("config.json"))
    if not cfg or not cfg.get("channels"):
        return 0
    fields = find_paths()
    print("フォロワーらしい欄:", fields or "なし")
    fp = path("data", "followers.json")
    data = load_json(fp, {}) or {}
    day = now_jst().strftime("%Y-%m-%d")
    row = {}
    if fields:
        q = "query($o: OrganizationId!) { channels(input: {organizationId: $o}) { id service %s } }" % " ".join(fields)
        try:
            chans = buffer_gql(q, {"o": cfg["organizationId"]})["channels"] or []
        except Exception as e:  # 欄はあっても聞けない時
            print("取れない:", str(e)[:300])
            chans = []
        mine = set(cfg["channels"].values())
        for c in chans:
            if c.get("id") not in mine:
                continue
            vals = {}
            for k, v in c.items():
                if isinstance(v, dict):
                    vals.update({kk: vv for kk, vv in v.items() if isinstance(vv, (int, float))})
                elif isinstance(v, (int, float)) and k not in ("id",):
                    vals[k] = v
            if vals:
                row[c.get("service")] = vals
    data.setdefault("days", {})[day] = row or {"note": "Bufferからは取れない（欄なし）"}
    data["fields"] = fields
    save_json(fp, data)
    print(day, row or "取れない")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("フォロワー数は取れませんでした:", str(e)[:300])
        sys.exit(0)
