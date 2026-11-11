"""楽天ROOMの台本を、機械が毎日そろえる（notes/room-daihon.md）。11/11 月（オーナー「楽天roomとか…全部やれ」）。
それまで：夜の回が手で選ぶ → 古い商品で機械の確かめに落ちる（11/10 は9件中7件が×）・渡し忘れの夜は0件。
これから：その日の data/tanka.json（page.yml が楽天で取り直した、1個あたりで安い・レビュー4.0以上の物）から20件まで。
  ・燈が予定表 schedule/今日.json の room に入れた物があれば先頭に置く
  ・前の14日に台本へ出した物は出さない（data/room-log.json）
  ・同じ日に2回動いても同じ台本（朝7:30 と 夕18:30 の page.yml）
凪（GPT）は https://raw.githubusercontent.com/oreusa/akari-auto/main/notes/room-daihon.md を読む。"""
import json, os, re
from datetime import datetime, timezone, timedelta, date

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
MAX = 20
KEEP = 14
COL = {"毎日なくなる物": ("water", "soda", "rice", "tp", "tea", "coffee", "detergent", "softener", "shampoo", "bodysoap", "dish", "tissue", "trash", "pasta", "beans"),
       "赤ちゃん・ペットの毎日": ("diaper", "wipes", "dogfood", "catfood"),
       "そなえ": ("battery", "mask")}
FOR = {"water": "毎日飲む水を、重い買い物なしで届けてほしい家", "soda": "炭酸水を毎日飲む家", "rice": "お米をまとめて買っておきたい家", "tp": "トイレットペーパーを切らしたくない家",
       "tea": "お茶を箱で置いておきたい家", "coffee": "ボトルコーヒーを毎日飲む家", "detergent": "洗濯の回数が多い家", "softener": "柔軟剤を詰め替えで安く続けたい家",
       "shampoo": "シャンプーを詰め替えで続けたい家", "bodysoap": "ボディソープを家族で使う家", "dish": "食器用洗剤をまとめて置きたい家", "tissue": "ティッシュを箱で置いておきたい家",
       "trash": "ゴミ袋をまとめて買っておきたい家", "pasta": "パスタをよく作る家", "beans": "コーヒー豆を毎日ひく家", "diaper": "おむつを毎日たくさん使う家", "wipes": "おしりふきをまとめて置きたい家",
       "dogfood": "犬のごはんを切らしたくない家", "catfood": "猫のごはんを切らしたくない家", "battery": "乾電池をそなえておきたい家", "mask": "マスクを箱で置いておきたい家"}


def load(p, d):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return d


def yen(v):
    return f"{v:,.1f}".rstrip("0").rstrip(".") if v < 100 else f"{round(v):,}"


def main():
    today = datetime.now(timezone(timedelta(hours=9))).date()
    T = today.isoformat()
    log = load(P("data", "room-log.json"), {})
    log = {d: v for d, v in log.items() if (today - date.fromisoformat(d)).days <= KEEP}
    used = {u for d, v in log.items() if d != T for u in v}
    tk = load(P("data", "tanka.json"), {"cats": []})
    cand = {}
    for c in tk.get("cats", []):
        col = next((n for n, ks in COL.items() if c.get("key") in ks), None)
        if not col:
            continue
        for i, t in enumerate(c.get("top", []), 1):
            u = (t.get("plain") or "").split("?")[0]
            bd = t.get("bd") or ""
            if not u.startswith("https://item.rakuten.co.jp/") or not bd or bd not in t.get("name", "") or (t.get("av") or 0) < 4.0 or (t.get("rc") or 0) < 50 or not t.get("per"):
                continue
            cm = (f"選んだ理由：{c['title']}を{c.get('read', 0)}点、{c['unit']}あたりの値段にそろえて比べました。この{bd}は{c['unit']}あたり{yen(t['per'])}円"
                  f"（{t['amt']}で{t['price']:,}円・{today.month}/{today.day}時点）。レビューは{t['rc']:,}件で★{t['av']:.2f}です。\n"
                  f"ただし、値段と在庫は日によって変わります。送料はお店のページでご確認ください。\n{FOR.get(c['key'], 'まとめて買っておきたい家')}に向いています。")
            cand[u] = {"url": u, "name": t["name"][:60], "expect": bd, "comment": cm, "col": col, "tag": f"#{c['title'].split('（')[0]} #まとめ買い #1個あたりで比べた", "rank": i, "cat": c["key"]}
    sch = load(P("schedule", T + ".json"), {})
    hand = [r for r in (sch.get("room") or []) if isinstance(r, dict) and str(r.get("url", "")).startswith("https://item.rakuten.co.jp/") and r.get("comment")]
    if T in log:   # 同じ日の2回目：朝と同じ並びを保つ（無くなった物だけ落とす）
        order = [u for u in log[T]]
    else:
        order = []
    # 1位の物をカテゴリを回しながら → 2位…の順（同じ種類が続かないように）
    for u, x in sorted(cand.items(), key=lambda kv: (kv[1]["rank"], kv[1]["cat"])):
        if u not in used and u not in order:
            order.append(u)
    hand_urls = [r["url"].split("?")[0] for r in hand]
    order = [u for u in order if u in cand and u not in hand_urls][:max(0, MAX - len(hand))]
    rows = []
    for r in hand:
        rows.append((r.get("collection") or "毎日なくなる物", r.get("expect", ""), r["url"].split("?")[0], r["comment"], r.get("tags") or "#暮らし #買ってよかった"))
    for u in order:
        x = cand[u]
        rows.append((x["col"], x["name"], u, x["comment"], x["tag"]))
    log[T] = hand_urls + order
    out = [f"ROOM台本（機械が毎日そろえる。凪はこのページだけを見て、上から順に載せる）", "", f"更新：{T}", f"件数：{len(rows)}件", "",
           "・「更新：」の日付が今日の時だけ載せる。開くのは「探し方」のURLだけ。コメントとハッシュタグはそのまま貼る。",
           "・コレクションは、同じ名前があればそこへ。無ければ「新しく作る」の名前で作る（1日3つまで）。", "", "（ここから下に台本）", ""]
    for i, (col, nm, u, cm, tg) in enumerate(rows, 1):
        out += [f"{i}｜コレクション：{col}（無ければ 新しく作る：{col}）", f"商品：{nm}", f"探し方：{u}", "コメント：", cm, f"ハッシュタグ：{tg}", ""]
    out.append("（ROOM台本 ここまで）")
    open(P("notes", "room-daihon.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    json.dump(log, open(P("data", "room-log.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("room_auto", T, "件数", len(rows), "（燈が選んだ物", len(hand), "・機械", len(order), "）")


if __name__ == "__main__":
    main()
