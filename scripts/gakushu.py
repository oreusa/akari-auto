"""関東の学習の台帳（11/11 オーナー「直して欲しいんじゃない。学習して成長し考えることが出来るシステムを」）。
ばらばらだった帳面（成長の帳面・当たり帳・GPTの回の記録・ページの数）を1枚にまとめ、項目ごとに
①機械が測った数字 ②合格の線 ③答え（当たり・外れ・未確認）④機械が出す指令 を毎朝作る。
- notes/gakushu.md  1枚（燈の夜の回は、これを最初に読む。ほかの帳面は、指令に書いてある時だけ開く）
- data/shirei.json  きょうの指令（to＝燈の夜・投稿・リール・月）
- data/manabi.json  学びの帳面（答えが変わった日に機械が1行足す。同じ外れをくり返さない）
数字が取れない項目は「未確認」。計画を実績と書かない。使い方：python3 scripts/gakushu.py [YYYY-MM-DD]"""
import glob, json, os, re, statistics, sys
from datetime import date, timedelta
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *p: os.path.join(ROOT, *p)
today = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
def load(p, d):
    try: return json.load(open(p, encoding="utf-8"))
    except Exception: return d
sei = load(P("data", "seichou.json"), {}); prev = load(P("data", "gakushu.json"), {})
manabi = load(P("data", "manabi.json"), {"about": "学びの帳面。機械が、答えの変わった日に1行足す。消さない", "rows": []})
d7 = (today - timedelta(days=8)).isoformat(); d14 = (today - timedelta(days=15)).isoformat()
posts = []
for f in sorted(glob.glob(P("data", "metrics", "*.json"))):
    day = os.path.basename(f)[:10]
    if day > d14:
        for p in load(f, {}).get("posts", []):
            m = p.get("metrics") or {}
            posts.append({"day": day, "svc": p.get("service"), "slot": p.get("slot", ""), "kind": p.get("kind", ""), "v": int(m.get("views", m.get("impressions")) or 0), "first": p.get("first", "")})
now = [p for p in posts if p["day"] > d7]; old = [p for p in posts if p["day"] <= d7]
med = lambda xs: int(statistics.median(xs)) if xs else 0
items, orders = [], []
def item(id, name, num, line, ans, why): items.append({"id": id, "name": name, "num": num, "line": line, "ans": ans, "why": why})
def order(to, id, text, why, kind="作る"): orders.append({"to": to, "item": id, "order": text, "why": why, "kind": kind})

# 1 HP
n, pv = sei.get("now", {}), sei.get("prev", {})
item("hp", "HP（関東）", f"見られた {n.get('views', '未確認')}（前の7日 {pv.get('views', '未確認')}）・相談や査定へ {n.get('ask', 0)}・買い物や宿 {n.get('buy', 0)}", "見られた 週1500", "当たり" if n.get("views", 0) >= 1500 else "外れ", sei.get("weak", ""))
if sei.get("next"): order("燈の夜", "hp", sei["next"], "いちばん弱い所：" + sei.get("weak", ""))

# 2 投稿：枠（時刻）ごと・型ごとの中央値。強い枠へ寄せ、弱い枠・型を止める
for svc, name in (("threads", "Threads"), ("twitter", "X")):
    cur = [p for p in now if p["svc"] == svc and p["kind"] == "通常"]
    allm = med([p["v"] for p in cur]); oldm = med([p["v"] for p in old if p["svc"] == svc and p["kind"] == "通常"])
    slots = {}
    for p in cur: slots.setdefault(p["slot"], []).append(p["v"])
    sm = sorted(((s, med(v), len(v)) for s, v in slots.items() if len(v) >= 3), key=lambda x: -x[1])
    item("post-" + svc, f"投稿（{name}）", f"中央値 {allm}（前の7日 {oldm}）・強い枠 " + ("・".join(f"{s} {m}" for s, m, _ in sm[:3]) or "未確認") + "・弱い枠 " + ("・".join(f"{s} {m}" for s, m, _ in sm[-2:]) or "未確認"), "中央値が前の7日より上", "当たり" if allm > oldm else ("計測中" if not oldm else "外れ"), "通常の投稿だけ")
    if len(sm) >= 4 and sm[-1][1] * 3 < sm[0][1]:
        order("投稿", "post-" + svc, f"{name} の {sm[-1][0]} の枠（中央値 {sm[-1][1]}）をやめ、その1本を {sm[0][0]} の前後30分（中央値 {sm[0][1]}）に移す。本数は増やさない", "弱い枠は強い枠の3分の1より下")
kinds = {}
for p in now:
    if p["svc"] in ("threads", "twitter"): kinds.setdefault(p["kind"], []).append(p["v"])
base = med(kinds.get("通常", []))
for k, v in kinds.items():
    if k not in ("通常", "4コマ") and len(v) >= 5 and med(v) * 3 < base:
        order("投稿", "post-kind", f"「{k}」の投稿（中央値 {med(v)}、通常は {base}）は、Threads と X では週2本までに減らし、空いた枠を通常の当たりの型に回す", "通常の3分の1より下が7日続いた")
# 4コマ（雫＝GPTの絵）。11/12 owner「4コマなぁ、gpt使って欲しいんよなぁ、毎月お金かかってるし」→ やめない。見られる形を機械が探す
_k4 = {sv: [p["v"] for p in now if p["svc"] == sv and p["kind"] == "4コマ"] for sv in ("twitter", "threads", "instagram")}
_n4 = {sv: [p["v"] for p in now if p["svc"] == sv and p["kind"] == "通常"] for sv in ("twitter", "threads")}
if any(_k4.values()):
    _okx = bool(_k4["twitter"]) and med(_k4["twitter"]) >= med(_n4["twitter"]); _okt = bool(_k4["threads"]) and med(_k4["threads"]) >= med(_n4["threads"])
    item("koma4", "4コマ（雫の絵）", f"X {med(_k4['twitter'])}（ふつうの投稿 {med(_n4['twitter'])}）・Threads {med(_k4['threads'])}（ふつう {med(_n4['threads'])}）・インスタ {med(_k4['instagram'])}", "X か Threads で、ふつうの投稿の中央値より上", "当たり" if (_okx or _okt) else "外れ", "GPT（雫）の毎日の仕事。見られる形にする")
    _best = sorted([p for p in now if p["kind"] == "4コマ" and p["svc"] in ("twitter", "threads")], key=lambda x: -x["v"])[:1]
    _hit = sorted([p for p in now if p["kind"] == "通常" and p["svc"] in ("twitter", "threads")], key=lambda x: -x["v"])[:1]
    if not _okt and _hit: order("燈の夜", "koma4", f"4コマは続ける（オーナー 11/12）。Threads で 4コマ {med(_k4['threads'])}・ふつう {med(_n4['threads'])}。あすの4コマの題材を、この7日でいちばん見られた投稿「{_hit[0]['first'][:26]}」（{_hit[0]['v']}）と同じ種類（食べ物の催し・新しい店など）にし、投稿文の1行目をその投稿と同じ「日付、場所で名前」の形にする" + (f"。4コマでいちばん見られた回は「{_best[0]['first'][:22]}」（{_best[0]['v']}）" if _best else ""), "4コマが、ふつうの投稿より見られていない")
    if _okx: order("燈の夜", "koma4", f"4コマは X で当たり（{med(_k4['twitter'])}、ふつう {med(_n4['twitter'])}）。X の4コマは今の形のまま。出す時刻を X の強い枠に合わせる", "X ではふつうより見られている")
top = sorted([p for p in now if p["svc"] in ("threads", "twitter")], key=lambda x: -x["v"])[:3]
if top and top[0]["v"] >= max(300, base * 3):
    order("投稿", "post-hit", "当たった3本の形（1行目の作り・題材）を、あす別の場所・別の日付で1本ずつ作る：" + "／".join(f"{p['first'][:28]}（{p['v']}）" for p in top), "中央値の3倍以上")

# 3 投稿からHPへ（来た元の印）
item("come", "投稿からHPへ", f"来た {n.get('come', 0)}（前 {pv.get('come', 0)}）・来て押した {n.get('post', 0)}（前 {pv.get('post', 0)}）", "来た 週50", "当たり" if n.get("come", 0) >= 50 else "外れ", "2本目の行き先")
sl = sei.get("slots", [])
if sl: order("投稿", "come", f"HPに一番来た枠「{sl[0]['name']}」（{sl[0]['n']}人）の2本目の行き先と同じ型のページへ、ほかの枠の2本目も向ける", "来た元の数")
else: order("投稿", "come", "どの投稿も、2本目にその話の答えが出るHPのページ（街・費用・地図）を1つ付け、来た元の印（x時刻・t時刻）を付ける", "来た数がまだ0")

# 4 インスタ（4コマ・リール）
ig = {}
for p in now:
    if p["svc"] == "instagram": ig.setdefault(p["kind"], []).append(p["v"])
item("ig", "インスタ", "・".join(f"{k} {len(v)}本 中央値{med(v)}" for k, v in ig.items()) or "未確認", "リールの中央値 100", "当たり" if med(ig.get("おでかけリール", [])) >= 100 else ("未確認" if not ig else "外れ"), "4コマとリールをくらべる")
if ig.get("4コマ") and ig.get("おでかけリール") and med(ig["4コマ"]) * 5 < med(ig["おでかけリール"]):
    order("リール", "ig", f"インスタの4コマ（中央値 {med(ig['4コマ'])}）は続ける（オーナー 11/12「GPTを使ってほしい」）。インスタで増やすのは、おでかけリール（中央値 {med(ig['おでかけリール'])}）の方（1日2本）。雫の絵（うさぎちゃん）をおでかけリールの表紙に使う", "リールが4コマの5倍以上")

# 5 担当（雫・汐・凪）— notes/gpt-runs.md の ○× を機械が数える
runs = [l for l in open(P("notes", "gpt-runs.md"), encoding="utf-8").read().splitlines() if re.match(r"- 20\d\d-\d\d-\d\d", l) and l[2:12] > d7] if os.path.exists(P("notes", "gpt-runs.md")) else []
if runs:
    miss = {}
    for l in runs:
        for who, pat in (("雫", r"雫6:40([○×？])"), ("汐", r"汐7:45([○×？])"), ("凪", r"20:20([○×？])")):
            m = re.search(pat, l)
            if not m or m.group(1) != "○": miss[who] = miss.get(who, 0) + 1
    item("gpt", "担当（雫・汐・凪）", f"{len(runs)}日のうち出なかった日：" + ("・".join(f"{w} {c}日" for w, c in miss.items()) or "なし"), "出なかった日 0", "当たり" if not miss else "外れ", "notes/gpt-runs.md")
    for w, c in miss.items():
        if c >= 2: order("月", "gpt", f"{w}が{c}日出していない。指示書を半分の長さにして、やる事を1つに絞る。次の週も出なければ、その仕事を機械に移す", "出ない指示書は長すぎるか難しすぎる")
else:
    item("gpt", "担当（雫・汐・凪）", "未確認", "出なかった日 0", "未確認", "notes/gpt-runs.md に行が無い")
    order("燈の夜", "gpt", "notes/gpt-runs.md に、きょうの 雫6:40・汐7:45・凪20:20 の ○× を1行で書く（機械が数える）", "担当の出来が未確認")

# 6 お金（買い物・宿が押された数は機械。成果は data/seika.json に汐の月曜の写しを入れる）
sk = load(P("data", "seika.json"), {}).get("rows", [])
last = sk[-1] if sk else None
# 11/12 成果は、燈が毎朝 notes/sales-board.md に書く「M/D 朝：成果N…楽天クリックN」の行を機械が読む（人が写す手間を無くす）
_sb = []
try:
    for l_ in open(P("notes", "sales-board.md"), encoding="utf-8"):
        m_ = re.match(r"- (\d+)/(\d+) 朝：成果(\d+)", l_)
        if m_:
            dd = date(today.year, int(m_.group(1)), int(m_.group(2)))
            if dd > today: dd = date(today.year - 1, dd.month, dd.day)
            c_ = re.search(r"楽天クリック(\d+)", l_)
            _sb.append((dd.isoformat(), int(m_.group(3)), int(c_.group(1)) if c_ else 0))
except Exception: pass
_sb7 = {d_: (s_, c_) for d_, s_, c_ in _sb if d_ > d7}
if _sb7:
    _s = sum(v[0] for v in _sb7.values()); _c = sum(v[1] for v in _sb7.values())
    item("money", "買い物・宿・ROOM", f"HPで押された {n.get('buy', 0)}（前 {pv.get('buy', 0)}）・楽天で押された {_c}・成果 {_s}件（{len(_sb7)}日ぶん・燈の朝の写し）・ROOMで売れた {last.get('room_uri', '未確認') if last else '未確認'}", "成果 週1件", "当たり" if _s > 0 else "外れ", "クリックは売上ではない。成果は楽天の画面の数字だけ")
    if _s == 0 and (n.get("buy", 0) >= 30 or _c >= 100): order("燈の夜", "money", f"楽天で {_c}回（機械がリンクを確かめた分も入る）・HPで {n.get('buy', 0)}回 押されたのに成果0。押された先の上位3つを notes/sales-board.md と data/page-stats.json で見て、買われやすい物（毎日使う消耗品・3,000円まで・レビュー4.3以上・送料込み）に1つ差し替える。セールの入口（エントリー）はそのまま", "押されているのに買われていない＝物が合っていない")
    elif _s == 0: order("燈の夜", "money", "楽天で押された数が週100に届かない。おかいものの入口を、見られた数が多いおでかけページの下に1つ置く（そのおでかけに持って行く物）", "押される数がまだ少ない")
else:
    item("money", "買い物・宿・ROOM", f"押された {n.get('buy', 0)}（前 {pv.get('buy', 0)}）・成果 未確認", "成果 週1件", "未確認", "notes/sales-board.md に「M/D 朝：成果N」の行が無い")
    order("燈の夜", "money", "notes/sales-board.md に、きょうの行を「- M/D 朝：成果N・楽天クリックN」の形で書く（機械が読む）", "成果が未確認のまま", "数字")

# 6b 売却の受け皿（ASP の案件。notes/daichou.md の表を機械が読む）
_pr = []
if os.path.exists(P("notes", "daichou.md")):
    for _l in open(P("notes", "daichou.md"), encoding="utf-8"):
        _c = [x.strip() for x in _l.strip().strip("|").split("|")]
        if _l.startswith("| A8") or _l.startswith("| VC"):
            if len(_c) >= 5: _pr.append((_c[1][:24], _c[3], _c[4]))
_wait = [p for p in _pr if "審査中" in p[1]]; _ok = [p for p in _pr if "提携済み" in p[1] or "承認" in p[1]]; _ng = [p for p in _pr if "見送り" in p[1] or "否" in p[1]]
item("asp", "売却・査定の案件（ASP）", f"提携済み {len(_ok)}・審査中 {len(_wait)}（" + "・".join(f"{n} {r}" for n, _, r in _wait[:4]) + f"）・見送り {len(_ng)}", "売りたい人の送り先が1つ以上 提携済み", "当たり" if any("査定" in n or "売却" in n or "仲介" in n for n, st, _ in _ok if "使わない" not in st) else "外れ", "セレスは 11/11 見送り。代わりは審査中の案件")
if _wait: order("月", "asp", "月曜の汐の写しで、審査中の案件（" + "・".join(n for n, _, _ in _wait[:4]) + "）の状態を台帳 notes/daichou.md に入れる。提携済みになった物は、その日のうちに /uru の「売りたい」に付け、押された数を数える。2週たっても審査中の物は、汐にもう1件ずつ申請を足してもらう", "売りたい人の送り先がまだ無い")

# 7b 市区ごとの解体補助ページ（11/11〜。data/page-stats.json の「表示：市の解体補助 <市区>」）
_days = load(P("data", "page-stats.json"), {}).get("days", {}); _city = {}
for _d, _v in _days.items():
    if _d <= d7: continue
    for _src, _it in (_v.get("click") or {}).items():
        for _k, _c in _it.items():
            _m = re.search(r"表示：市の解体補助 ([^（｜]+)", _k)
            if _m: _city[_m.group(1)] = _city.get(_m.group(1), 0) + _c
_n = len(glob.glob(P("site", "kaitai-*.html"))); _tot = sum(_city.values())
item("city", "市区ごとの解体補助ページ", f"{_n}市区・見られた {_tot}・上位 " + ("・".join(f"{c} {v}" for c, v in sorted(_city.items(), key=lambda x: -x[1])[:3]) or "まだ無し"), "見られた 週20", "当たり" if _tot >= 20 else ("計測中" if not _tot else "外れ"), "検索から来る入口。市区を足すほど入口が増える")
if _tot >= 20: order("月", "city", "関東の市区を1日2つ足す（凪の帳面の順に、公式ページで確かめて usagi tools/kaitai/kanto_hojo.tsv と city_life.py の SLUG へ）", "当たり：入口が効いている")
else: order("月", "city", "関東の市区を1日1つ足す（公式ページで確かめた行だけ）。7日たっても見られた数が0なら、題を「◯◯市 解体 補助金 2026 いくら」の形に変える", "まだ数が無い")

# 7 反響
def rung(now, ladder): return next((x for x in ladder if x > now), ladder[-1])
hist = prev.get("hist", {})
sent = n.get("sent", 0); _so = [v for d, v in hist.get("lead_sent", []) if d <= d7]
item("lead", "相談（反響）", f"見られた {n.get('views', 0)}・相談や査定へ押した {n.get('ask', 0)}・申し込みを開いた {n.get('open', 0)}・送信 {sent}", f"次の段：送信 {rung(sent, [1, 3, 10])}件（その先 月10件）", "当たり" if sent >= 1 and sent > (_so[-1] if _so else 0) else "外れ", "関東も問い合わせはオーナーへ")
# いちばん人が落ちている段を機械が選ぶ（お金にいちばん近いので、月あての1番）
_st = [("見られた", n.get("views", 0)), ("申し込みを開いた", n.get("open", 0)), ("送信", sent)]
_drop = None
for (x, a_), (y, b_) in zip(_st, _st[1:]):
    if a_ >= 10 and (_drop is None or b_ / a_ < _drop[4]): _drop = (x, a_, y, b_, b_ / a_)
_FIX = {"申し込みを開いた": "見られた数が多いページ（成長の帳面の上位3つ）の最初の画面の中に、そのページの悩みに合わせた「相談する（無料）」への道を1つ置く。「相談や査定へ押した」人が外の査定サイトだけに流れていないか、押された先をくらべる",
        "送信": "申し込みページの最初の画面を「選ぶだけの質問1つ」から始める（名前・電話は最後）。スマホ幅で、開く→送信の手前までを通しで確かめる"}
if _drop: order("月", "lead", f"「{_drop[0]}」{_drop[1]} →「{_drop[2]}」{_drop[3]}（{_drop[4] * 100:.1f}%）が、いちばん人が落ちている段。" + _FIX[_drop[2]] + "。関西と同じ形に", "お金にいちばん近い段")

pa = {i["id"]: i for i in prev.get("items", [])}
for i in items:
    o = pa.get(i["id"])
    if o and o["ans"] != i["ans"] and i["ans"] not in ("未確認", "計測中"):
        manabi["rows"].append({"day": today.isoformat(), "item": i["name"], "from": o["ans"], "to": i["ans"], "num": i["num"], "did": [x["order"] for x in prev.get("orders", []) if x["item"] == i["id"]][:2]})
# 数字の歩み（30日）と、やった手の答え合わせ（data/yatta.json に回が {day, item, what} を足す → 7日後に機械が答えを付ける）
VAL = {"hp": n.get("views"), "come": n.get("come"), "money": n.get("buy"), "lead": sent * 100 + n.get("open", 0), "city": _tot, "lead_sent": sent}
for it in items:
    if it["id"].startswith("post-") and it["id"] in ("post-threads", "post-twitter"):
        m_ = re.search(r"中央値 (\d+)", it["num"]); VAL[it["id"]] = int(m_.group(1)) if m_ else None
    if it["id"] == "ig":
        m_ = re.findall(r"中央値(\d+)", it["num"]); VAL["ig"] = max(map(int, m_)) if m_ else None
for k, v in VAL.items():
    if v is not None:
        h = [x for x in hist.setdefault(k, []) if x[0] != today.isoformat()]; h.append([today.isoformat(), v]); hist[k] = h[-30:]
yatta = load(P("data", "yatta.json"), {"about": "やった手の帳面。回が、指令をやったら {day, item, what} を1行足す（item は台帳の項目の id：hp・post-threads・post-twitter・come・ig・money・city・lead）。before・after・result は機械が入れる", "rows": []})
name_of = {i["id"]: i["name"] for i in items}
for y in yatta["rows"]:
    if "before" not in y:
        xs = [v for d, v in hist.get(y.get("item"), []) if d <= y.get("day", "")]
        y["before"] = xs[-1] if xs else VAL.get(y.get("item"))
    if "result" not in y and y.get("day", "9") <= (today - timedelta(days=7)).isoformat() and VAL.get(y.get("item")) is not None and y.get("before") is not None:
        y["after"] = VAL[y["item"]]
        y["result"] = "効いた" if y["after"] >= y["before"] * 1.2 and y["after"] - y["before"] >= 1 else "効かなかった"
        manabi["rows"].append({"day": today.isoformat(), "item": name_of.get(y["item"], y["item"]), "id": y["item"], "kind": "手の答え", "what": y["what"], "before": y["before"], "after": y["after"], "result": y["result"]})
ng, ok = {}, {}
for m in manabi["rows"]:
    if m.get("kind") == "手の答え": (ok if m["result"] == "効いた" else ng).setdefault(m["id"], []).append(m["what"])
# 11/12 owner「なんでそれが抜けてるのか理解できない。大問題だろ」：関東の街ページ329枚に申し込みへの道が無かった（見られた1195→申し込み0）。人の目ではなく、機械が毎日「家のページなのに申し込みへ行けないページ」を数える
def _michi(root):
    import re as _re
    bad = []
    for d, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith(".html"): continue
            rel = os.path.relpath(os.path.join(d, f), root)
            if not _re.match(r"(machi/|jikka/[^/]+\.html|kaitai|ranking|chika|uru|fudosan-list)", rel) or rel == "jikka/index.html": continue
            s = open(os.path.join(d, f), encoding="utf-8", errors="ignore").read()
            if 'http-equiv="refresh"' in s: continue
            if "moushikomi" not in _re.sub(r"<nav.*?</nav>", "", s, flags=_re.S): bad.append(rel)
    return sorted(bad)
_bad = _michi(os.path.join(ROOT, "site"))
item("michi", "申し込みへの道", f"家のページで道が無い {len(_bad)}枚" + (f"（例 {_bad[0]}）" if _bad else ""), "合格の線：0枚", "当たり" if not _bad else "外れ", "家・土地のページは、どれも申し込みへ1回で行ける事")
if _bad: order("月", "michi", f"申し込みへの道が無い家のページが {len(_bad)}枚（{'・'.join(_bad[:3])}）。そのページを作る機械に、街の名前入りの「いくらで売れるか無料で聞く」を足す", "見られても反響にならない")
PRI = ["lead", "michi", "come", "city", "hp", "post-threads", "post-twitter", "post-kind", "post-hit", "koma4", "ig", "money", "asp", "gpt"]
_old = {(o["to"], o["item"], o["order"][:24]): o.get("days", 1) for o in prev.get("orders", [])}
for o in orders:
    if any(w in o["order"] for w in ("data/seika.json", "gpt-runs.md", "台帳 notes/daichou.md")): o["kind"] = "数字"
    d = _old.get((o["to"], o["item"], o["order"][:24]))
    o["days"] = (d if prev.get("day") == today.isoformat() else d + 1) if d else 1
    _w = [y["what"] for y in yatta["rows"] if "result" not in y and y.get("item") == o["item"]]
    if _w: o["wait"] = _w[-3:]
    if ng.get(o["item"]): o["ng"] = ng[o["item"]][-3:]
    if ok.get(o["item"]): o["ok"] = ok[o["item"]][-3:]
orders.sort(key=lambda o: (o["kind"] != "作る", PRI.index(o["item"]) if o["item"] in PRI else 99))
for to in ("燈の夜", "月"):
    _c = [o for o in orders if o["to"] == to and o["kind"] == "作る"]
    f_ = next((o for o in _c if len(o.get("wait", [])) < 2), _c[0] if _c else None)
    if f_: f_["first"] = True
def line(o):
    t = ("【きょうの1つ】" if o.get("first") else ("【数字を入れる】" if o["kind"] == "数字" else "")) + o["order"] + f"（理由：{o['why']}）"
    if o["days"] >= 3: t += f" ！{o['days']}日つづけて出ている＝まだやられていない"
    if o.get("wait"): t += "／答え待ちの手（同じ所を重ねて変えない。足りない所だけ足す）：" + "・".join(o["wait"])
    if o.get("ng"): t += "／前に効かなかった手（くり返さない）：" + "・".join(o["ng"])
    if o.get("ok"): t += "／前に効いた手（同じ型を増やす）：" + "・".join(o["ok"])
    return "- " + t
def mline(m):
    if m.get("kind") == "手の答え": return f"- {m['day']} {m['item']}：やった手「{m['what']}」→ {m['result']}（{m['before']}→{m['after']}）"
    return f"- {m['day']} {m['item']}：{m['from']}→{m['to']}（{m['num']}）。その前に出ていた指令：{'／'.join(m['did']) or '記録なし'}"
MARK = {"当たり": "◎", "外れ": "×", "未確認": "？", "計測中": "…"}
L = [f"# 関東の学習の台帳（{today.isoformat()} 朝）", "", "機械が毎朝作ります。燈の夜の回は、これを最初に読み、自分あての指令をそのままやります。数字が取れない物は「未確認」。", "",
     "| | 項目 | 機械が測った数字 | 合格の線 | 答え |", "|---|---|---|---|---|"]
L += [f"| {MARK.get(i['ans'], '')} | {i['name']} | {i['num']} | {i['line']} | {i['ans']} |" for i in items]
L += ["", "## きょうの指令", ""]
for to in ("燈の夜", "投稿", "リール", "月"):
    xs = [o for o in orders if o["to"] == to]
    if xs: L += [f"### {to}"] + [line(o) for o in xs] + [""]
_wait_y = [y for y in yatta["rows"] if "result" not in y]
L += ["## 答え待ちの手（やってから7日で、機械が答えを付ける）", ""] + ([f"- {y['day']} {name_of.get(y['item'], y['item'])}：{y['what']}（やる前 {y.get('before')}）" for y in _wait_y] or ["- ありません（指令をやった回が data/yatta.json に1行足します）"]) + [""]
L += ["## 学び（手の答え・答えが変わった日）", ""] + ([mline(m) for m in manabi["rows"][-12:]] or ["- まだありません"]) + [""]
open(P("notes", "gakushu.md"), "w", encoding="utf-8").write("\n".join(L))
json.dump(yatta, open(P("data", "yatta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"day": today.isoformat(), "items": items, "orders": orders, "sum": {"sent": sent, "seika": (_s if _sb7 else None)}, "hist": hist}, open(P("data", "gakushu.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"day": today.isoformat(), "about": "to が自分の行を、動く前に読んでやる。やったら data/yatta.json の rows に {day, item, what} を1行足す（7日後に機械が効いた・効かなかったを付ける）。ng の手はくり返さない", "orders": orders}, open(P("data", "shirei.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(manabi, open(P("data", "manabi.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n".join(L))
