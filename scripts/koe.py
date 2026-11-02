"""11/2 オーナー「テスターが必要」→ /koe から届いた声（リクエスト・感想）を KV から data/koe.json に移す。
KV のキー koe|日時|乱数 を読み、data/koe.json に足してから KV から消す（functions/koe-send.js が置く）。
公開するのはオーナーがOKした物だけ：data/koe_public.json（scripts/koe_page.py が /koe に載せる）。
使い方: python3 scripts/koe.py <KVのID>"""
import json, sys
from lib import load_json, save_json, path
from pagestats import _wr, list_keys


def main():
    ns = sys.argv[1] if len(sys.argv) > 1 else ""
    if not ns:
        return 0
    keys = list_keys(ns, "koe|") or []
    fp = path("data", "koe.json")
    data = load_json(fp, {}) or {}
    items = data.get("items", [])
    seen = {i.get("key") for i in items}
    new = 0
    for k in keys:
        name = k.get("name", "")
        if name in seen:
            _wr(["kv", "key", "delete", f"--namespace-id={ns}", name])
            continue
        r = _wr(["kv", "key", "get", f"--namespace-id={ns}", name])
        if r.returncode != 0:
            continue
        txt = r.stdout.strip()
        try:
            v = json.loads(txt[txt.find("{"):])
        except Exception:
            continue
        v["key"] = name
        v["public"] = False
        items.append(v)
        new += 1
        _wr(["kv", "key", "delete", f"--namespace-id={ns}", name])
    items.sort(key=lambda i: i.get("at", ""))
    save_json(fp, {"about": "/koe から届いた声。public はオーナーがOKした物だけ true（公開は data/koe_public.json）", "items": items})
    print(f"届いた声 {new}件（ぜんぶで {len(items)}件）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
