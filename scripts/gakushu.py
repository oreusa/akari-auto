"""関東の学習の台帳（11/11 オーナー「直して欲しいんじゃない。学習して成長し考えることが出来るシステムを」）。
ばらばらだった帳面（成長の帳面・当たり帳・GPTの回の記録・ページの数）を1枚にまとめ、項目ごとに
①機械が測った数字 ②合格の線 ③答え（当たり・外れ・未確認）④機械が出す指令 を毎朝作る。
- notes/gakushu.md  1枚（燈の夜の回は、これを最初に読む。ほかの帳面は、指令に書いてある時だけ開く）
- data/shirei.json  きょうの指令（to＝燈の夜・投稿・リール・月）
- data/manabi.json  学びの帳面（答えが変わった日に機械が1行足す。同じ外れをくり返さない）
数字が取れない項目は「未確認」。計画を実績と書かない。使い方：python3 scripts/gakushu.py [YYYY-MM-DD]"""
import glob, json, os, re, statistics, sys
from datetime import date, timedelta

# 11/12 調べ役やテストが打った言葉（あいうえお・xyz999・セール 等）が「探されたのに無かった物」の指令になっていた → 品物の名前らしくない物は外す
def _tameshi(k):
    k = str(k).strip()
    return (len(k) < 2 or re.fullmatch(r"[a-zA-Z0-9]+", k) is not None or k in ("あいうえお", "テスト", "test", "セール", "おすすめ", "安い", "最安", "送料無料")
            or re.fullmatch(r"(.)\1+", k) is not None)

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
            posts.append({"day": day, "svc": p.get("service"), "slot": p.get("slot", ""), "kind": p.get("kind", ""), "v": int(m.get("views", m.get("impressions")) or 0), "first": p.get("first", ""), "img": p.get("img")})
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
# 4コマ（雫＝GPTの絵）。11/12 09:04 owner「関東4コマ辞める。その代わり違う仕事を」「GPTに絵をかくのはやめる」→ 11/13 からやめた。雫は朝の楽天ROOMとコメント返信に替えた（指示_雫）。
# 下は、やめる前の数字を残すだけ（指令は出さない）。
_k4 = {sv: [p["v"] for p in now if p["svc"] == sv and p["kind"] == "4コマ"] for sv in ("twitter", "threads", "instagram")}
_n4 = {sv: [p["v"] for p in now if p["svc"] == sv and p["kind"] == "通常"] for sv in ("twitter", "threads")}
if any(_k4.values()):
    item("koma4", "4コマ（11/13 からやめた。前の数字）", f"X {med(_k4['twitter'])}（ふつうの投稿 {med(_n4['twitter'])}）・Threads {med(_k4['threads'])}（ふつう {med(_n4['threads'])}）・インスタ {med(_k4['instagram'])}", "―", "やめた", "オーナーが 11/12 に決めた。GPT（雫）は朝の楽天ROOMとコメント返信へ")
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
    order("リール", "ig", f"インスタの4コマ（中央値 {med(ig['4コマ'])}）は 11/13 からやめた（オーナー 11/12）。インスタは、おでかけリール（中央値 {med(ig['おでかけリール'])}）だけを1日2本。表紙の1枚目に題とロゴを出す（プロフィールの一覧に並ぶため）。GPTに絵は描かせない", "リールが4コマの5倍以上")

# 4b 絵本を開く型のリール（11/12 から。その前のリールとくらべる。6本で答え）
_eh = [p["v"] for p in posts if p["svc"] == "instagram" and p["kind"] == "おでかけリール" and p["day"] >= "2026-11-12"]
_bf = [p["v"] for p in posts if p["svc"] == "instagram" and p["kind"] == "おでかけリール" and p["day"] < "2026-11-12"]
item("reel-ehon", "絵本を開く型のリール（11/12〜）", f"絵本 {len(_eh)}本 中央値 {med(_eh)}・その前 {len(_bf)}本 中央値 {med(_bf)}", "6本で、前の型の中央値を越える", "計測中" if len(_eh) < 6 else ("当たり" if med(_eh) > med(_bf) else "外れ"), "型を替えた答えを、同じ物差し（見られた数）で出す")
if len(_eh) >= 6 and med(_eh) > med(_bf): order("リール", "reel-ehon", f"絵本の型が前の型より上（{med(_bf)}→{med(_eh)}）。いちばん見られた回の題材と1枚目の言葉を、次の3本でまねる", "当たり：型が効いた")
elif len(_eh) >= 6: order("リール", "reel-ehon", f"絵本の型が前の型より下（{med(_bf)}→{med(_eh)}）。型は残し、1枚目の題を「場所＋日付＋無料か」に、声の1行目を問いかけにして3本試す。1つずつ変える", "外れ：1枚目で止まっていない")

# 4c 夜の手順の長さ（毎晩ぜんぶ読む物。長いほど費用がかかり、古い決まりが残るほど間違える）
_np = open(P("docs", "nightly-prompt.md"), encoding="utf-8").read(); _kb = len(_np.encode()) // 1024
_dead = [w for w in ("koma4/D.json", "凪の明日の目標", "旅先4コマ", "ROOM台本を", "Amazon確認帳に書いた物だけ") if w in _np]
item("tejun", "夜の手順の長さ", f"{_kb}KB・やめた仕事の言葉 {len(_dead)}" + (f"（{'・'.join(_dead)}）" if _dead else ""), "46KB より短い・やめた仕事の言葉 0", "当たり" if _kb <= 46 and not _dead else "外れ", "毎晩ぜんぶ読む。やめた決まりが残ると、上と下でぶつかる")
if _kb > 46 or _dead: order("月", "tejun", f"夜の手順（docs/nightly-prompt.md）が {_kb}KB" + (f"・やめた仕事の言葉が残っている（{'・'.join(_dead)}）" if _dead else "") + "。足した決まりと同じ数だけ、古い決まりを docs/history へ移す", "足すだけだと毎晩の費用が増え、ぶつかる決まりで間違える")

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

# 6b' 絵つきの投稿（11/12 オーナー「写真も効果ありならちょこちょこ入れる」）。HPの画面の絵を、同じ枠で1日おきに付けてくらべる。
# 答えは data/postimg-rule.json に書き、book.py がそれで動く（all＝全部に付ける・pr＝PRだけ・half＝1日おきでくらべ続ける）。PR（くらべた話）はいつも付ける。
_ia = [p["v"] for p in now if p["svc"] == "threads" and p.get("img") == 1 and not (p.get("first") or "").startswith("【くらべた")]
_ib = [p["v"] for p in now if p["svc"] == "threads" and p.get("img") == 0]
_imode = "all" if min(len(_ia), len(_ib)) < 8 else (  # 11/12 月：数がそろうまでは全部に付ける（関西で絵つきが文字だけの1.7倍だった。オーナー「関東の方も画像付きにした？」）
    "all" if med(_ia) >= med(_ib) * 1.15 else ("pr" if med(_ia) <= med(_ib) * 0.85 else "half"))
json.dump({"about": "投稿に絵を付ける決まり。gakushu.py が数字で決め、book.py が読む", "mode": _imode, "day": today.isoformat(), "img": [len(_ia), med(_ia)], "noimg": [len(_ib), med(_ib)]}, open(P("data", "postimg-rule.json"), "w", encoding="utf-8"), ensure_ascii=False)
item("post-img", "絵つきの投稿（HPの画面）", f"Threads 絵あり {len(_ia)}本 中央値 {med(_ia) if _ia else '未確認'}・絵なし {len(_ib)}本 中央値 {med(_ib) if _ib else '未確認'}", "絵ありが絵なしの1.15倍より上", "計測中" if min(len(_ia), len(_ib)) < 8 else {"all": "当たり", "pr": "外れ", "half": "計測中"}[_imode], {"all": "当たり → 合う絵がある投稿の全部に付ける", "pr": "外れ → PR（くらべた話）だけに付ける", "half": "同じ枠で1日おきに付けてくらべている（8本ずつたまるまで）"}[_imode])

# 6c くらべた話（11/12 オーナーがカードで「1日1本だけ7日ためす」。11/13〜11/19。見出しが「【くらべた｜」で始まる投稿を、通常の投稿とくらべる）
_kb = [p for p in posts if (p.get("first") or "").startswith("【くらべた") and p["svc"] in ("threads", "twitter")]
_kbt = [p["v"] for p in _kb if p["svc"] == "threads"]; _nt = [p["v"] for p in now if p["svc"] == "threads" and p["kind"] == "通常" and not (p.get("first") or "").startswith("【くらべた")]
_kbuy = sum(_c for _d, _v in load(P("data", "page-stats.json"), {}).get("days", {}).items() if _d >= "2026-11-13" for _k, _c in ((_v.get("click") or {}).get("okaibuy") or {}).items())
_kdays = len({p["day"] for p in _kb})
item("kurabe", "くらべた話（7日の試し 11/13〜11/19）", f"{_kdays}日ぶん・Threads 中央値 {med(_kbt) if _kbt else '未確認'}（通常 {med(_nt)}）・HPの買うボタン {_kbuy}回（11/13から）", "通常の中央値より上、かつ買うボタンが1回でも押される", "計測中" if _kdays < 7 else ("当たり" if med(_kbt) >= med(_nt) and _kbuy > 0 else "外れ"), "オーナーが決めた試し。7日たつまで本数を変えない")
if today.isoformat() <= "2026-11-19" and not any(p["day"] == today.isoformat() for p in _kb) and today.isoformat() >= "2026-11-12":
    order("燈の夜", "kurabe", "あすの予定表に「くらべた話」を1本だけ入れる（12:15 か 13:45。見出しは「【くらべた｜物、単位あたりの最安は◯円】」。商品のリンクなし。2つ目に HP の /okaimono-<種類> を1つ。まだ出していない種類）。決まりは nightly-prompt の一番上", "オーナーが決めた7日の試し")
if _kdays >= 7:
    if med(_kbt) < med(_nt): order("月", "kurabe", f"くらべた話は7日の中央値 {med(_kbt)} で、通常 {med(_nt)} より下。やめる。オーナーに数字で報告する", "試しの答え：外れ")
    else: order("月", "kurabe", f"くらべた話は7日の中央値 {med(_kbt)}（通常 {med(_nt)}）・買うボタン {_kbuy}回。続けるか・本数をオーナーに聞く", "試しの答え")

# 7a おかいもの（11/12 オーナー「おかいものの方も工夫してくれ」）。開いた数（どこから）→ 探した・絞った → 買うボタン の3段を機械が測り、落ちている段を直す指令を出す
_ok = {"open": {}, "ope": 0, "buy": 0, "top": {}, "none": {}}
for _d, _v in load(P("data", "page-stats.json"), {}).get("days", {}).items():
    if _d <= d7: continue
    for _k, _c in ((_v.get("click") or {}).get("okaimono") or {}).items():
        _k = _k.split("|", 1)[-1]
        if _k.startswith("表示:"): _ok["open"][_k[3:]] = _ok["open"].get(_k[3:], 0) + _c
        else:
            _ok["ope"] += _c
            if _k.startswith("探す・なし:"): _ok["none"][_k[6:]] = _ok["none"].get(_k[6:], 0) + _c
            if _k.startswith("種類:"): _ok["top"][_k[3:]] = _ok["top"].get(_k[3:], 0) + _c
    for _k, _c in ((_v.get("click") or {}).get("okaibuy") or {}).items(): _ok["buy"] += _c
_oo = sum(_ok["open"].values()); _top = sorted(_ok["top"].items(), key=lambda x: -x[1])[:3]; _none = sorted(((k, v) for k, v in _ok["none"].items() if not _tameshi(k)), key=lambda x: -x[1])[:3]
item("okai", "おかいもの", (f"開いた {_oo}（" + "・".join(f"{k} {v}" for k, v in sorted(_ok["open"].items(), key=lambda x: -x[1])) + "）" if _oo else "開いた 計測中（11/12 から数える）") + f"・探した/絞った {_ok['ope']}・買うボタン {_ok['buy']}" + (f"・よく見られた種類 {'・'.join(f'{k} {v}' for k, v in _top)}" if _top else ""), "開いた人の1割が買うボタンを押す", "計測中" if _oo < 20 else ("当たり" if _ok["buy"] >= _oo * 0.1 else "外れ"), "買うボタンは 11/12 から数えている（その前は数えていなかった）")
if _none: order("燈の夜", "okai", f"おかいもので探されたのに無かった物：{'・'.join(f'{k}（{v}回）' for k, v in _none)}。いちばん多い物を、くらべる種類に1つ足す（名の知れたメーカー・送料込みの1個あたり）", "探しに来た人が、何も見ずに帰っている")
if _oo >= 20 and _ok["buy"] < _oo * 0.1:
    if _ok["ope"] < _oo: order("燈の夜", "okai", "おかいものを開いた人の半分以上が、何も押さずに帰っている。最初の画面に、いちばん見られた種類（" + ("・".join(k for k, _ in _top) or "未確認") + "）の「いちばん安い1つ」と買うボタンを、選ばなくても見える形で3つ置く", f"開いた {_oo}・操作 {_ok['ope']}")
    else: order("燈の夜", "okai", "おかいもので探す・絞るまではされているのに、買うボタンが押されない。順位の1位の行に「いつもの店より いくら安いか」を金額で出し、買うボタンを行の中の見える所へ上げる", f"操作 {_ok['ope']}・買う {_ok['buy']}")
elif _top and _oo >= 20: order("燈の夜", "okai", f"おかいもので買うボタンが押された。いちばん見られた種類「{_top[0][0]}」と同じ形で、近い種類を1つ足し、投稿の2本目を1本そこへ向ける", "当たった型を増やす")

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
PRI = ["lead", "michi", "come", "city", "hp", "post-threads", "post-twitter", "post-kind", "post-hit", "koma4", "ig", "reel-ehon", "kurabe", "okai", "money", "asp", "gpt"]
_old = {(o["to"], o["item"], o["order"][:24]): o.get("days", 1) for o in prev.get("orders", [])}
for o in orders:
    if any(w in o["order"] for w in ("data/seika.json", "gpt-runs.md", "台帳 notes/daichou.md")): o["kind"] = "数字"
    d = _old.get((o["to"], o["item"], o["order"][:24]))
    o["days"] = (d if prev.get("day") == today.isoformat() else d + 1) if d else 1
    _w = [y["what"] for y in yatta["rows"] if "result" not in y and y.get("item") == o["item"]]
    if _w: o["wait"] = _w[-3:]
    if ng.get(o["item"]): o["ng"] = ng[o["item"]][-3:]
    if ok.get(o["item"]): o["ok"] = ok[o["item"]][-3:]
# 指令をやったかの見張り（11/12 オーナー「一つ一つ完璧な仕組みにしろ」）。指令が出ているのに、その項目に手（data/yatta.json の行）が無い日数を数える。
# 同じ項目に指令が2つ以上ある時は、行の order（指令の最初の24字）が合う手だけを数える（order の無い古い行は、その項目の1つ目の指令の手とみなす）
from datetime import timedelta as _td
def _last(o):
    sib = [x for x in orders if x["item"] == o["item"] and x["to"] == o["to"]]
    return max([y.get("day", "") for y in yatta["rows"] if y.get("item") == o["item"] and (len(sib) < 2 or y.get("order", "")[:24] == o["order"][:24] or ("order" not in y and sib[0] is o))] or [""])
# 11/12 待つしかない指令（月曜の汐の写し待ち）は「手が無い」に数えない。足す時は、何を待つかを指令の文に書く
MACHI = {"asp"}
for o in orders:
    lt = _last(o); st = (today - _td(days=o["days"] - 1)).isoformat()
    o["idle"] = o["days"] if lt < st else max(0, (today - date.fromisoformat(lt)).days)
orders.sort(key=lambda o: (o["kind"] != "作る", PRI.index(o["item"]) if o["item"] in PRI else 99))
# 11/12 月の作り替え（オーナー「無駄な仕組みになってないか」）：指令は回ごとに1日3本まで。残りは控え（hikae）。関西の台帳（usagi tools/seichou/gakushu.py）と同じ決まり
# 11/12 段（関西の台帳と同じ）：載る（Google に100枚）→ 来る（見られた 週1500）→ 申し込む（送信 週1件）→ お金。2つ先の段の指令は出さない（控えへ）
def _idx_kanto():
    try:
        import urllib.request
        r = json.loads(urllib.request.urlopen("https://raw.githubusercontent.com/oreusa/usagi-fudosan-media/main/stats/kensaku.json", timeout=8).read().decode("utf-8"))
        k = [x for x in r.get("rows", []) if x.get("site") == "kanto" and x.get("idx") is not None]
        return sorted(k, key=lambda x: x.get("day", ""))[-1]["idx"] if k else None
    except Exception: return None
IDX = _idx_kanto()
DAN_N = ["載る", "来る", "申し込む", "お金"]
DAN_L = ["Google に関東100枚", "見られた 週1500", "送信 週1件", "成果 月1件"]
dan = 0 if (IDX is not None and IDX < 100) else (1 if n.get("views", 0) < 1500 else (2 if sent < 1 else 3))
DS = {"city": 0, "hp": 0, "michi": 0, "come": 1, "post-threads": 1, "post-twitter": 1, "post-kind": 1, "post-hit": 1, "koma4": 1, "ig": 1, "reel-ehon": 1, "kurabe": 1, "asp": 1, "gpt": 0,
      "lead": 2, "okai": 2, "money": 3}
_nn = {}; hikae = []; _act = []
for o in orders:
    if DS.get(o["item"], 0) > dan + 1: o["hold"] = f"いまの段は「{DAN_N[dan]}」。この指令は「{DAN_N[min(3, DS[o['item']])]}」の段の物"; hikae.append(o)
    elif _nn.get(o["to"], 0) >= 3: o["hold"] = "1日3本まで"; hikae.append(o)
    else: _act.append(o); _nn[o["to"]] = _nn.get(o["to"], 0) + 1
orders = _act
for to in ("燈の夜", "月"):
    _c = [o for o in orders if o["to"] == to and o["kind"] == "作る"]
    f_ = next((o for o in _c if len(o.get("wait", [])) < 2), _c[0] if _c else None)
    if f_: f_["first"] = True
_firsts = {o["to"]: o["item"] for o in orders if o.get("first")}
for _i, to in enumerate(("燈の夜", "月")):
    _m = [o for o in orders if o["to"] == to]; _late = [o for o in _m if o.get("idle", 0) >= 3 and o["item"] not in MACHI]
    _pf = (prev.get("first_items") or {}).get(to); _pd = prev.get("day", "")
    _did = (not _pf) or _pd == today.isoformat() or any(y.get("item") == _pf and y.get("day", "") >= _pd for y in yatta["rows"])
    items.insert(_i, {"id": "jikkou-" + ("akari" if to == "燈の夜" else "tsuki"), "name": f"指令をやったか（{to}）", "num": f"{to}あての指令 {len(_m)}本・3日以上 手が無い {len(_late)}本" + (f"（{'・'.join(sorted(set(o['item'] for o in _late)))}）" if _late else "") + f"・きのうの【きょうの1つ】{'やった' if _did else 'やっていない'}",
                       "line": "きのうの1つをやった・3日以上 手が無い指令 0本", "ans": "当たり" if _did and not _late else "外れ", "why": "仕組みを作っても、指令どおりに動かなければ意味がない（11/12 オーナー）"})
def line(o):
    t = ("【きょうの1つ】" if o.get("first") else ("【数字を入れる】" if o["kind"] == "数字" else "")) + o["order"] + f"（理由：{o['why']}）"
    if o.get("idle", 0) >= 3 and o["item"] not in MACHI: t += f" ！{o['idle']}日 手が無い＝まだやられていない（やったら data/yatta.json に1行）"
    elif o["days"] >= 3: t += f"（{o['days']}日目。手は打ってある）"
    if o.get("wait"): t += "／答え待ちの手（同じ所を重ねて変えない。足りない所だけ足す）：" + "・".join(o["wait"])
    if o.get("ng"): t += "／前に効かなかった手（くり返さない）：" + "・".join(o["ng"])
    if o.get("ok"): t += "／前に効いた手（同じ型を増やす）：" + "・".join(o["ok"])
    return "- " + t
def mline(m):
    if m.get("kind") == "手の答え": return f"- {m['day']} {m['item']}：やった手「{m['what']}」→ {m['result']}（{m['before']}→{m['after']}）"
    return f"- {m['day']} {m['item']}：{m['from']}→{m['to']}（{m['num']}）。その前に出ていた指令：{'／'.join(m['did']) or '記録なし'}"
MARK = {"当たり": "◎", "外れ": "×", "未確認": "？", "計測中": "…"}
L = [f"# 関東の学習の台帳（{today.isoformat()} 朝）", "", "機械が毎朝作ります。燈の夜の回は、これを最初に読み、自分あての指令をそのままやります。数字が取れない物は「未確認」。", "",
     "## いちばん上の3つ（この3つが動かなければ、ほかが当たりでも進んでいない）", "", f"- 投稿からHPに来た人（7日）：**{n.get('come', 0)}**（線 週50）", f"- 反響（送信・7日）：**{sent}**（線 週1件）", f"- Google に載った枚数（関東）：**{'未確認' if IDX is None else IDX}**（線 100枚）", "", f"いまの段：**{DAN_N[dan]}**（越える線：{DAN_L[dan]}）。段は 載る → 来る → 申し込む → お金。2つ先の段の指令は出しません（控え {len(hikae)}本）。指令は回ごとに1日3本まで。", "",
     "## 項目ごと", "", "| | 項目 | 機械が測った数字 | 合格の線 | 答え |", "|---|---|---|---|---|"]
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
json.dump({"day": today.isoformat(), "first_items": _firsts, "items": items, "orders": orders, "hikae": hikae, "sum": {"sent": sent, "seika": (_s if _sb7 else None)}, "hist": hist}, open(P("data", "gakushu.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({"day": today.isoformat(), "about": "to が自分の行を、動く前に読んでやる。やったら data/yatta.json の rows に {day, item, what} を1行足す（同じ item の指令が2つ以上ある時は order に指令の最初の24字も書く。書かないと「手が無い」と数えられる）（7日後に機械が効いた・効かなかったを付ける）。ng の手はくり返さない", "orders": orders}, open(P("data", "shirei.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(manabi, open(P("data", "manabi.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n".join(L))
