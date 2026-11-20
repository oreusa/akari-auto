"""11/20 owner「検索ヒットなるように頑張りたい」→ 新しいページ（shin）は中身を全部 JS で描くので、HTML だけを読む検索の機械には
題の1行しか見えず、1件ページ（/o/）・街のページ（/machi/）・開店閉店のページへのリンクも無かった。
各ページの下に「一覧」（たたんだ details）を HTML のまま書く。見えている中身と同じ物だけ（隠しの文字ではない）。
関西 tools/shin/ix.py と関東 akari scripts/shin/ix.py は同じ物（片方を直したら両方）。"""
import os, html

E = lambda s: html.escape(str(s or ""), quote=True)
W = "月火水木金土日"


def _md(d):
    try:
        y, m, dd = d[:10].split("-"); return f"{int(m)}/{int(dd)}"
    except Exception:
        return ""


def _li(href, t, sub):
    a = f'<a href="{E(href)}">{E(t)}</a>' if href else f"<b>{E(t)}</b>"
    return f"<li>{a}{('<span>' + E(sub) + '</span>') if sub else ''}</li>"


def ix_html(name, data, root):
    """root＝公開フォルダ（links か site）。リンク先のファイルがある時だけリンクにする"""
    if not isinstance(data, dict): return ""
    has = lambda p: os.path.exists(os.path.join(root, p.strip("/") + ".html"))
    rows, label = [], ""
    items = data.get("items") if isinstance(data.get("items"), list) else None
    if items and isinstance(items[0], dict):
        if name.startswith("kaiten"): label = "開店・閉店の一覧"
        elif name.startswith("ranking"): label = "ランキングの一覧"
        elif name.startswith("hatsumode"): label = "初詣の一覧"
        elif name.startswith("illumination"): label = "イルミネーションの一覧"
        elif name.startswith("koyo"): label = "紅葉の一覧"
        elif name.startswith("tomari"): label = "泊まりで行くおでかけの一覧"
        elif name.startswith("ima"): label = "いまから行けるおでかけの一覧"
        else: label = "このページのおでかけ一覧"
        pg = data.get("page") if isinstance(data.get("page"), dict) else {}
        if pg.get("p"): items = [x for x in items if x.get("p") == pg["p"]]  # 府県・都県のページはその府県だけ（JS の絞り込みと同じ）
        for x in items[:400]:
            t = x.get("t")
            if not t: continue
            href = ""
            if x.get("o") and has("/o/" + x["o"]): href = "/o/" + x["o"]
            elif name.startswith("kaiten") and x.get("id") and has("/kaiten/" + x["id"]): href = "/kaiten/" + x["id"]
            when = x.get("d") or ((f"{_md(x['s'])}〜" if x.get("s") else "") + (_md(x["e"]) if x.get("e") else ""))
            if when and when.endswith("〜"): when = when + "（公式で確認）"
            place = x.get("v") or x.get("a") or ""
            sub = "・".join(v for v in (x.get("p", ""), place[:40], when) if v)
            rows.append(_li(href, t, sub))
    elif isinstance(data.get("towns"), list):
        label = "街の一覧（家と土地の相場）"
        for x in data["towns"]:
            if not x.get("id") or not x.get("n"): continue
            href = "/machi/" + x["id"] if has("/machi/" + x["id"]) else ""
            rows.append(_li(href, x["n"], x.get("p", "")))
    elif isinstance(data.get("ft"), list):
        # 表紙：サイトの中身（足の案内と同じ分け方）と、いま載っているおでかけ
        label = "このサイトの中身"
        for grp in data["ft"]:
            if not (isinstance(grp, list) and len(grp) == 2): continue
            for t, u in grp[1]:
                rows.append(_li(u, t, grp[0]))
        for x in ((data.get("od") or {}).get("ph") or [])[:20]:
            if x.get("o") and has("/o/" + x["o"]): rows.append(_li("/o/" + x["o"], x.get("t", ""), "・".join(v for v in (x.get("p", ""), (_md(x["e"]) + "まで") if x.get("e") else "") if v)))
    if not rows: return ""
    # 表紙は同じリンクが画面に描かれる（足の案内）ので、HTML の写しは見せない（JS が無い時の案内だけ）
    cls = "ix ixh" if isinstance(data.get("ft"), list) and not items else "ix"
    return (f'<section class="{cls}" aria-label="{E(label)}"><details><summary>{E(label)}（{len(rows)}件）</summary>'
            f'<ul>{"".join(rows)}</ul></details></section>')


def pre_html(data):
    """読み物のページ（data に html がある物）は、#app の中に同じ文を HTML のまま置く（JS が描くと入れ替わる）"""
    if not isinstance(data, dict) or not isinstance(data.get("html"), str) or not data["html"].strip(): return ""
    return f'<article class="pre"><h1>{E(data.get("h1", ""))}</h1>{data["html"]}</article>'
