"""11/19 オーナー「おかいものの良さは Amazon・楽天・Yahoo を1つで見れる良さ」→ 新しい土台のおかいもの（townnote /shin/kau）用の値段の表。
okai_v4.build() と同じ中身（楽天・Yahoo! の1L・1枚あたり）＋ブラックフライデーの行（夜の Amazon・楽天）を site/okai-shin.json に出す。
/shin/kau はこの表を毎回取りに来る（_headers で TOWN NOTE から読めるようにしている）。page.yml で bf_okaimono.py の後に動く。"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "scripts"))
import okai_v4  # noqa: E402
import bf_okaimono  # noqa: E402

JST = timezone(timedelta(hours=9))


def bf_rows(now):
    if not (bf_okaimono.START <= now <= bf_okaimono.END):
        return []
    try:
        items = json.load(open(bf_okaimono.DATA, encoding="utf-8")).get("items", [])
    except Exception:
        return []
    out = []
    for it in items:
        try:
            at = datetime.strptime(it["at"], "%Y-%m-%d %H:%M").replace(tzinfo=JST)
        except Exception:
            continue
        if now - at > timedelta(hours=36):
            continue
        out.append({"w": "Amazon" if it["src"] == "amazon" else "楽天", "k": it.get("k") or "", "kind": it.get("kind") or "",
                    "n": it.get("n") or "", "q": it.get("q") or "", "p": it.get("p") or "", "cp": it.get("cp") or "",
                    "t": it.get("t") or "", "at": it["at"], "url": bf_okaimono.link(it)})
    return out


def main():
    at, cats = okai_v4.build()
    if len(cats) < 5:
        print("okai_shin: 種類が少ないので出さない", len(cats))
        return
    keep = ("n", "p", "u", "a", "s", "w", "av", "rc", "url", "img", "ut", "tg")
    out = []
    for c in cats:
        rows = []
        for o in sorted(c["o"], key=lambda x: x["u"]):
            r = {k: o[k] for k in keep if o.get(k) not in (None, "", [])}
            h = o.get("h") or {}
            if h:
                ds = sorted(h)[-30:]
                r["h"] = [h[d] for d in ds]
            rows.append(r)
        out.append({"k": c["k"], "nm": c["nm"], "unit": c["unit"], "seen": c.get("seen", 0), "o": rows})
    now = datetime.now(JST)
    d = {"at": at, "made": now.strftime("%Y-%m-%d %H:%M"), "amz": okai_v4.AMZ, "cats": out, "bf": bf_rows(now),
         "bfEnd": bf_okaimono.END.strftime("%Y-%m-%d %H:%M")}
    p = os.path.join(okai_v4.SITE, "okai-shin.json")
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("okai_shin:", len(out), "種類", sum(len(c["o"]) for c in out), "件・BF", len(d["bf"]), "件", os.path.getsize(p) // 1024, "KB")


if __name__ == "__main__":
    main()
