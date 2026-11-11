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
def order(to, id, text, why): orders.append({"to": to, "item": id, "order": text, "why": why})

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
    if k != "通常" and len(v) >= 5 and med(v) * 3 < base:
        order("投稿", "post-kind", f"「{k}」の投稿（中央値 {med(v)}、通常は {base}）は、Threads と X では週2本までに減らし、空いた枠を通常の当たりの型に回す", "通常の3分の1より下が7日続いた")
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
    order("リール", "ig", f"インスタの4コマ（中央値 {med(ig['4コマ'])}）は出すのをやめ、おでかけリール（中央値 {med(ig['おでかけリール'])}）を1日2本にする。うさぎちゃんの絵はリールの表紙に使う", "リールが4コマの5倍以上")

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
item("money", "買い物・宿・ROOM", f"押された {n.get('buy', 0)}（前 {pv.get('buy', 0)}）・成果 {last.get('hassei', '未確認') if last else '未確認'}・確定 {last.get('kakutei', '未確認') if last else '未確認'}・ROOMで売れた {last.get('room_uri', '未確認') if last else '未確認'}", "成果 月1件", ("当たり" if int(last.get("hassei") or 0) > 0 else "外れ") if last else "未確認", "クリックは売上ではない")
if not last or (today - date.fromisoformat(last["day"])).days > 8:
    order("燈の夜", "money", "月曜の汐の写し（楽天・A8・バリューコマースの成果、ROOM のクリックと売れた数）を data/seika.json の rows に {day, hassei, kakutei, nyukin, room, room_uri} で1行入れる。写しが無ければ「未確認」のまま、連絡帳に1行", "成果が未確認のまま")

# 7 反響
item("lead", "相談（反響）", f"申し込みを開いた {n.get('open', 0)}・送信 {n.get('sent', 0)}", "反響 月10件", "当たり" if n.get("sent", 0) >= 3 else "外れ", "関東も問い合わせはオーナーへ")

pa = {i["id"]: i for i in prev.get("items", [])}
for i in items:
    o = pa.get(i["id"])
    if o and o["ans"] != i["ans"] and i["ans"] not in ("未確認", "計測中"):
        manabi["rows"].append({"day": today.isoformat(), "item": i["name"], "from": o["ans"], "to": i["ans"], "num": i["num"], "did": [x["order"] for x in prev.get("orders", []) if x["item"] == i["id"]][:2]})
MARK = {"当たり": "◎", "外れ": "×", "未確認": "？", "計測中": "…"}
L = [f"# 関東の学習の台帳（{today.isoformat()} 朝）", "", "機械が毎朝作ります。燈の夜の回は、これを最初に読み、自分あての指令をそのままやります。数字が取れない物は「未確認」。", "",
     "| | 項目 | 機械が測った数字 | 合格の線 | 答え |", "|---|---|---|---|---|"]
L += [f"| {MARK.get(i['ans'], '')} | {i['name']} | {i['num']} | {i['line']} | {i['ans']} |" for i in items]
L += ["", "## きょうの指令", ""]
for to in ("燈の夜", "投稿", "リール", "月"):
    xs = [o for o in orders if o["to"] == to]
    if xs: L += [f"### {to}"] + [f"- {o['order']}（理由：{o['why']}）" for o in xs] + [""]
L += ["## 学び（答えが変わった日）", ""] + ([f"- {m['day']} {m['item']}：{m['from']}→{m['to']}（{m['num']}）。その前にやった事：{'／'.join(m['did']) or '記録なし'}" for m in manabi["rows"][-12:]] or ["- まだありません"]) + [""]
open(P("notes", "gakushu.md"), "w", encoding="utf-8").write("\n".join(L))
json.dump({"day": today.isoformat(), "items": items, "orders": orders}, open(P("data", "gakushu.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"day": today.isoformat(), "orders": orders}, open(P("data", "shirei.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(manabi, open(P("data", "manabi.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n".join(L))
