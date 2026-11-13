# 11/13 検索の作り替え：街ページ・実家ページに「その街だけの数字」を足す部品（関西 towns.py・関東 fudosan_kanto.py で同じ物を使う）
# 数字は総務省統計局の公式（国勢調査 2020・2025年／住宅・土地統計調査 2018・2023年）。e-Stat 統計ダッシュボードから取った物を toukei.json に置く。
# 取れていない数字は出さない（文も作らない）。確かめていない言い切り（住みやすい・人気 など）は書かない。
import json, os, html

E = html.escape
SRC_NAME = "総務省統計局「国勢調査」（2020年・2025年）・「住宅・土地統計調査」（2018年・2023年）"
SRC_URL = "https://dashboard.e-stat.go.jp/"
GOT = "2026年11月13日"
LASTMOD = "2026-11-13"


def load(path):
    if not os.path.exists(path):
        return {}
    return json.load(open(path, encoding="utf-8"))


def _r(d, k):
    v = d.get(k)
    return None if v in (None, "", "-") else float(v)


def calc(d):
    """1つの市区町村の数字から、ページに出す値を作る（無い物は None）"""
    if not d:
        return {}
    p20, p25, h20, h25 = _r(d, "p20"), _r(d, "p25"), _r(d, "h20"), _r(d, "h25")
    a18, a23, j18, j23 = _r(d, "a18"), _r(d, "a23"), _r(d, "j18"), _r(d, "j23")
    o20, o25 = _r(d, "o20"), _r(d, "o25")
    c = {"p20": p20, "p25": p25, "h20": h20, "h25": h25, "o20": o20, "o25": o25, "a18": a18, "a23": a23, "j18": j18, "j23": j23}
    c["pg"] = round((p25 - p20) / p20 * 100, 1) if p20 and p25 else None
    c["pge"] = (p25 - p20) / p20 * 100 if p20 and p25 else None  # 比べる時は丸める前の値で
    c["pd"] = int(p25 - p20) if p20 and p25 else None
    c["pph"] = round(p25 / h25, 2) if p25 and h25 else None
    c["hg"] = int(h25 - h20) if h20 and h25 else None
    c["vr"] = round(a23 / j23 * 100, 1) if a23 and j23 else None
    c["vr18"] = round(a18 / j18 * 100, 1) if a18 and j18 else None
    c["vd"] = int(a23 - a18) if a18 is not None and a23 is not None else None
    return c


def ranks(towns, T, key):
    """同じ府県の、このリストの街の中での順位（大きい順）。towns は {n, p, code} の並び"""
    out = {}
    by = {}
    for t in towns:
        v = calc(T.get(t["code"], {})).get(key)
        if v is not None:
            by.setdefault(t["p"], []).append((v, t["n"]))
    for p, vs in by.items():
        vs.sort(key=lambda x: -x[0])
        for i, (v, n) in enumerate(vs, 1):
            out[(p, n)] = (i, len(vs))
    return out


def _yen(n):
    return f"{int(n):,}"


def _pm(v, unit=""):
    return (f"+{v:,}" if v > 0 else f"{v:,}" if v < 0 else "±0") + unit


def _pct(v):
    return f"+{v:.1f}%" if v > 0 else f"{v:.1f}%" if v < 0 else "±0%"


def _pg(c):
    """人口の増減率。0.1%より小さい動きは「±0%」と書かず、小数2けたで出す（+30人なのに±0% と見えないように）"""
    if c.get("p20") and c.get("p25"):
        g = (c["p25"] - c["p20"]) / c["p20"] * 100
        if c["p25"] != c["p20"] and abs(g) < 0.05:
            return f"{'+' if g > 0 else ''}{g:.2f}%"
    return _pct(c["pg"])


def sentences(n, pfull, c, pc, rk_p=None, rk_v=None):
    """街だけの文。c＝その街、pc＝府県全体。言えることだけを書く"""
    s = []
    if c.get("p25"):
        t = f"{n}の人口は{_yen(c['p25'])}人（2025年10月1日の国勢調査）。"
        if c.get("pg") is not None:
            t += f"2020年の{_yen(c['p20'])}人から{_pm(c['pd'], '人')}（{_pg(c)}）で、5年で{'増えました' if c['pd'] > 0 else '減りました' if c['pd'] < 0 else '変わっていません'}。"
            if pc.get("pg") is not None:
                g, pg = c["pge"], pc["pge"]
                if abs(g - pg) < 0.05:
                    t += f"{pfull}全体（{_pct(pg)}）とほぼ同じ動きです。"
                elif g > pg:
                    pg_s = _pct(pc["pg"])
                    t += (f"{pfull}全体（{pg_s}）が減る中で、人が増えている街です。" if g > 0 and pg < 0 else
                          f"{pfull}全体（{_pct(pg)}）より増え方が大きい街です。" if g > 0 else
                          f"{pfull}全体（{_pct(pg)}）より減り方が小さい街です。")
                else:
                    t += (f"{pfull}全体（{_pct(pg)}）は増える中で、人が減っている街です。" if g < 0 and pg > 0 else
                          f"{pfull}全体（{_pct(pg)}）より減り方が大きい街です。" if g < 0 else
                          f"{pfull}全体（{_pct(pg)}）より増え方が小さい街です。")
            if rk_p:
                t += (f"このページで比べた{pfull}の{rk_p[1]}の市区町村で、5年の人口の伸びがいちばん大きい街です。" if rk_p[0] == 1 else
                      f"5年の人口の動きを、このページで比べた{pfull}の{rk_p[1]}の市区町村で増えた順にならべると{rk_p[0]}番目です。")
        s.append(t)
    if c.get("h25") and c.get("pph"):
        t = f"世帯の数は{_yen(c['h25'])}世帯で、1世帯あたり{c['pph']:.2f}人"
        if pc.get("pph"):
            t += f"（{pfull}全体は{pc['pph']:.2f}人）"
        t += "。"
        if c.get("hg") is not None and c.get("pd") is not None and c["hg"] > 0 and c["pd"] < 0:
            t += "人は減っても、世帯の数は5年で増えています（1人・2人のくらしが増えている形です）。"
        s.append(t)
    if c.get("o25") is not None:
        # 2020年の割合は計算のしかたが2025年とちがう（年齢「不詳」の扱い）ため、5年の差は出さない
        s.append(f"65歳以上の人の割合は{c['o25']:.1f}%（2025年の国勢調査）です。")
    if c.get("vr") is not None:
        t = f"2023年の住宅・土地統計調査では、住宅{_yen(c['j23'])}戸のうち空き家が{_yen(c['a23'])}戸で、空き家の割合は{c['vr']:.1f}%"
        if pc.get("vr") is not None:
            t += f"（{pfull}全体は{pc['vr']:.1f}%）"
        t += "。"
        if c.get("vd") is not None:
            t += f"2018年の{_yen(c['a18'])}戸から{_pm(c['vd'], '戸')}です。" if c["vd"] else "2018年と同じ戸数です。"
        if rk_v:
            t += (f"このページで比べた{pfull}の{rk_v[1]}の市区町村で、空き家の割合がいちばん高い街です。" if rk_v[0] == 1 else
                  f"このページで比べた{pfull}の{rk_v[1]}の市区町村で、空き家の割合が高い方から{rk_v[0]}番目です。")
        s.append(t)
    return s


def machi_block(n, short_n, pfull, c, pc, rk_p=None, rk_v=None, rk_href=""):
    """街ページ（地価）の中に入れる箱。既存の .big（2列の数字）と h2・.cap を使う"""
    if not c or not c.get("p25"):
        return ""
    cells = [("人口（2025年）", f'{_yen(c["p25"])}<small style="font-size:13px">人</small>')]
    if c.get("pg") is not None:
        cells.append(("5年の人口の増減", _pg(c)))
    if c.get("o25") is not None:
        cells.append(("65歳以上の割合", f'{c["o25"]:.1f}<small style="font-size:13px">%</small>'))
    if c.get("vr") is not None:
        cells.append(("空き家の割合（2023年）", f'{c["vr"]:.1f}<small style="font-size:13px">%</small>'))
    big = '<div class="big" style="margin-top:6px">' + "".join(f'<div><span>{E(a)}</span><b style="color:#2B2622;font-size:21px">{b}</b></div>' for a, b in cells) + '</div>'
    tx = "".join(f'<p style="font-size:13.5px;line-height:1.95;color:#4E453F;margin:12px 0 0">{E(x)}</p>' for x in sentences(n, pfull, c, pc, rk_p, rk_v))
    return (f'<h2>数字で見る{E(short_n)}のくらし</h2><p class="cap">国の統計（国勢調査・住宅・土地統計調査）の、{E(n)}の数字です。</p>'
            + big + tx
            + '<p class="cap" style="margin-top:10px">空き家には、借り手・買い手を待っている賃貸用・売却用の住宅もふくみます。住宅・土地統計調査は、調べた家から全体を見積もった数字（推計）です。</p>'
            + (f'<a class="back" href="{rk_href}" data-k="街ページ｜空き家ランキング" style="margin-top:14px">{E(pfull)}の空き家の割合ランキングを見る</a>' if rk_href and c.get("vr") is not None else ''))


def jikka_block(n, pfull, c, pc, rk_v=None, rk_href=""):
    """実家ノートに入れる箱（空き家と65歳以上）。既存の .jn（2列の数字）と .mk3・.jh・.src を使う"""
    if not c or c.get("vr") is None:
        return ""
    cells = [(f'{_yen(c["a23"])}<small>戸</small>', f'空き家の数（2023年・住宅の{c["vr"]:.1f}%）')]
    if c.get("vd") is not None:
        cells.append((f'{_pm(c["vd"])}<small>戸</small>', f'2018年からの空き家の増減（2018年は{_yen(c["a18"])}戸）'))
    if c.get("o25") is not None:
        cells.append((f'{c["o25"]:.1f}<small>%</small>', '65歳以上の人の割合（2025年）'))
    if c.get("p25"):
        cells.append((f'{_yen(c["p25"])}<small>人</small>', '人口（2025年）' + (f'・5年で{_pct(c["pg"])}' if c.get("pg") is not None else '')))
    g = '<div class="jn">' + "".join(f'<div><b>{a}</b><span>{E(b)}</span></div>' for a, b in cells) + '</div>'
    t = f"{n}の空き家の割合は{c['vr']:.1f}%"
    if pc.get("vr") is not None:
        t += f"で、{pfull}全体の{pc['vr']:.1f}%より{'高く' if c['vr'] > pc['vr'] else '低く' if c['vr'] < pc['vr'] else 'ほぼ同じで'}"
        t += "なっています。" if c['vr'] != pc['vr'] else "す。"
    else:
        t += "です。"
    if rk_v:
        t += (f"このノートで比べた{pfull}の{rk_v[1]}の市区町村で、いちばん高い割合です。" if rk_v[0] == 1 else
              f"このノートで比べた{pfull}の{rk_v[1]}の市区町村で、高い方から{rk_v[0]}番目です。")
    if c.get("vd"):
        t += f"5年で{abs(c['vd']):,}戸{'増えました' if c['vd'] > 0 else '減りました'}。"
    return (f'<p class="mk3">DATA</p><h2 class="jh">{E(n)}の空き家と、くらす人</h2>{g}'
            f'<p style="font-size:13px;line-height:1.9;color:#4E453F;margin:12px 0 0">{E(t)}</p>'
            f'<p class="src">出典：{E(SRC_NAME)}（{E(SRC_URL)}・{GOT}に取得）。空き家には賃貸用・売却用の住宅もふくみ、住宅・土地統計調査は推計の数字です。</p>'
            + (f'<a class="jl" href="{rk_href}" data-k="実家｜空き家ランキング">{E(pfull)}の空き家の割合ランキング <i>→</i></a>' if rk_href else ''))


def faq(n, pfull, c, pc):
    out = []
    if c.get("pg") is not None:
        a = f"2025年の国勢調査で{n}の人口は{_yen(c['p25'])}人、2020年から{_pm(c['pd'], '人')}（{_pg(c)}）でした。"
        if pc.get("pg") is not None:
            a += f"{pfull}全体は{_pct(pc['pg'])}です。"
        out.append((f"{n}の人口は増えていますか？", a))
    if c.get("vr") is not None:
        a = f"2023年の住宅・土地統計調査で、{n}の空き家は{_yen(c['a23'])}戸、住宅のうち{c['vr']:.1f}%でした。"
        if pc.get("vr") is not None:
            a += f"{pfull}全体は{pc['vr']:.1f}%です。"
        a += "空き家には賃貸用・売却用の住宅もふくみます（推計の数字）。"
        out.append((f"{n}の空き家はどのくらいありますか？", a))
    return out


def desc_add(n, c):
    if c.get("pg") is None:
        return ""
    t = f"人口{_yen(c['p25'])}人（5年で{_pg(c)}）"
    if c.get("vr") is not None:
        t += f"・空き家の割合{c['vr']:.1f}%"
    return t + "。"


def note(c):
    if not c or not c.get("p25"):
        return ""
    return f"人口・世帯・65歳以上・空き家：{SRC_NAME}。e-Stat 統計ダッシュボード {SRC_URL}（{GOT}に取得）"


def akiya_items(towns, T):
    """空き家の割合ランキングの並び。towns は {id, n, p, code, href} の並び"""
    out = []
    for t in towns:
        c = calc(T.get(t["code"], {}))
        if c.get("vr") is not None:
            out.append(dict(t, vr=c["vr"], a23=int(c["a23"]), vd=c.get("vd")))
    return sorted(out, key=lambda x: -x["vr"])


def akiya_ol(items, show_pref, color):
    """地価ランキングと同じ形（li.r・.no・.nm・.bar・.v）で空き家の割合を並べる"""
    if not items:
        return ""
    mx = max(x["vr"] for x in items) or 1
    out, prev, pr = [], None, 0
    for i, x in enumerate(items, 1):
        if x["vr"] != prev:
            pr = i
        prev = x["vr"]
        c = color(x["p"])
        out.append(f'<li class="r{" top" if pr <= 3 else ""}" style="--c:{c}"><a href="{x["href"]}" data-k="空き家ランキング｜{E(x["n"])}">'
                   f'<span class="no">{pr}</span><span class="nm">{E(x["n"])}' + (f'<small>{E(x["p"])}</small>' if show_pref else '') + f'<small>{x["a23"]:,}戸</small></span>'
                   f'<span class="bar"><b class="z" style="left:0%"></b><i style="left:0%;width:{x["vr"] / mx * 100:.1f}%"></i></span>'
                   f'<span class="v" style="color:{c}">{x["vr"]:.1f}%</span></a></li>')
    return "\n".join(out)


def akiya_page(region, en, brand, logo, items, panes, head_fn, css, scripts, beacon_html, base, color, back_href, back_label):
    """空き家の割合ランキング（/akiya-ranking）。panes = [(key, 府県の短い名前, 府県の名前)]。地価ランキングと同じ形"""
    if not items:
        return ""
    top = items[0]
    allv = [x["vr"] for x in items]
    med = sorted(allv)[len(allv) // 2]
    desc = (f"{region}の{len(items)}の市区町村の空き家の割合（2023年 住宅・土地統計調査）を、高い順に並べました。"
            f"いちばん高いのは{top['n']}（{top['p']}）の{top['vr']:.1f}%。府県ごとにも見られます。実家・空き家を売る・片付ける・解体する前に。")
    faq = [(f"{region}で空き家の割合がいちばん高い街は？",
            f"2023年の住宅・土地統計調査で比べると、このページの{len(items)}の市区町村では{top['n']}（{top['p']}）の{top['vr']:.1f}%がいちばん高い割合でした。"),
           ("空き家の割合はどうやって出していますか？",
            "住宅・土地統計調査の「空き家の数」を「住宅の数」で割った割合です。空き家には、借り手・買い手を待っている賃貸用・売却用の住宅や、別荘などもふくみます。調べた家から全体を見積もった数字（推計）です。"),
           ("のっていない町や村があるのはなぜ？",
            "住宅・土地統計調査は、人口の少ない町や村の数字を出していません。数字の出ている市区町村だけをのせています。")]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Dataset", "name": f"{region}の市区町村 空き家の割合ランキング（2023年 住宅・土地統計調査）", "description": desc, "temporalCoverage": "2023-10-01", "spatialCoverage": region, "isBasedOn": SRC_URL},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]}
    pl = [("all", "すべて", region + "ぜんぶ", items, True)] + [(k, p, pn, [x for x in items if x["p"] == p], False) for k, p, pn in panes]
    pl = [x for x in pl if x[3]]
    h = head_fn(f"{region} 空き家の割合ランキング｜{len(items)}の市区町村（2023年 住宅・土地統計調査）", desc, f"{base}/akiya-ranking", ld)
    body = (f'<style>{css}</style>{scripts}</head><body><div class="wrap">'
            f'<div class="head"><img src="{logo}" width="60" height="60" alt="{brand} のロゴ"><div class="en">{en} ─ AKIYA</div>'
            f'<h1>{E(region)} 空き家の割合ランキング<span>2023年 住宅・土地統計調査</span></h1>'
            f'<p class="sub">{len(items)}の市区町村の空き家の割合を、<br>国の統計の数字で並べました。</p>'
            f'<div class="upd">2023年10月1日時点の数字（{GOT} 作成）</div></div>'
            f'<div class="sum"><div><span>{E(region)}の1位</span><em>{E(top["n"])}</em><b>{top["vr"]:.1f}%</b></div><div><span>まん中の街の割合</span><em>{len(items)}の街のうち</em><b>{med:.1f}%</b></div></div>'
            '<nav class="flt">' + "".join(f'<button data-p="{k}" style="--pc:{color(p) if k != "all" else "#2B2622"}"{" class=\"on\"" if k == "all" else ""}>{E(p)}</button>' for k, p, _, _, _ in pl) + '</nav>'
            + "".join(f'<section class="pane{" on" if k == "all" else ""}" id="{k}"><h2 style="--pc:{color(p) if k != "all" else "#B97A62"}">{E(pn)}の空き家の割合</h2><p class="cap">高い順です。押すと、その街のページが開きます。</p><ol>{akiya_ol(ts, sp, color)}</ol></section>' for k, p, pn, ts, sp in pl)
            + '<section class="faq"><h2>よくある質問</h2>' + "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faq) + '</section>'
            + f'<p class="note">出典：総務省統計局「住宅・土地統計調査」（2023年）。e-Stat 統計ダッシュボード {SRC_URL}（{GOT}に取得）<br>空き家の割合＝空き家の数÷住宅の数。空き家には賃貸用・売却用の住宅や別荘もふくみます。推計の数字です。</p>'
            + f'<a class="back" href="{back_href}" data-k="空き家ランキング｜戻る">{E(back_label)}</a><div class="ft">{brand}</div></div>'
            + '<script>(function(){function go(k){var b=document.querySelector(\'.flt button[data-p="\'+k+\'"]\');if(!b)return;document.querySelectorAll(".flt button,.pane").forEach(function(x){x.classList.remove("on")});b.classList.add("on");document.getElementById(k).classList.add("on");}'
            + 'document.querySelectorAll(".flt button").forEach(function(b){b.onclick=function(){go(b.dataset.p);history.replaceState(null,"","#"+b.dataset.p);}});if(location.hash)go(location.hash.slice(1));})();</script>'
            + beacon_html + '</body></html>')
    return h + body
