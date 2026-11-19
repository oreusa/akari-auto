# 投稿の写真の表紙を機械で作る（11/19 オーナー「投稿に使う写真も劇的に変えれる」「関東の方も全部の話だよね？」）。
# 予約の前（book.yml）に動く。今日の予定表のおでかけの枠で、まだ予約していない物を data/photo-pick.json の写真と照らし、
# 合う写真があれば scripts/post_photo.js で表紙を作って site/card/ に置き、data/photo-auto.json に「日付 時刻 → 絵のURL」を書く。
# book.py はこの表を見て、予定表の image より先にこの絵を付ける。
# 写真は data/photo-pick.json に月か燈が目で見て入れた物だけ（催しそのもの・季節が合う・幅900px以上・cr あり）。合わない枠は今の絵のまま。
# 使い方：python3 scripts/photo_auto.py [--need]（--need は作る物があれば yes を出すだけ。道具を入れるかどうかに使う）
import json, os, re, subprocess, sys, tempfile, time
from datetime import datetime, timedelta, timezone

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JST = timezone(timedelta(hours=9))
RAW = "https://raw.githubusercontent.com/oreusa/akari-auto/main/site/card/"
WD = "月火水木金土日"


def load(p, d):
    try:
        with open(os.path.join(R, p), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return d


def in_season(pk, day):
    md = day[5:]
    a, b = pk.get("from", "01-01"), pk.get("to", "12-31")
    return a <= md <= b if a <= b else (md >= a or md <= b)


def pick_for(post, day, picks):
    t = (post.get("threads") or post.get("x") or [""])[0].split("\n")[0] + " " + str(post.get("place", ""))
    for pk in picks:
        if all(w in t for w in pk["all"]) and (not pk.get("any") or any(w in t for w in pk["any"])) and in_season(pk, day):
            return pk
    return None


def spec_for(post, day, slot, pk):
    line = (post.get("threads") or post.get("x") or [""])[0].split("\n")[0]
    m = re.match(r"【([^｜]+)｜([^】]+)】", line)
    if not m:
        return None
    left, body = m.group(1).strip(), m.group(2).strip()
    parts = re.split(r"[　 ]+", left, maxsplit=1)
    when, place = (parts[0], parts[1]) if len(parts) == 2 else ("", left)
    dm = re.match(r"(\d{1,2})/(\d{1,2})(.*)", when)
    big, unit = (f"{int(dm.group(1))}.{int(dm.group(2)):02d}", dm.group(3)[:4]) if dm else (None, None)
    pill = post.get("topic", "")
    if dm:
        try:
            wd = WD[datetime(int(day[:4]) + (1 if int(dm.group(1)) < int(day[5:7]) else 0), int(dm.group(1)), int(dm.group(2))).weekday()]
            pill += f"　{int(dm.group(1))}/{int(dm.group(2))}（{wd}）{dm.group(3)}"
        except ValueError:
            pill += "　" + when
    elif when:
        pill += "　" + when
    name = f"photo-{day[5:].replace('-', '')}-{slot.replace(':', '')}"
    base = {"name": name, "im": pk["file"], "cr": pk["cr"], "pos": pk.get("pos", "50% 50%"), "pill": pill.strip(),
            "big": big, "unit": unit, "en": pk.get("en", "")}
    cap = pk.get("cap", "")
    # 長い見出しは字を小さく、まだ入らなければ名前だけを見出しにして中身は下の小さい字へ
    return [dict(base, head=f"<em>{place}</em><br>{body}", cap=cap, nowrap=True),
            dict(base, head=f"<em>{place}</em><br>{body}", cap=cap, hs=60, nowrap=True),
            dict(base, head=f"<em>{place}</em>", cap=body, nowrap=True),
            dict(base, head=f"<em>{place}</em>", cap=body, hs=60, nowrap=True)]


def main():
    now = datetime.now(JST)
    day = now.date().isoformat()
    sched = load(f"schedule/{day}.json", {}) or {}
    picks = (load("data/photo-pick.json", {}) or {}).get("items") or []
    booked = load("state/booked.json", {}) or {}
    made = load("data/photo-auto.json", {}) or {}
    todo = []
    for post in sched.get("posts", []):
        slot = post.get("slot", "")
        key = f"{day} {slot}"
        if "おでかけ" not in str(post.get("series", "")) or key in made:
            continue
        if any((booked.get(key) or {}).get(s, {}).get("id") for s in ("threads", "twitter")):
            continue
        pk = pick_for(post, day, picks)
        if pk:
            sp = spec_for(post, day, slot, pk)
            if sp:
                todo.append((key, sp))
    if "--need" in sys.argv:
        print("yes" if todo else "no")
        return 0
    for key, tries in todo:
        for sp in tries:
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
                json.dump([sp], f, ensure_ascii=False)
            r = subprocess.run(["node", os.path.join(R, "scripts", "post_photo.js"), f.name], capture_output=True, text=True, timeout=120)
            out = os.path.join(R, "site", "card", f"card-{sp['name']}.jpg")
            if "作った 1 枚" in r.stdout and os.path.exists(out):
                made[key] = {"url": RAW + f"card-{sp['name']}.jpg?v={int(time.time()) % 100000000:x}",
                             "photo": sp["im"], "cr": sp["cr"], "head": sp["head"]}
                print(f"写真の表紙：{key} {sp['im']}")
                break
            print(f"写真の表紙×（次の形で）：{key} {r.stdout.strip()[-120:]} {r.stderr.strip()[-200:]}")
    old = (now - timedelta(days=14)).date().isoformat()
    made = {k: v for k, v in made.items() if k[:10] >= old}
    with open(os.path.join(R, "data", "photo-auto.json"), "w", encoding="utf-8") as f:
        json.dump(made, f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
