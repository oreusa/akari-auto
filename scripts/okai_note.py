"""11/5 オーナー「ノーブランドで安いのは当たり前、わざわざここで買う理由がない」「お前が最高のhpつくるなら好きにしろ」
→ くらべたおかいものリストのいちばん上に「いつもの物の値段帳」を入れる。
  ・名の知れたメーカー（scripts/tanka.py の BRAND）の物だけを、種類ごとに3つまで、送料込みの1個あたりで
  ・毎回の値段を data/note-history.json に残し、「いつもより安い／いつもどおり／いつもより高い」の札を付ける
  ・/okaimono?k=wipes のように種類を付けて開くと、その種類が開いた状態で出る（投稿から1つの答えへ飛ばす）
  ・日用品と関係ない「ほかのおすすめ」（旅行・お花など）は見せない
lifenote.py が site/okaimono.html を作ったあとに動かす。失敗しても元のページはそのまま。"""
import html
import json
import os
import re
import statistics
import urllib.parse
from datetime import datetime, timedelta, timezone

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JST = timezone(timedelta(hours=9))
E = html.escape
ORDER = ["wipes", "diaper", "detergent", "softener", "dish", "tissue", "tp", "water", "tea", "rice",
         "bodysoap", "shampoo", "trash", "mask", "battery", "coffee", "soda", "pasta", "dogfood", "catfood"]
SHORT = {"water": "水", "tea": "お茶", "coffee": "コーヒー", "detergent": "洗濯洗剤", "softener": "柔軟剤", "shampoo": "シャンプー",
         "bodysoap": "ボディソープ", "dish": "食器用洗剤", "battery": "乾電池", "rice": "お米", "soda": "炭酸水"}


def code(u):
    m = re.search(r"item\.rakuten\.co\.jp/([^/]+)/([^/?#]+)", u or "")
    return f"{m.group(1)}:{m.group(2)}" if m else ""


def afl(u):
    aid = os.environ.get("RAKUTEN_AFFILIATE_ID")
    if not aid:
        return u
    enc = urllib.parse.quote(u, safe="")
    return f"https://hb.afl.rakuten.co.jp/hgc/{aid}/?pc={enc}&m={enc}"


def load(p, d):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return d


def mark(hist):
    v = [hist[k] for k in sorted(hist)]
    if len(v) < 3:
        return "new", "値段を記録中"
    now, past = v[-1], v[:-1]
    avg = statistics.mean(past)
    if now < min(past):
        return "low", f"{len(v)}日でいちばん安い"
    if now < avg * 0.97:
        return "low", f"いつもより{round((1 - now / avg) * 100)}%安い"
    if now > avg * 1.03:
        return "hi", "いつもより高い"
    return "eq", "いつもどおり"


def main():
    page = os.path.join(R, "site", "okaimono.html")
    if not os.path.exists(page):
        print("okaimono.html が無い")
        return
    d = load(os.path.join(R, "data", "tanka.json"), {})
    hp = os.path.join(R, "data", "note-history.json")
    hist = load(hp, {})
    today = datetime.now(JST).strftime("%Y-%m-%d")
    cats = {c["key"]: c for c in d.get("cats", [])}
    tiles, panels, low = [], [], []
    for k in ORDER:
        c = cats.get(k)
        if not c:
            continue
        rows, seen = [], set()
        for it in c.get("top", []):
            b = it.get("bd")
            if not b or b in seen or not code(it.get("plain")):
                continue
            seen.add(b)
            rows.append(it)
            if len(rows) == 3:
                break
        if not rows:
            continue
        name = SHORT.get(k) or c["title"].split("（")[0]
        rr = ""
        for i, it in enumerate(rows):
            cd = code(it["plain"])
            h = hist.setdefault(cd, {})
            h[today] = it["per"]
            for old in sorted(h)[:-60]:
                del h[old]
            mk = mark(h)
            if mk[0] == "low":
                low.append((name, it, mk[1], k))
            url = it.get("url") or afl(it["plain"])
            im = it.get("img") or ""
            rr += (f'<a class="nb-nr{" b" if i == 0 else ""}" href="{E(url, quote=True)}" rel="sponsored noopener" target="_blank" data-k="値段帳｜{E(name)}｜{E(it["bd"])}">'
                   f'<span class="nb-ni">{f"<img src={chr(34)}{E(im, quote=True)}{chr(34)} alt={chr(34)}{chr(34)} loading={chr(34)}lazy{chr(34)} referrerpolicy={chr(34)}no-referrer{chr(34)}>" if im else ""}</span>'
                   f'<span class="nb-nt"><b>{E(it["bd"])}</b><small>{E(str(it.get("amt") or ""))}・レビュー{int(it.get("rc") or 0):,}件</small>'
                   f'<i class="nb-nm {mk[0]}">{E(mk[1])}</i></span>'
                   f'<span class="nb-np"><em>{it["per"]:g}<small>円</small></em><small>{E(c["unit"])}あたり</small><u>楽天で見る ›</u></span></a>')
        tiles.append(f'<button type="button" class="ntl" data-k="{k}"><b>{E(name)}</b><small>{E(rows[0]["bd"])} {rows[0]["per"]:g}円</small></button>')
        panels.append(f'<div class="npn" id="n-{k}" data-k="{k}"><p class="nb-nh">{E(name)}<small>名の知れたメーカー{len(rows)}つ・送料込み・{E(c["unit"])}あたり</small></p>{rr}'
                      f'<p class="nb-nf">楽天の{int(c.get("seen") or 0):,}件から、毎回しらべています</p></div>')
    if not panels:
        print("値段帳：名の知れた物が無いので入れない")
        return
    json.dump(hist, open(hp, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    lowh = ""
    if low:
        lowh = ('<p class="nhd">今日は、いつもより安い</p><div class="nlo">' + "".join(
            f'<button type="button" class="nlb" data-k="{k}"><b>{E(n)}・{E(it["bd"])}</b><small>{E(m)}</small></button>' for n, it, m, k in low[:4]) + '</div>')
    # 買う日の予定（data/sales.json。楽天は入口の箱と同じ日程、Yahoo!・Amazon は綾香様の声と公式で確かめた物だけ note なしで出す）
    sales = load(os.path.join(R, "data", "sales.json"), {}).get("sales", [])
    now = datetime.now(JST).replace(tzinfo=None)
    wk = "月火水木金土日"
    cal = ""
    for x in sales:
        try:
            st, en = datetime.fromisoformat(x["start"]), datetime.fromisoformat(x["end"])
        except Exception:
            continue
        if en < now:
            continue
        if st <= now:
            e2 = en + timedelta(minutes=1)
            cal += f'<li class="now"><span>開催中</span><b>{E(x["name"])}</b><small>{e2.month}/{e2.day}（{wk[e2.weekday()]}）{e2:%H:%M}まで</small></li>'
        else:
            cal += f'<li><span>{st.month}/{st.day}</span><b>{E(x["name"])}</b><small>{"見込み" if x.get("note") else f"{st:%H:%M}から"}</small></li>'
    # 5と0の日（楽天カードでポイントが増える日）を、次の1回だけ
    for i in range(0, 11):
        dd = (now + timedelta(days=i)).date()
        if dd.day % 5 == 0:
            cal += f'<li><span>{dd.month}/{dd.day}</span><b>5と0のつく日</b><small>楽天カードでポイントが増える日</small></li>'
            break
    calh = f'<p class="nhd">買う日の予定</p><ul class="ncal">{cal}</ul>' if cal else ""
    block = (
        '<section class="nbk" id="note" aria-label="いつもの物の値段帳">'
        '<h2 class="nttl">いつもの日用品、<br>今日いちばん安いのは？</h2>'
        '<p class="nld">パンパース・アタックなど<b>いつものメーカー</b>だけで、<br>送料込みの1個あたりを毎日くらべています</p>'
        '<div class="nwy"><div><b>いつもの物だけ</b>知らない安物は<br>入れません</div><div><b>買い時がわかる</b>毎日の値段を<br>記録しています</div>'
        '<div><b>送料込み</b>1枚・1Lあたりで<br>そろえて比較</div></div>'
        + lowh +
        '<p class="nhd">いつもの物をえらぶ</p><div class="ntls" role="tablist">' + "".join(tiles) + '</div>'
        + "".join(panels) + calh +
        '<p class="nhd nask">ほかの物は、うさぎに聞く</p></section>')
    css = ("<style>"
           ".nbk{margin:4px 0 8px}.nttl{font:600 22px/1.45 'Shippori Mincho',serif;text-align:center;margin:6px 0;letter-spacing:.04em;color:#1F1B18}"
           ".nld{text-align:center;color:#6E655D;font-size:13px;line-height:1.7;margin:0 0 16px}.nld b{color:#1F1B18}"
           ".nwy{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin:0 0 20px}.nwy div{border:1px solid #E6E2DE;border-radius:12px;padding:10px 4px;text-align:center;font-size:11px;line-height:1.5;color:#6E655D;background:#fff}.nwy b{display:block;color:#1F1B18;font-size:12.5px;margin-bottom:2px}"
           ".nhd{font:700 13px/1 'Zen Kaku Gothic New',sans-serif;letter-spacing:.08em;margin:0 0 10px;color:#1F1B18}"
           ".ntls{display:flex;gap:8px;overflow-x:auto;padding:2px 2px 12px;scrollbar-width:none;-webkit-overflow-scrolling:touch}.ntls::-webkit-scrollbar{display:none}"
           ".ntl{flex:none;border:1px solid #D6D1CC;background:#fff;border-radius:14px;padding:10px 14px;text-align:left;cursor:pointer;font-family:inherit;color:#1F1B18;min-height:52px}"
           ".ntl b{display:block;font-size:14px;line-height:1.3}.ntl small{font-size:11px;color:#6E655D}.ntl.on{background:#1F1B18;border-color:#1F1B18;color:#fff}.ntl.on small{color:#D8D2CC}"
           ".npn{display:none;border:1px solid #E6E2DE;border-radius:16px;padding:14px 14px 8px;margin-bottom:22px;background:#fff;scroll-margin-top:70px}.npn.on{display:block}"
           ".nb-nh{margin:0 0 4px;font:600 18px/1.4 'Shippori Mincho',serif;color:#1F1B18}.nb-nh small{display:block;font:400 11px 'Zen Kaku Gothic New',sans-serif;color:#6E655D}"
           ".nbk a.nb-nr{display:grid!important;grid-template-columns:56px minmax(0,1fr) auto;gap:10px;align-items:center;padding:12px 0;border-top:1px solid #E6E2DE;color:inherit;text-decoration:none}"
           ".nb-ni{width:56px;height:56px;border-radius:10px;background:#F4F1EE;overflow:hidden;display:block}.nb-ni img{width:100%;height:100%;object-fit:cover;display:block}"
           ".nb-nt b{display:block;font-size:15px;color:#1F1B18}.nb-nt small{display:block;font-size:11px;color:#6E655D;line-height:1.5}"
           ".nb-nm{display:inline-block;font-style:normal;font-size:11px;font-weight:700;border-radius:99px;padding:1px 8px;margin-top:3px;background:#F1EEEA;color:#6E655D}.nb-nm.low{background:#E4F2EA;color:#2F7D57}.nb-nm.hi{background:#F7E9E5;color:#B5523B}"
           ".nbk .nb-np{text-align:right;white-space:nowrap}.nbk .nb-nt{min-width:0}.nb-np em{display:block;font:500 22px/1.1 Jost,sans-serif;font-style:normal;color:#1F1B18}.nb-np em small{font-size:11px;margin-left:1px}.nb-np>small{display:block;font-size:10.5px;color:#6E655D}"
           ".nb-np u{display:inline-block;margin-top:4px;text-decoration:none;font-size:11px;font-weight:700;color:#BF0000}.nb-nr.b .nb-np em{color:#B5523B}"
           ".nb-nf{font-size:11px;color:#6E655D;text-align:right;margin:4px 0 0}"
           ".nlo{display:flex;flex-direction:column;gap:6px;margin:0 0 20px}.nlb{display:flex;justify-content:space-between;gap:8px;border:1px solid #CFE6D8;background:#F3FAF6;border-radius:12px;padding:11px 14px;font-family:inherit;cursor:pointer;text-align:left}.nlb b{font-size:13.5px;color:#1F1B18}.nlb small{font-size:12px;font-weight:700;color:#2F7D57;white-space:nowrap}"
           ".ncal{list-style:none;margin:0 0 22px;padding:0;border:1px solid #E6E2DE;border-radius:16px;background:#fff}.ncal li{display:grid;grid-template-columns:56px 1fr;gap:2px 8px;padding:11px 14px;border-top:1px solid #E6E2DE}.ncal li:first-child{border-top:0}"
           ".ncal span{grid-row:span 2;font:500 13px/1.6 Jost,sans-serif;color:#6E655D}.ncal b{font-size:14px;color:#1F1B18}.ncal small{font-size:11px;color:#6E655D}.ncal li.now span{color:#B5523B;font:700 12px/1.6 'Zen Kaku Gothic New',sans-serif}"
           ".nask{text-align:center;margin:0 0 8px}"
           ".kgh,.kgh~details.kpr{display:none!important}"
           "html.dark .nwy div,html.dark .npn,html.dark .ntl,html.dark .ncal{background:transparent}"
           "</style>")
    js = ("<script>(function(){var T=[].slice.call(document.querySelectorAll('.ntl')),P=[].slice.call(document.querySelectorAll('.npn'));"
          "function op(k,sc){var hit=0;T.forEach(function(t){var on=t.dataset.k===k;t.classList.toggle('on',on);t.setAttribute('aria-selected',on);if(on){hit=1;t.scrollIntoView({block:'nearest',inline:'center'});}});"
          "P.forEach(function(p){p.classList.toggle('on',p.dataset.k===k)});if(sc&&hit){var p=document.getElementById('n-'+k);if(p)p.scrollIntoView({block:'start',behavior:'smooth'});}return hit;}"
          "T.forEach(function(t){t.onclick=function(){op(t.dataset.k,0);try{history.replaceState(null,'','?k='+t.dataset.k)}catch(e){}}});"
          "document.querySelectorAll('.nlb').forEach(function(b){b.onclick=function(){op(b.dataset.k,1)}});"
          "var q='';try{q=new URLSearchParams(location.search).get('k')||''}catch(e){}"
          "if(!(q&&op(q,1))&&T[0])op(T[0].dataset.k,0);})();</script>")
    s = open(page, encoding="utf-8").read()
    if 'id="note"' in s:
        return
    i = s.find('<section class="kq"')
    if i < 0:
        print("聞く欄が見つからない")
        return
    s = s[:i] + block + s[i:]
    s = s.replace("</head>", css + "</head>", 1)
    s = s.replace("</body>", js + "</body>", 1)
    open(page, "w", encoding="utf-8").write(s)
    print("値段帳：", len(panels), "種類・安い", len(low))


if __name__ == "__main__":
    main()
