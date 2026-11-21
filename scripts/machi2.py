"""11/20 19:00 owner「完璧？他社より使いやすく見やすくお洒落？」→ 街のページ（/machi/<id>）は前のページに頭とバーをかぶせただけ。
新しい形の見本を、今のページの数字から作る（見本だけ・noindex）。OK が出たら towns.py / akari fudosan_kanto.py の town_page をこの形にする。

使い方: python3 tools/shin/machi_mihon.py <今の街のページ.html> <出す所.html>
形（tanosu の決まり：白地に細い線・同じ形の2列カード・字は 3 つの大きさ・色は目印だけ）：
  ① 街の名前（大）＋ 府県
  ② 数字のカード 2列×2（マンション・一戸建て／地価・人口 … 無い物は空き家・平均の地価で埋める）。件数を必ず出す
  ③ ひとことの答え（前の年より…）
  ④ うちの家はいくら？（主役のボタン 1 つ）＋ 無料で聞く
  ⑤ 近くの街とくらべる（skin.js の cmpTowns がここ #itt の前に入る）
  ⑥ この街で探す（売り出し中・広告）
  ⑦ 実家・空き家・解体（行き先 3 つ）
  ⑧ くらしの数字（表）・よくある質問（たたむ）・出典（小さく）
"""
import html as _h
import re
import sys

E = _h.escape


def text(h):
    b = re.sub(r"<style[\s\S]*?</style>|<script[\s\S]*?</script>|<svg[\s\S]*?</svg>", "", h)
    b = b[b.find("<body"):]
    t = re.sub(r"<[^>]+>", "\n", b)
    t = _h.unescape(t)
    return [x.strip() for x in t.split("\n") if x.strip()]


def after(L, key, n=1):
    for i, x in enumerate(L):
        if x == key or x.startswith(key):
            return L[i + n] if i + n < len(L) else ""
    return ""


CSSV = "1"


def main(src, out, prod=False):
    h = open(src, encoding="utf-8").read()
    if 'data-m2="1"' in h:
        return "skip"
    L = text(h)
    kt = "LIFE NOTE" in L[-3:] or "kanto.townnote" in h
    tid = re.search(r'/machi/([a-z]+-\d+)', re.search(r'<link rel="canonical" href="([^"]+)"', h).group(1)).group(1)
    h1 = next(x for x in L if x.endswith("の地価"))
    name = h1[:-3]
    pfline = next((x for x in L if x.startswith("国の地価公示の数字で")), "")
    pfull = re.sub(r"の住宅地.*", "", after(L, "国の地価公示の数字で、"))
    pref = re.match(r"(東京都|北海道|(?:京都|大阪)府|.{2,3}県)", pfull)
    pref = pref.group(1) if pref else ""
    r8 = after(L, "住宅地 1年の動き")
    rk = after(L, pref + "での順位") if pref else ""
    rk2 = after(L, pref + "での順位", 2)
    prev = after(L, "前の年（令和7年）")
    verdict = next((x for x in L if x.startswith("前の年より")), "")
    avgp = after(L, "住宅地の平均価格（1㎡）")
    # 売れた家
    sold = []
    for lab in ("中古マンション", "中古の一戸建て"):
        try:
            i = L.index(lab, L.index("この街で売れた家の値段")) if "この街で売れた家の値段" in L else -1
        except ValueError:
            i = -1
        if i < 0:
            continue
        cnt = L[i + 1]
        if not cnt.endswith("件の平均"):
            continue
        price = L[i + 2]
        det = []
        j = i + 3
        while j < len(L) and not L[j].startswith(pref[:2] if pref else "@@") and L[j] not in ("中古の一戸建て", "IN THIS TOWN"):
            det.append(L[j]); j += 1
        cmp = L[j] if j < len(L) and L[j].startswith(pref[:2]) else ""
        sold.append((lab.replace("中古の", "中古"), cnt.replace("の平均", ""), price, "・".join(det), cmp))
    # くらし
    pop = after(L, "人口（2025年）"); pop5 = after(L, "5年の人口の増減"); old = after(L, "65歳以上の割合"); ak = after(L, "空き家の割合（2023年）")
    para = [x for x in L if x.startswith(name + "の人口は") or x.startswith("世帯の数は") or x.startswith("2023年の住宅・土地統計調査では")]
    # 近くの街
    # FAQ
    faq = []
    if "よくある質問" in L:
        i = L.index("よくある質問") + 1
        while i + 1 < len(L) and L[i].endswith("？"):
            faq.append((L[i], L[i + 1])); i += 2
    src_i = next((i for i, x in enumerate(L) if x.startswith("出典：")), None)
    srcs = []
    if src_i is not None:
        for x in L[src_i:]:
            if x in ("関西不動産リストを見る", "関東不動産リストを見る"):
                break
            srcs.append(x)
    # 行き先（今のページのリンクをそのまま使う）
    hrefs = re.findall(r'href="([^"]+)"', h)
    yh = [x for x in hrefs if "valuecommerce" in x][:3]
    ikura = next((x for x in hrefs if x.startswith("/ikura")), "/ikura")
    ask = next((x for x in hrefs if x.startswith("/moushikomi") and "lite=1" in x), "/moushikomi")
    sozoku = next((x for x in hrefs if x.startswith("/moushikomi") and "lite=1" not in x), "/moushikomi")
    kai = next((x for x in hrefs if re.match(r"/kaitai-(?!ranking)", x)), "")
    city = after(L, "大阪市の中の都島区", 0) if False else ""
    katamoji = "/moushikomi?want=%E7%89%87%E4%BB%98%E3%81%91%E3%83%BB%E9%81%BA%E5%93%81%E6%95%B4%E7%90%86%E3%81%AE%E8%A6%8B%E7%A9%8D%E3%82%8A"

    def card(k, v, u, s, cls=""):
        return (f'<div class="mc{cls}"><small>{E(k)}</small><b>{E(v)}{f"<u>{E(u)}</u>" if u else ""}</b><span>{E(s)}</span></div>')

    def num(v):
        m = re.match(r"([+\-−]?[\d,.]+)(.*)", v)
        return (m.group(1), m.group(2)) if m else (v, "")

    cards = []
    for lab, cnt, price, det, cm in sold:
        a, u = num(price)
        few = int(re.sub(r"\D", "", cnt) or 0) < 10
        cards.append(card(lab, a, u, "売れた平均・" + cnt + "・" + re.sub(r"1㎡あたり[^・]*・?", "", det) + ("・件数が少ないので目安" if few else ""), " few" if few else ""))
    a, u = num(r8)
    cards.append(card("地価（住宅地・1年）", a, u, (f"{pref}で{rk}{rk2}" if rk else "") + (f"・前の年 {prev}" if prev else ""), " up" if a.startswith("+") else " dn"))
    a, u = num(pop5)
    cards.append(card("人口（5年）", a, u, f"{pop}人・2025年" if pop else "", ""))
    if len(cards) < 4 and avgp:
        a, u = num(avgp); cards.insert(1, card("住宅地の平均（1㎡）", a, u, "2026年の地価公示", ""))
    if len(cards) < 4 and ak:
        cards.append(card("空き家の割合", ak, "%", "2023年", ""))
    if len(cards) < 4 and old:
        cards.append(card("65歳以上の割合", old, "%", "2025年", ""))
    cards = cards[:4]

    tabs = (f'<nav class="mt" aria-label="{E(name)}のページ"><a class="on" aria-current="page">値段と地価</a>'
            f'<a href="/jikka/{tid}">実家・空き家</a><a href="{kai or "/kaitai"}">{"解体の補助金" if kai else "解体・片付け"}</a></nav>')
    yrow = "".join(f'<a href="{x}" rel="sponsored noopener" target="_blank">{lab}<i>↗</i></a>' for x, lab in zip(yh, ["中古マンション", "中古一戸建て", "土地"]))
    rows = [("人口", f"{pop}人" if pop else "—", "2025年"), ("5年の人口の増減", pop5, ""), ("65歳以上の割合", f"{old}%" if old else "—", ""), ("空き家の割合", f"{ak}%" if ak else "—", "2023年")]
    rows = [r for r in rows if r[1] and r[1] != "—"]
    body = f'''<main class="m2">
<header class="m2h"><p class="pf">{E(pref)}</p><h1>{E(name)}</h1><p class="sb">家と土地の値段・地価・くらしの数字</p></header>
<section class="mcs" aria-label="数字">{"".join(cards)}</section>
{f'<p class="vd">{E(verdict)}</p>' if verdict else ""}
<a class="go" href="{ikura}"><b>{E(name)}で、うちの家はいくら？</b><small>種類と広さから30秒で目安・名前は要りません</small><i>›</i></a>
<a class="go2" href="{ask}">売る前に、無料で聞いてみる<i>›</i></a>
<!-- 11/21 売り出し中の家を近くの街くらべより上に（関西と同じ） -->
<section class="sec yhs"><h2>{E(name)}で売り出し中の家</h2><div class="yh">{yrow}</div><p class="note">Yahoo!不動産の一覧が開きます（広告）</p></section>
<div id="itt"></div>
<section class="sec"><h2>実家・空き家・解体</h2><nav class="ls">
<a href="{sozoku}"><b>相続した家・古い家の相談</b><small>再建築不可・空き家も。無料</small><i>›</i></a>
{f'<a href="{kai}"><b>解体の補助金</b><small>いくら出るか・受付の状況</small><i>›</i></a>' if kai else ""}
<a href="/kaitai"><b>片付け・解体の費用</b><small>広さから30秒で目安</small><i>›</i></a>
<a href="{katamoji}"><b>片付け・遺品整理の無料見積り</b><small>家財の片付けだけでも大丈夫です</small><i>›</i></a>
</nav></section>
<section class="sec"><h2>くらしの数字</h2><dl class="tb">{"".join(f"<div><dt>{E(k)}<small>{E(n)}</small></dt><dd>{E(v)}</dd></div>" for k, v, n in rows)}</dl>
<details class="more"><summary>くわしく読む</summary>{"".join(f"<p>{E(x)}</p>" for x in para)}</details></section>
<section class="sec faq"><h2>よくある質問</h2>{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faq)}</section>
<footer class="src"><h2>出典</h2>{"".join(f"<p>{E(x)}</p>" for x in srcs)}</footer>
</main>'''
    if prod:
        keep = re.findall(r'<title>[\s\S]*?</title>|<meta (?:name="description"|property="og:[^"]+"|name="twitter:[^"]+"|name="theme-color")[^>]*>|<link rel="(?:canonical|icon|apple-touch-icon|manifest)"[^>]*>|<script type="application/ld\+json">[\s\S]*?</script>', h)
        head = "\n".join(keep)
        css = '<link rel="stylesheet" href="/shin/machi2.css?v=' + CSSV + '">'
    else:
        head = f'<title>{E(name)}の家と土地の値段（見本）</title><meta name="robots" content="noindex">'
        css = "<style>" + open(__file__.replace("machi2.py", "../site/shin/machi2.css"), encoding="utf-8").read() + "</style>"
    page = f'''<!doctype html><html lang="ja" data-m2="1"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{head}
<script>window.TN_P="/machi/{tid}";document.documentElement.dataset.k="m2";document.documentElement.classList.add("sk");try{{if(localStorage.getItem("usagi_theme")==="night")document.documentElement.classList.add("nt")}}catch(e){{}}</script>
<link rel="stylesheet" href="/shin/skin.css"><script src="/shin/skin.js" defer></script>
{css}</head><body>{body}</body></html>'''
    open(out, "w", encoding="utf-8").write(page)
    return len(cards)


def batch(src_dir, out_dir):
    """全部の街：src_dir/<id>.html → out_dir/<id>.html（本番の形）。読めないページは書かない（前のページのまま）"""
    import os
    os.makedirs(out_dir, exist_ok=True)
    ok = ng = 0
    for fn in sorted(os.listdir(src_dir)):
        if not re.match(r"[a-z]+-\d+\.html$", fn):
            continue
        try:
            r = main(os.path.join(src_dir, fn), os.path.join(out_dir, fn) + ".tmp", prod=True)
            if r == "skip":
                continue
            if r < 2:
                raise ValueError("cards " + str(r))
            os.replace(os.path.join(out_dir, fn) + ".tmp", os.path.join(out_dir, fn)); ok += 1
        except Exception as e:
            ng += 1; print("machi2: そのまま", fn, e)
            try:
                os.remove(os.path.join(out_dir, fn) + ".tmp")
            except OSError:
                pass
    print(f"machi2: 新しい形 {ok} 枚・前のまま {ng} 枚")


if __name__ == "__main__":
    if sys.argv[1] == "all":
        batch(sys.argv[2], sys.argv[3])
    else:
        print(main(sys.argv[1], sys.argv[2]))
