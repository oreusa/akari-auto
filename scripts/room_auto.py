"""楽天ROOMの台本を、機械が毎日そろえる（notes/room-daihon.md）。11/11 月（オーナー「楽天roomとか…全部やれ」）。
それまで：夜の回が手で選ぶ → 古い商品で機械の確かめに落ちる（11/10 は9件中7件が×）・渡し忘れの夜は0件。
これから：その日の data/tanka.json（page.yml が楽天で取り直した、1個あたりで安い・レビュー4.0以上の物）から20件まで。
  ・燈が予定表 schedule/今日.json の room に入れた物があれば先頭に置く
  ・前の14日に台本へ出した物は出さない（data/room-log.json）
  ・同じ日に2回動いても同じ台本（朝7:30 と 夕18:30 の page.yml）
凪（GPT）は https://raw.githubusercontent.com/oreusa/akari-auto/main/notes/room-daihon.md を読む。"""
import json, os, re
from urllib.parse import quote
from datetime import datetime, timezone, timedelta, date

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
MAX = 100  # 11/13 19:35 オーナー「夜にももっと100倍楽天roomやれ」→ 40→100。比べた候補（tanka.json）が尽きたら前に出した物を古い順に足す。
# 前： 11/13 オーナー「gptまじ勿体ないからお金稼げるようにして」「月が使い込んでいいから」→ 1日20→40件。雫の3回と凪で上から続きを載せる
KEEP = 14
COL = {"毎日なくなる物": ("water", "soda", "rice", "tp", "tea", "coffee", "detergent", "softener", "shampoo", "bodysoap", "dish", "tissue", "trash", "pasta", "beans"),
       "赤ちゃん・ペットの毎日": ("diaper", "wipes", "dogfood", "catfood"),
       "そなえ": ("battery", "mask")}
FOR = {"water": "毎日飲む水を、重い買い物なしで届けてほしい家", "soda": "炭酸水を毎日飲む家", "rice": "お米をまとめて買っておきたい家", "tp": "トイレットペーパーを切らしたくない家",
       "tea": "お茶を箱で置いておきたい家", "coffee": "ボトルコーヒーを毎日飲む家", "detergent": "洗濯の回数が多い家", "softener": "柔軟剤を詰め替えで安く続けたい家",
       "shampoo": "シャンプーを詰め替えで続けたい家", "bodysoap": "ボディソープを家族で使う家", "dish": "食器用洗剤をまとめて置きたい家", "tissue": "ティッシュを箱で置いておきたい家",
       "trash": "ゴミ袋をまとめて買っておきたい家", "pasta": "パスタをよく作る家", "beans": "コーヒー豆を毎日ひく家", "diaper": "おむつを毎日たくさん使う家", "wipes": "おしりふきをまとめて置きたい家",
       "dogfood": "犬のごはんを切らしたくない家", "catfood": "猫のごはんを切らしたくない家", "battery": "乾電池をそなえておきたい家", "mask": "マスクを箱で置いておきたい家"}


STOP = ("送料無料", "ケース販売", "新米", "まとめ買い", "あす楽", "公式", "ポイント", "クーポン", "セット")


def room_search(nm, n=3):
    """11/13：GPTの画面では楽天市場の商品ページが「緊急メンテナンス」で開かない（夜が実物で確かめた）。ROOMの中の検索は開くので、探し方をそちらのURLにする。
    言葉は商品名の最初の3語（宣伝の言葉・【】・[]・数字だけの語は外す）。長いと出ない。"""
    nm = re.sub(r"【[^】]*】|\[[^\]]*\]|\([^)]*\)|（[^）]*）|[…●★☆]", " ", nm)
    ws = [w for w in nm.split() if w and not any(x in w for x in STOP) and not re.fullmatch(r"[\d.,xX×]+\S{0,3}", w)]
    ws = list(dict.fromkeys(ws))
    if n < 3 and len(ws) <= n: return ""  # 11/13：短い方の探し方は、言葉が3つ以上ある時だけ（同じURLを2回書かない）
    return "https://room.rakuten.co.jp/search/item?keyword=" + quote(" ".join(ws[:n]) or nm.strip()[:12])


RYOU = "毎日使う物なので、まとめ買いの候補に入れています。\n量・値段・在庫はお店と日によって変わるので、お店のページでご確認ください。"


def other(cm):
    """11/13：ROOMの中の検索では、台本と同じ店の商品が出ない事が多い（10件中6件）。同じ商品を別の店から載せる時は、店ごとに違う値段・レビューの数を抜いた文にする（違う数字を書かない）。"""
    m = re.search(r"この(.+?)は(.+?)あたり[\d,]+円（.+?時点）。レビューは[\d,]+件で★[\d.]+です。\n", cm)
    if not m: return ""
    return (cm[:m.start()] + f"この{m.group(1)}は、{m.group(2)}あたりの値段が安い方でした（比べたのは別のお店の値段です）。\n" + cm[m.end():]).replace("ただし、値段と在庫は日によって", "ただし、値段と在庫はお店と日によって")


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
            if not u.startswith("https://item.rakuten.co.jp/") or not bd or bd not in t.get("name", "") or (t.get("av") or 0) < 4.0 or (t.get("rc") or 0) < 20 or not t.get("per"):
                continue
            cm = (f"選んだ理由：{c['title']}を{c.get('read', 0)}点、{c['unit']}あたりの値段にそろえて比べました。この{bd}は{c['unit']}あたり{yen(t['per'])}円"
                  f"（{t['amt']}で{t['price']:,}円・{today.month}/{today.day}時点）。レビューは{t['rc']:,}件で★{t['av']:.2f}です。\n"
                  f"ただし、値段と在庫は日によって変わります。送料はお店のページでご確認ください。\n{FOR.get(c['key'], 'まとめて買っておきたい家')}に向いています。")
            cand[u] = {"url": u, "name": t["name"][:60] + f"（量：{t['amt']}）", "expect": bd, "comment": cm, "col": col, "tag": f"#{c['title'].split('（')[0]} #まとめ買い #1個あたりで比べた", "rank": i, "cat": c["key"]}
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
    # 11/12：まだ出していない物が20件に足りない日は、前に台本に出した物を古い順に足す（比べる物は30〜50点しか無く、14日出さない決まりだと3日目に0件になる。
    # 台本に出ても、メンテや時間切れでROOMに載っていない物が多い。もう載っている物は GPT が「載せ済み」で飛ばす）
    last = {}
    for d in sorted(log):
        if d != T:
            for u in log[d]:
                last[u] = d
    for u in sorted((u for u in cand if u in used and u not in order), key=lambda u: (last.get(u, ""), cand[u]["rank"])):
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
    # 11/13：GPTの自動審査が「新しいコレクションの完了」を止めて、載せられない商品が出た（雫 12:37）→ コレクションは作らせない
    out = [f"ROOM台本（機械が毎日そろえる。凪と雫はこのページだけを見て、上から順に載せる）", "", f"更新：{T}", f"件数：{len(rows)}件", "",
           "・「更新：」の日付が今日の時だけ載せる（朝の雫は、きのうの日付でも載せる）。開くのは「探し方」のURLだけ。コメントとハッシュタグはそのまま貼る。",
           "・「探し方」のURLは、ROOMの中の検索です（楽天市場の商品ページは開かない）。出てきた商品を上から20個まで見て、「商品：」の行と同じ商品（メーカー・商品の種類・1つの量・入っている数が同じ）の「コレ！」を押して載せる。",
           "・店の名前まで同じかは見なくてよい。同じ商品で店が違う時（店が分からない時も）は、コメントに「別の店の時のコメント：」の下の文を貼る。「訳あり」「中古」「お試し」と書いてある物は選ばない。",
           "・「探し方」で「該当する商品はありません」と出た時・同じ商品が20個の中に無い時は、「出ない時の探し方：」のURLを1回だけ開いて、同じように探す（その行が無い商品は、そのまま飛ばす）。",
           "・同じ商品が無く、同じメーカーの同じ種類で量や入っている数だけが違う物があれば、それを載せる（11/13 17:30 の雫は、これで15件を飛ばしていた）。その時のコメントは「量が違う時のコメント：」の下の文を貼る（値段の話を書かない）。別の種類の商品しか無ければ、載せずに飛ばす（報告に 飛ばした：番号）。",
           "・もうROOMに載っている商品は載せずに飛ばす（前の日に載せきれなかった物が、もう一度ここに出る）。",
           "・コレクションは、同じ名前があればそこへ。無ければ、新しく作らずに「毎日なくなる物」へ入れる。それも選べなければ、コレクションを選ばずに載せる（コレクションが無い・作れないことを理由に、載せるのをやめない）。", "", "（ここから下に台本）", ""]
    for i, (col, nm, u, cm, tg) in enumerate(rows, 1):
        out += [f"{i}｜コレクション：{col}（無ければ：毎日なくなる物）", f"商品：{nm}", f"探し方：{room_search(nm)}", *([f"出ない時の探し方：{room_search(nm, 2)}"] if room_search(nm, 2) else []), "コメント：", cm, f"ハッシュタグ：{tg}"] + (["別の店の時のコメント：", other(cm)] if other(cm) else []) + ["量が違う時のコメント：", RYOU] + [f"（{i}番 ここまで）", ""]
    out.append("（ROOM台本 ここまで）")
    # 11/13 オーナー「gptまじで使え」「楽天roomも本気でやらせろ」「もったいないぞ」→ 台本が終わって時間が残ったら、ROOMの中の検索で人気の物を足す（1回30件まで）
    out += ["", "■台本が終わって時間が残ったら（11/13〜・1回100件まで。11/13 19:35 オーナー「100倍やれ」）",
            "・下の言葉の「探し方」のURL（ROOMの中の検索）を上から開き、出てきた商品のうち、ふだん使う物を、1つの言葉で5件まで載せる。★とレビューの数が見える時は★4.0以上・レビュー100件以上の物。見えない時は、検索の上から順に選んでよい（11/13 17:30 の雫は、数字が確かめられず0件だった）。お酒・たばこ・薬・健康食品・美容の効き目をうたう物・大人向けの物は載せない。",
            "・コメントは次の形だけ（使った感想・「おすすめ」「最高」「買ってよかった」は書かない。見た数字だけ）：",
            "　数字が見えた時：「{商品の名前の短い形}。{月}/{日}に見た時点で{値段}円、レビューは{件数}件で★{点数}でした。値段と在庫は変わるので、お店のページでご確認ください。」",
            "　数字が見えない時：「{商品の名前の短い形}。毎日使う物なので、まとめ買いの候補に入れています。値段と在庫は変わるので、お店のページでご確認ください。」",
            "・ハッシュタグ：#{言葉} #日用品 #まとめ買い　コレクション：「毎日なくなる物」（無ければ選ばずに載せる）",
            "・もうROOMに載っている商品は飛ばす。報告の行に「人気から○件（言葉）」を足す。"]
    WORDS = ("トイレットペーパー", "ティッシュ", "洗濯洗剤", "柔軟剤", "食器用洗剤", "キッチンペーパー", "ラップ", "ゴミ袋", "ハンドソープ",
             "シャンプー 詰め替え", "ボディソープ 詰め替え", "歯ブラシ", "歯磨き粉", "マスク", "除菌シート", "おしりふき", "おむつ", "生理用品",
             "お米 10kg", "お米 5kg", "水 2L", "炭酸水", "お茶 ペットボトル", "コーヒー", "ドリップコーヒー", "紅茶", "カップラーメン", "パスタ",
             "レトルトカレー", "味噌汁 フリーズドライ", "納豆", "卵", "冷凍 餃子", "冷凍 うどん", "ナッツ", "プロテイン", "スープ", "ふりかけ",
             "猫砂", "キャットフード", "ドッグフード", "ペットシーツ", "カイロ", "加湿器", "電気毛布", "毛布", "こたつ", "ヒーター", "湯たんぽ",
             "靴下 冬", "手袋", "マフラー", "鍋", "鍋スープ", "土鍋", "おせち", "年賀状", "カレンダー 2027", "手帳 2027", "大掃除", "重曹",
             "クエン酸", "窓 掃除", "排水口 掃除", "カビ取り", "収納ケース", "ハンガー", "布団乾燥機", "ふるさと納税", "ブラックフライデー",
             "クリスマス お菓子", "お歳暮", "モバイルバッテリー", "充電器", "電池", "LED電球", "延長コード", "防災 保存水", "非常食", "懐中電灯")
    for w in WORDS:
        out.append(f"・{w}：探し方：{room_search(w)}")
    out.append("（追加 ここまで）")
    open(P("notes", "room-daihon.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    json.dump(log, open(P("data", "room-log.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("room_auto", T, "件数", len(rows), "（燈が選んだ物", len(hand), "・機械", len(order), "）")


if __name__ == "__main__":
    main()
