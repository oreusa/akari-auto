"""11/10 表紙 v3（TOWN NOTE と同じ「1つの地図で4つのノート」）を LIFE NOTE の入口に当てる。lifenote.py が入口を作ったあとに呼ぶ。
数字は site/assets/cover.json（都県ごとの開催中・地価の上がり幅・実家ノートの街の数。3KB）。見た目と動きは site/assets/cover.css・cover.js（月と同じファイル）。
関東はご相談を受けないので、実家のカードは「査定くらべ」（広告）にする。"""
import json, os, re, datetime, html
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(R, "site")
PREF = ["東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬"]
SLUG = {"tokyo": "東京", "kanagawa": "神奈川", "saitama": "埼玉", "chiba": "千葉", "ibaraki": "茨城", "tochigi": "栃木", "gunma": "群馬"}
V = "2"
today = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d")
P = {p: {"od": 0, "free": 0, "odL": [], "tw": 0, "upT": 0, "avg": 0.0, "top": [], "kN": 0, "kAvg": 0} for p in PREF}

# おでかけ：「開催中」の段のカード（終わった物は数えない）
try:
    s = open(os.path.join(S, "odekake.html"), encoding="utf-8").read()
    m = re.search(r'<div class="pane" data-t="now">(.*?)<div class="pane" data-t="', s, re.S)
    for c in re.finditer(r'<div class="card it" data-pref="([^"]*)" data-free="(\d)"[^>]*?data-e="([^"]*)"[^>]*>(.*?)<div class="m">', m.group(1) if m else "", re.S):
        p, fr, e, body = c.groups()
        if p not in P or (e and e < today):
            continue
        x = P[p]; x["od"] += 1; x["free"] += fr == "1"
        t = re.search(r'<div class="t">(.*?)</div>', body, re.S)
        if t and len(x["odL"]) < 3:
            x["odL"].append({"t": html.unescape(re.sub(r"<[^>]+>", "", t.group(1))).strip()})
except Exception as ex:
    print("cover: odekake skipped", ex)

# 街の地価（住宅地 1年の動き）
T = json.load(open(os.path.join(S, "assets", "towns.json"), encoding="utf-8"))
for p in PREF:
    tw = [t for t in T if t["p"] == p and isinstance(t.get("r8"), (int, float))]
    if not tw:
        continue
    x = P[p]; x["tw"] = len(tw); x["upT"] = sum(1 for t in tw if t["r8"] > 0)
    x["avg"] = round(sum(t["r8"] for t in tw) / len(tw), 1)
    x["top"] = [{"n": t["n"], "r": t["r8"], "id": t["id"]} for t in sorted(tw, key=lambda t: -t["r8"])[:3]]

# 実家ノートの街の数
jd = os.path.join(S, "jikka")
for n in (os.listdir(jd) if os.path.isdir(jd) else []):
    p = SLUG.get(n.split("-")[0])
    if p and n.endswith(".html"):
        P[p]["kN"] += 1
NJ = sum(P[p]["kN"] for p in PREF)
json.dump({"at": today, "p": P}, open(os.path.join(S, "assets", "cover.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))


def apply(s):
    if 'id="cover3"' in s:
        return s
    s = re.sub(r'<nav class="q3">.*?</nav>', '', s, count=1, flags=re.S)
    lens = ('<div class="today" id="today"></div><div class="lens" id="lens" role="tablist" aria-label="地図で見るもの">'
            '<button type="button" data-l="od" class="on" style="--c:#E39B3A"><small>01</small>おでかけ</button>'
            '<button type="button" data-l="fu" style="--c:#4F7BA8"><small>02</small>街の地価</button>'
            '<button type="button" data-l="jk" style="--c:#5E9E6E"><small>03</small>実家</button>'
            '<button type="button" data-l="ok" style="--c:#C2727F"><small>04</small>おかいもの</button></div>')
    s = s.replace('<p class="pur">', lens + '<p class="pur">', 1)
    jk = ('<a class="ls" href="/jikka/" data-k="入口｜実家・空き家ノート" style="--ac:#5E9E6E;--bg:#EEF6F0;--c:#5E9E6E"><div class="no"><small>PAGE</small>03</div>'
          '<div class="en">JIKKA NOTE</div><h3>実家・空き家ノート</h3><p>相続した家を、売る・片付ける・解体する前に。</p>'
          f'<div class="st"><div><span>関東の街</span><b>{NJ or "―"}</b></div><div><span>やること</span><b>4<small style="font-size:12px">つ</small></b></div><div><span>査定くらべ</span><b style="font-size:15px">無料</b></div></div>'
          '<div class="go">実家ノートを開く<span>→</span></div></a>')
    s = s.replace('<a class="ls" href="/okaimono"', jk + '<a class="ls" href="/okaimono"', 1)
    s = s.replace('<div class="no"><small>PAGE</small>03</div><div class="en">OKAIMONO LIST', '<div class="no"><small>PAGE</small>04</div><div class="en">OKAIMONO LIST', 1)
    s = s.replace('</head>', f'<link id="cover3" rel="stylesheet" href="/assets/cover.css?v=1"></head>', 1)
    s = s.replace('</body>', f'<script src="/assets/cover.js?v={V}" defer></script></body>', 1)
    return s


ip = os.path.join(S, "index.html")
src = open(ip, encoding="utf-8").read()
open(ip, "w", encoding="utf-8").write(apply(src))
print("cover v3 (関東)", {p: (P[p]["od"], P[p]["avg"], P[p]["kN"]) for p in PREF})
