"""11/19 写真が出る前のぼかし色（ThumbHash・github.com/evanw/thumbhash）。
assets/ph/t/*.webp（小さい写真）から 1枚25字ほどの印を作り assets/phh.json に。hitech2.js が読む前の背景に使う。
python3 scripts/hx_phh.py site/assets（関西は usagi tools/hx/phh.py）"""
import json, os, sys
import thumbhash

A = sys.argv[1] if len(sys.argv) > 1 else "links/assets"
out = os.path.join(A, "phh.json")
old = {}
try:
    old = json.load(open(out))
except Exception:
    pass
res = {}
for d in ("t", ""):
    p = os.path.join(A, "ph", d)
    if not os.path.isdir(p):
        continue
    for f in sorted(os.listdir(p)):
        if not f.endswith(".webp") or f in res:
            continue
        if f in old:
            res[f] = old[f]; continue
        try:
            res[f] = thumbhash.image_to_thumbhash(os.path.join(p, f))
        except Exception as e:
            print("skip", f, e)
json.dump(res, open(out, "w"), separators=(",", ":"))
print(len(res), "枚", out)
