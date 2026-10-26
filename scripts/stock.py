"""HPの在庫（おでかけ・お店・商品）の見張り。毎朝、数字係のあとに動き、notes/stock.md に書く。

10/26 オーナー「中途半端ならダメ」「漏らさず」：数が足りない欄、終わった物、開けないリンクを機械が数えて×を出す。
集め係（docs/collector-prompt.md）は最初にこれを読み、×の欄から埋める。
終わった催し（ends を1日過ぎた物）と開店から31日たったお店は、data/page-spots.json から自動で消す。
"""
import json
import os
import re
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import JST, load_json, now_jst, path  # noqa: E402
import page  # noqa: E402

# 欄ごとの最低の数（都県ごと）。投稿した物と合わせて数える（10/26 オーナー「関東おでかけリスト」「月の見て、綺麗に分けてる」）
NEED = {"now": 8, "up": 4, "soon": 2, "new": 2}  # 欄の名前の並びに使う
NEED_PREF = {"東京": {"now": 8, "up": 2}, "神奈川": {"now": 4, "up": 2}, "埼玉": {"now": 4, "up": 2}, "千葉": {"now": 4, "up": 2},
             "茨城": {"now": 3, "up": 2}, "栃木": {"now": 3, "up": 2}, "群馬": {"now": 3, "up": 2}}
NEED_SHOP = 4  # 新しいお店（もうすぐ＋できた）は関東全体で
TAB = {"now": "開催中", "up": "これから", "soon": "もうすぐ（開店前のお店）", "new": "できた（開いたお店）"}
NEED_GOODS_TOTAL = 30
NEED_GOODS_CAT = 5
PREFS = tuple(NEED_PREF)


def prune(now, fp=None):
    """終わった物を page-spots.json から消す。消した題を返す。"""
    fp = fp or path("data", "page-spots.json")
    data = load_json(fp, {}) or {}
    keep, gone = [], []
    for it in data.get("items", []):
        end = page._dt(it.get("ends"))
        od = page._dt(it.get("open")) if it.get("kind") == "shop" else None
        if (end and end < now - timedelta(days=1)) or (od and od < now - timedelta(days=31)):
            gone.append(it.get("title", ""))
            continue
        keep.append(it)
    if gone:
        data["items"] = keep
        with open(fp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
    return gone


def _open_day(e, now):
    d = page._dt(e.get("open"))
    if d:
        return d.date()
    m = re.search(r"(\d{1,2})/(\d{1,2})(?:（.）)?\s*(?:に)?開店", (e.get("name") or "") + e.get("title", ""))
    try:
        return datetime(now.year, int(m[1]), int(m[2]), tzinfo=JST).date() if m else None
    except ValueError:
        return None


def tabs(now):
    """HPと同じ分け方で、地域ごと・欄ごとの物を返す。"""
    items, _ = page.collect(now, light=True)
    page._NOW[:] = [now]
    out = {r: {k: [] for k in NEED} for r in PREFS}
    for e in page.all_spots(items, now):
        r = page._pref(e)
        if r not in out:
            continue
        if e.get("kind") == "shop":
            od = _open_day(e, now)
            k = "soon" if od and od > now.date() else "new"
        else:
            st = page._dt(e.get("start"))
            k = "up" if st and st > now else "now"
        out[r][k].append(e)
    return out


def goods(now):
    """商品の置き場の数を、買い物の項目ごとに（楽天には聞かない。売り切れはHPを作る時に外れる）。"""
    cs = page.cats(now)
    keys = []
    for k, _, name, *_ in cs:  # 時期の項目と同じ key（food など）は1つにまとめる
        if k not in ("stay", "book", "sale") and k not in dict(keys):
            keys.append((k, name))
    cnt = Counter()
    for it in page.goods_store(now):
        line = (it.get("comment") or "").split("\n")[0]
        k = it.get("cat") if it.get("cat") in dict(keys) else page._cat(" ".join([it.get("expect", ""), line]), cs)
        cnt[k] += 1
    return keys, cnt


def dead_links(now, timeout=12):
    """page-spots.json の公式ページを開いてみる。開けない物（404など）を返す。商品はHPを作る時に楽天で確かめている。"""
    urls = [(it.get("title", ""), it.get("url", "")) for it in (load_json(path("data", "page-spots.json"), {}) or {}).get("items", [])]
    bad = []
    for name, u in urls:
        if not u.startswith("https://"):
            bad.append((name, u, "https でない"))
            continue
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (akari-auto link check)"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                code = r.status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception as e:  # つながらない
            code = type(e).__name__
        # 403・429・503 は「機械お断り」のサイトが多いので×にしない（人が開けば見られる）
        if code in (404, 410) or (isinstance(code, str)):
            bad.append((name, u, str(code)))
    return bad


def dupes():
    seen, out = {}, []
    for it in (load_json(path("data", "page-spots.json"), {}) or {}).get("items", []):
        k = re.sub(r"\W", "", it.get("title", "")).lower()[:14]
        if k in seen:
            out.append(it.get("title", ""))
        seen[k] = 1
    return out


def report(now, check_links=True):
    gone = prune(now)
    t = tabs(now)
    keys, gc = goods(now)
    bad = dead_links(now) if check_links else []
    dup = dupes()
    short = []
    lines = [f"# HPの在庫（{now:%m/%d %H:%M} 機械が数えた）", "",
             "集め係・夜の回は、×の欄から埋める。数は投稿した物とHPだけの物を合わせた、今HPに並んでいる数。", "",
             "## おでかけ（都県ごと）", "", "| 都県 | 開催中 | これから | 目標 |", "|---|---|---|---|"]
    for r, need in NEED_PREF.items():
        row = []
        for k in ("now", "up"):
            n = len(t[r][k])
            row.append(f"{n} {'○' if n >= need[k] else '×'}")
            if n < need[k]:
                short.append(f"{r}の{TAB[k]}があと{need[k] - n}件")
        lines.append(f"| {r} | {row[0]} | {row[1]} | 開催中{need['now']}・これから{need['up']} |")
    ns, nn = sum(len(t[r]["soon"]) for r in PREFS), sum(len(t[r]["new"]) for r in PREFS)
    lines.append(f"| 新しいお店（関東全体） | もうすぐ{ns}・できた{nn} | {'○' if ns + nn >= NEED_SHOP else '×'} | 合わせて{NEED_SHOP} |")
    if ns + nn < NEED_SHOP:
        short.append(f"新しいお店（もうすぐ・できた）が関東であと{NEED_SHOP - ns - nn}件")
    total = sum(gc.values())
    lines += ["", "## 商品の置き場（data/page-goods.json）", "", "| 項目 | 数 | 目標 |", "|---|---|---|"]
    for k, name in keys:
        n = gc.get(k, 0)
        lines.append(f"| {name} | {n} {'○' if n >= NEED_GOODS_CAT else '×'} | {NEED_GOODS_CAT}件 |")
        if n < NEED_GOODS_CAT:
            short.append(f"商品の「{name}」があと{NEED_GOODS_CAT - n}件")
    lines.append(f"| 合計 | {total} {'○' if total >= NEED_GOODS_TOTAL else '×'} | {NEED_GOODS_TOTAL}件 |")
    if total < NEED_GOODS_TOTAL:
        short.append(f"商品が合計であと{NEED_GOODS_TOTAL - total}件")
    # これから終わる物（3日以内）：代わりを先に探す
    soon_end = sorted({e["title"] for r in PREFS for e in t[r]["now"]
                       if page._dt(e.get("ends")) and page._dt(e["ends"]) < now + timedelta(days=3)})
    lines += ["", "## 足りない物", ""] + ([f"- × {s}" for s in short] or ["- なし（全部○）"])
    lines += ["", "## 3日以内に終わる（代わりを先に探す）", ""] + ([f"- {x}" for x in soon_end] or ["- なし"])
    lines += ["", "## 開けないリンク（直すか消す）", ""] + ([f"- {n}：{u}（{c}）" for n, u, c in bad] or ["- なし"])
    lines += ["", "## 同じ物が2つ（1つ消す）", ""] + ([f"- {x}" for x in dup] or ["- なし"])
    lines += ["", "## 今朝、終わったので消した物", ""] + ([f"- {x}" for x in gone] or ["- なし"])
    ok = not short and not bad and not dup
    lines.insert(2, f"判定：{'○ 全部そろっています' if ok else '× ' + '、'.join((short + [f'開けないリンク{len(bad)}件'] * bool(bad) + [f'重なり{len(dup)}件'] * bool(dup))[:6])}")
    lines.insert(3, "")
    return "\n".join(lines) + "\n", ok


def main(argv):
    now = now_jst()
    if "--now" in argv:
        now = datetime.fromisoformat(argv[argv.index("--now") + 1]).replace(tzinfo=JST)
    text, ok = report(now, check_links="--no-links" not in argv)
    with open(path("notes", "stock.md"), "w", encoding="utf-8") as fh:
        fh.write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
