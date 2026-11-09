"""11/6 オーナーOK「見本4」→ くらべたおかいものリスト（/okaimono）を作り直す。

夜（テスター）の参考サイト調査の学び＋燈だけの工夫：
  ・最初の画面に答え（検索・よく買う8種類・「すべての種類」→ すぐ下に「最安」と「おすすめ」）
  ・「最安（全部から）」と「おすすめ（名の知れたメーカーの中で）」を別の見出しに（夜#3・#68）
  ・値段の横に送料込みの総額・お店の名前。比べた物・比べ方・更新・注意を答えのすぐ下に（夜#16・#17）
  ・条件ボタンに件数、「条件をぜんぶ外す」。条件はURLに残る（戻る・再読込でも消えない 夜#11）
  ・おむつはサイズ・テープ/パンツで同じ物だけ比べられる（夜#55）
  ・ボタンはその商品のページへ直接（夜#14）。数える件数は画面に出ている物だけ（夜#15）
  ・値段グラフに期間・単位・送料込み・更新、取れなかった日は線をつながない。グラフの点に商品名（夜#35）
  ・燈だけ：わが家のいつもの物（この端末に保存→次に来たら前に見た日からの値動き）、1か月にいくら？、値段ちがいの連絡
今までのページ（セール・宿・AIに聞く など）は /otoku に移して残す。
lifenote.py・okai_note.py のあとに動かす。失敗したら今のページのまま。"""
import html
import json
import os
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, "scripts"))
try:
    from tanka import BRAND, ALIAS
except Exception:
    BRAND, ALIAS = {}, {}
JST = timezone(timedelta(hours=9))
E = html.escape
SITE = os.path.join(R, "site")

NAME = {"water": "水", "soda": "炭酸水", "rice": "お米", "tp": "トイレットペーパー", "tea": "お茶", "coffee": "コーヒー",
        "detergent": "洗濯洗剤", "softener": "柔軟剤", "shampoo": "シャンプー", "bodysoap": "ボディソープ", "dish": "食器用洗剤",
        "tissue": "ティッシュ", "diaper": "おむつ", "wipes": "おしりふき", "trash": "ゴミ袋", "battery": "乾電池", "mask": "マスク",
        "pasta": "パスタ", "beans": "コーヒー豆", "dogfood": "ドッグフード", "catfood": "キャットフード"}
GROUPS = [("赤ちゃん", ["diaper", "wipes"]), ("紙・日用品", ["tp", "tissue", "trash", "mask", "battery"]),
          ("洗濯・お風呂・台所", ["detergent", "softener", "shampoo", "bodysoap", "dish"]),
          ("飲み物・食べ物", ["water", "tea", "soda", "coffee", "beans", "rice", "pasta"]), ("ペット", ["dogfood", "catfood"])]
POP = ["tissue", "tp", "diaper", "water", "detergent", "softener", "rice", "catfood"]
# 探す言葉（ひらがな・言いかえ）→ 種類
SYN = {"といれっとぺーぱー": "tp", "といぺ": "tp", "とイレ": "tp", "てぃっしゅ": "tissue", "はなかみ": "tissue", "おむつ": "diaper", "オムツ": "diaper",
       "おしりふき": "wipes", "おしり拭き": "wipes", "みず": "water", "天然水": "water", "ミネラルウォーター": "water", "たんさん": "soda",
       "炭酸": "soda", "こめ": "rice", "米": "rice", "おこめ": "rice", "新米": "rice", "おちゃ": "tea", "茶": "tea", "緑茶": "tea",
       "こーひー": "coffee", "珈琲": "coffee", "コーヒー豆": "beans", "豆": "beans", "せんざい": "detergent", "洗剤": "detergent",
       "洗濯": "detergent", "じゅうなん": "softener", "柔軟": "softener", "しゃんぷー": "shampoo", "ぼでぃそーぷ": "bodysoap",
       "ボディ": "bodysoap", "しょっき": "dish", "食器": "dish", "台所": "dish", "ごみ": "trash", "ゴミ": "trash", "ごみぶくろ": "trash",
       "でんち": "battery", "電池": "battery", "ますく": "mask", "ぱすた": "pasta", "スパゲッティ": "pasta", "ドッグ": "dogfood", "犬": "dogfood",
       "いぬ": "dogfood", "キャット": "catfood", "猫": "catfood", "ねこ": "catfood"}
# 1か月に使う量のボタン（その人が選ぶ。燈が決めつけない）。count=何個入りで数える物
USE = {"tissue": ("箱", [2, 5, 10], "count"), "tp": ("ロール", [4, 8, 16], "count"), "diaper": ("枚", [150, 210, 300], "q"),
       "wipes": ("枚", [200, 400, 800], "q"), "trash": ("枚", [30, 60, 120], "q"), "battery": ("本", [2, 4, 8], "q"),
       "mask": ("枚", [30, 60, 120], "q"), "water": ("L", [20, 40, 80], "q"), "soda": ("L", [5, 10, 20], "q"),
       "tea": ("L", [10, 20, 40], "q"), "coffee": ("L", [5, 10, 20], "q"), "beans": ("kg", [0.3, 0.5, 1], "q"),
       "rice": ("kg", [5, 10, 15], "q"), "pasta": ("kg", [1, 2, 3], "q"), "detergent": ("L・kg", [0.5, 1, 2], "q"),
       "softener": ("L・kg", [0.5, 1, 2], "q"), "shampoo": ("L・kg", [0.2, 0.4, 0.8], "q"), "bodysoap": ("L・kg", [0.3, 0.6, 1.2], "q"),
       "dish": ("L・kg", [0.2, 0.4, 0.8], "q"), "dogfood": ("kg", [2, 4, 8], "q"), "catfood": ("kg", [1, 2, 4], "q")}
PROMO = [r"【[^】]*】", r"\[[^\]]*\]", r"［[^］]*］", r"＼[^／]*／", r"《[^》]*》", r"『[^』]*』", r"\([^)]*(?:送料|地域|限定|倍|OFF|クーポン)[^)]*\)",
         r"ポイント(?:最大)?\d+(?:\.\d+)?倍", r"P\d+倍", r"エントリーで[^ 　]*", r"要エントリー", r"\d+%OFF\S*", r"\d+％OFF\S*", r"クーポン\S*",
         r"期間限定", r"数量限定", r"セール特別価格", r"送料無料\S*", r"送料込\S*", r"最安値\S*", r"楽天\S*1位\S*", r"ランキング\S*",
         r"\d+月\d+日\S*", r"\d+[/／]\d+\S*", r"…", r"\.\.\.", r"\d+日\d+時\S*", r"即納\S*", r"お買得！?", r"お得な", r"★", r"☆", r"◆[^◆]*◆", r"MA期間\S*",
         r"マラソン限定\S*", r"訳あり", r"並行輸入品", r"公式", r"!+", r"！+", r"レビュー[\d,]+件\S*", r"当選確率\S*", r"\d等\S*", r"LINE追加\S*", r"\d{1,2}:\d\d\S*", r"\S*迄", r"先着\S*", r"^[＆&\s]+"]


def clean(n):
    # 11/9 全文点検：お店の名前が「…バラ ケース販売 テ…」のように途中で切れている → 最後の切れた言葉を落とす
    cut = (n or "").rstrip().endswith(("…", "...", "‥"))
    n = re.sub(r"(…|\.\.\.|‥)\s*$", "", (n or "").rstrip())
    if cut and " " in n.strip():
        n = n.strip().rsplit(" ", 1)[0]
    for p in PROMO:
        n = re.sub(p, " ", n)
    n = re.sub(r"[｜|／/・]+\s*$", "", n)
    n = re.sub(r"\s+", " ", n).strip(" 　-〜~、,")
    if len(n) > 40:
        n = n[:40].rsplit(" ", 1)[0] if " " in n[:40] else n[:40]
    return re.sub(r"[\s\d]+$", "", n) if n else ""


def brand(key, t):
    if t.get("bd"):
        b = t["bd"]
    else:
        low = (t.get("name") or "").lower()
        b = next((x for x in BRAND.get(key, ()) if x.lower() in low), "")
        if not b:  # お店の名前が「〇〇公式」の時は、そのメーカー（11/6 アイリスオーヤマを数えていなかった）
            sh = t.get("shop") or ""
            b = next((x for x in BRAND.get(key, ()) + ("アイリスオーヤマ",) if x in sh and "公式" in sh), "")
    return ALIAS.get(b, b)


def tags(key, t):
    n = (t.get("name") or "") + " " + (t.get("amt") or "")
    out = []
    if key == "tissue":
        out.append("ソフトパック" if ("ソフトパック" in n or "詰め替え" in n) else "箱")
    elif key == "tp":
        if "ダブル" in n: out.append("ダブル")
        if "シングル" in n: out.append("シングル")
        if re.search(r"(1\.5|1\.6|2|3|4)倍", n): out.append("長持ち")
    elif key == "diaper":
        if "テープ" in n: out.append("テープ")
        if "パンツ" in n: out.append("パンツ")
        for s, lab in (("新生児", "新生児"), ("Sサイズ", "S"), ("Mサイズ", "M"), ("Lサイズ", "L"), ("ビッグ", "ビッグ"), ("BIG", "ビッグ")):
            if s in n and lab not in out: out.append(lab)
        if not any(x in out for x in ("新生児", "S", "M", "L", "ビッグ")):
            m = re.search(r"(?<![A-Za-z])(S|M|L)(?:サイズ)?(?![A-Za-z])", t.get("name") or "")
            if m: out.append(m.group(1))
    elif key in ("detergent", "softener", "shampoo", "bodysoap", "dish"):
        out.append("詰め替え" if re.search(r"詰め?替|つめかえ|業務用|\d{1,2}L(?![a-z])", n) else "本体")
        if re.search(r"無香|香りなし|微香", n): out.append("無香料・微香")
        if key == "detergent":
            if "粉" in n: out.append("粉")
            if "ジェルボール" in n: out.append("ジェルボール")
    elif key in ("water", "tea", "coffee", "soda"):
        m = re.search(r"(\d+(?:\.\d+)?)\s*(ml|mL|L|ℓ)", t.get("amt") or "")
        if m:
            v = float(m.group(1)) * (1 if m.group(2).lower() in ("l", "ℓ") else 0.001)
            out.append("2Lなど大きいボトル" if v >= 1.5 else "500mlなど小さいボトル" if v <= 0.7 else "1L前後")
        if key == "coffee" and "無糖" in n: out.append("無糖")
    elif key == "rice":
        if "無洗米" in n: out.append("無洗米")
        if "新米" in n: out.append("新米")
        m = re.match(r"(\d+)kg", t.get("amt") or "")
        if m: out.append(m.group(1) + "kg")
    elif key == "mask":
        for s in ("小さめ", "ふつう", "大きめ"):
            if s in n: out.append(s)
    elif key == "battery":
        for s in ("単3", "単4"):
            if s in n: out.append(s)
    if t["bd"]:
        out.append("名の知れたメーカー")
    return out


def amt_split(a):
    m = re.match(r"\s*([\d.]+\s*[^\d×x]+?)\s*[×x]\s*(\d+)", a or "")
    if m:
        return m.group(1).strip(), int(m.group(2))
    return (a or "").strip(), 1


def code(u):
    m = re.search(r"item\.rakuten\.co\.jp/([^/]+)/([^/?#]+)", u or "")
    return f"{m.group(1)}:{m.group(2)}" if m else ""


PREFS = "北海道 青森 岩手 宮城 秋田 山形 福島 茨城 栃木 群馬 埼玉 千葉 東京 神奈川 新潟 富山 石川 福井 山梨 長野 岐阜 静岡 愛知 三重 滋賀 京都 大阪 兵庫 奈良 和歌山 鳥取 島根 岡山 広島 山口 徳島 香川 愛媛 高知 福岡 佐賀 長崎 熊本 大分 宮崎 鹿児島 沖縄".split()
AREAS = "魚沼 南魚沼 会津 佐渡 岩船 庄内 津軽 伊賀 近江 丹波 但馬 淡路 十勝 富良野".split()


def origin(name):
    """名前の中の産地（県・地域）。県名は「◯◯県・◯◯産・◯◯米」の形だけ数える（京都・大阪は会社名にもあるため）"""
    got = set(a for a in AREAS if a in name)
    for pf in PREFS:
        if re.search(pf + r"(県|府|道|都|産|米)", name):
            got.add(pf)
    return "・".join(sorted(got))


def build():
    d = json.load(open(os.path.join(R, "data", "tanka.json"), encoding="utf-8"))
    try:
        hist = json.load(open(os.path.join(R, "data", "price-history.json"), encoding="utf-8")).get("codes", {})
    except Exception:
        hist = {}
    at = d.get("at", "")
    cats = []
    for c in d["cats"]:
        k = c["key"]
        if k not in NAME:
            continue
        offers = []
        for site, rows in (("楽天", c.get("top", [])), ("Yahoo!", c.get("yahoo", []))):
            for t in rows:
                if not t.get("per") or not t.get("price"):
                    continue
                url = t.get("url") or ""
                if site == "Yahoo!" and not url:  # 前の回のデータには行き先が無い → 押せない物は出さない
                    continue
                o = {"n": clean(t.get("name") or "") or NAME[k], "p": int(t["price"]), "u": round(float(t["per"]), 1), "a": t.get("amt") or "",
                     "s": t.get("shop") or "", "w": site, "av": t.get("av") or 0, "rc": t.get("rc") or 0, "url": url,
                     "img": t.get("img") or "", "bd": "", "og": origin(t.get("name") or "")}
                o["bd"] = brand(k, {**t, "bd": t.get("bd") or ""})
                if o["bd"] and o["bd"] not in o["n"]:
                    o["n"] = (o["bd"] + " " + o["n"])[:34]
                # 11/6 売上の調査 B2：「訳あり」を名前から消していたため、楽天で初めて知って帰る人がいた → 名前の頭に出す
                raw = t.get("name") or ""
                if ("訳あり" in raw or "わけあり" in raw or "訳アリ" in raw) and "訳あり" not in o["n"]:
                    o["n"] = "訳あり品 " + o["n"]
                    if len(o["n"]) > 38:  # 11/9 全文点検：「60個 バ」のように言葉の途中で切れていた → 言葉の切れ目で切る
                        o["n"] = o["n"][:38].rsplit(" ", 1)[0]
                o["one"], o["cnt"] = amt_split(o["a"])
                if c["unit"] == "1L・1kg":  # 夜#31 1Lか1kgかは商品ごと（量の書き方から）
                    o["ut"] = "1kgあたり" if re.search(r"\d\s*(kg|g)(?![a-z])", o["a"], re.I) else "1Lあたり"
                o["tg"] = tags(k, {**t, "bd": o["bd"]})
                cd = code(t.get("plain") or "")
                h = hist.get(cd, {}).get("p") if cd else None
                if h:
                    o["h"] = h
                offers.append(o)
        if not offers:
            continue
        # 同じ物が楽天とYahoo!にある時の印（メーカー＋量が同じ）
        for o in offers:
            # 11/8 夜#131：産地がちがう米を「同じ物」にしていた → 産地（県・地域）も同じ時だけ
            o["same"] = [i for i, x in enumerate(offers) if x is not o and o["bd"] and x["bd"] == o["bd"] and x["a"] == o["a"] and x["og"] == o["og"]]
        for o in offers:
            o.pop("og", None)
        amz = [{"n": clean(a.get("name") or ""), "url": a.get("url") or (f"https://www.amazon.co.jp/dp/{a['asin']}" if a.get("asin") else "")}
               for a in c.get("amazon", []) if a.get("asin") or a.get("url")]
        cats.append({"k": k, "nm": NAME[k], "unit": c["unit"], "seen": c.get("seen", 0), "read": c.get("read", 0), "ok": c.get("ok", 0),
                     "o": offers, "amz": amz, "use": USE.get(k)})
    return at, cats


CSS = """
body{background:#fff;color:#222;font-family:"Zen Kaku Gothic New",sans-serif;font-size:14px;line-height:1.6;margin:0}
.v4top{max-width:560px;margin:0 auto;padding:12px 16px;border-bottom:1px solid #E2E2E2}.v4top .en{display:block;font-size:10px;letter-spacing:.2em;color:#6E6E6E;text-decoration:none}.v4top b{font-family:"Shippori Mincho",serif;font-size:16px;font-weight:600}
.v4{max-width:560px;margin:0 auto;padding:0 0 96px}
.v4 h1{font-family:var(--min,"Shippori Mincho",serif);font-size:21px;line-height:1.45;margin:14px 16px 4px;font-weight:600}
.v4 .lead{font-size:12.5px;color:var(--sub,#555);margin:0 16px}
.v4 .pr{font-size:12px;color:#595959;text-align:right;margin:6px 16px 0}
.v4 .srch{margin:12px 16px 0;display:flex;border:1.5px solid var(--ink,#222);border-radius:12px;overflow:hidden;background:var(--card,#fff)}
.v4 .srch input{flex:1;min-width:0;border:0;padding:11px 12px;font:inherit;font-size:16px;background:transparent;color:inherit}
.v4 .srch button{border:0;background:var(--ink,#222);color:var(--inkfg,#fff);padding:0 16px;font:inherit;font-weight:700}
.v4 .read{margin:6px 16px 0;font-size:12.5px;color:var(--sub,#555)}
.v4 .read button{border:0;background:none;color:var(--lk,#2F5FA8);text-decoration:underline;font:inherit;padding:0}
.v4 .chs{margin:10px 16px 0}.v4 .chs p{font-size:11.5px;color:var(--mute,#6E6E6E);margin:8px 0 4px}
.v4 .ch{display:inline-block;border:1px solid var(--line,#E2E2E2);border-radius:99px;padding:5px 12px;font:inherit;font-size:13px;margin:0 4px 6px 0;background:var(--card,#fff);color:inherit;cursor:pointer}
.v4 .ch[aria-pressed=true]{background:var(--ink,#222);color:var(--inkfg,#fff);border-color:var(--ink,#222);font-weight:700}
.v4 .ch i{font-style:normal;font-family:Jost,sans-serif;opacity:.65;margin-left:3px}
.v4 .ch.all{border-color:var(--ink,#222);font-weight:700}
.v4 .ch:disabled{opacity:.4;cursor:default}
.v4 .hd{margin:14px 16px 0;padding-top:12px;border-top:1px solid var(--line,#E2E2E2)}
.v4 .hd h2{font-size:18px;margin:0}.v4 .hd h2 small{font-size:12px;font-weight:400;color:var(--mute,#6E6E6E);margin-left:6px}
.v4 .cl{font-size:12.5px;color:var(--sub,#555);margin:2px 16px 0;display:flex;justify-content:space-between;gap:8px}
.v4 .cl button{border:0;background:none;color:var(--lk,#2F5FA8);text-decoration:underline;font:inherit;padding:0}
.v4 .ans{margin:12px 16px 0;border:1.5px solid var(--ink,#222);border-radius:16px;overflow:hidden;background:var(--card,#fff)}
.v4 .ans section{padding:14px}.v4 .ans section+section{border-top:1px solid var(--line,#E2E2E2)}
.v4 .lab{display:inline-block;font-size:12px;font-weight:700;padding:2px 10px;border-radius:6px}
.v4 .lab small{font-weight:400;margin-left:4px}.v4 .lab.c{background:var(--gbg,#E8F4EE);color:var(--g,#1F7A4D)}.v4 .lab.r{background:var(--bbg,#E9EFF8);color:var(--b,#2F5FA8)}
.v4 .it{display:flex;gap:12px;margin-top:8px}.v4 .it img,.v4 .ph{width:84px;height:84px;object-fit:contain;border-radius:10px;background:#fff;border:1px solid var(--line,#E2E2E2);flex:none}
.v4 .nm{font-weight:700;line-height:1.45}
.v4 .attr span{display:inline-block;font-size:11.5px;background:var(--box,#F1F2F4);border-radius:4px;padding:0 6px;margin:4px 4px 0 0;color:var(--sub,#555)}
.v4 .pp{display:flex;align-items:baseline;gap:10px;margin-top:6px;flex-wrap:wrap}.v4 .pp .big{font-family:Jost,sans-serif;font-size:28px;font-weight:500}
.v4 .pp .tot{font-size:12.5px;line-height:1.5}
.v4 .why{font-size:12.5px;margin-top:6px;color:var(--sub,#555)}
.v4 .btn{display:block;margin-top:10px;text-align:center;background:var(--ink,#222);color:var(--inkfg,#fff)!important;border-radius:10px;padding:11px;font-weight:700;font-size:14px;text-decoration:none}
.v4 .sv{display:block;width:100%;margin-top:8px;border:1px solid var(--line,#E2E2E2);background:none;color:inherit;border-radius:10px;padding:9px;font:inherit;font-size:13px}
.v4 .mo b{font-size:13.5px}.v4 .mo .row2{display:flex;gap:8px;margin-top:6px;font-size:12.5px}
.v4 .mo .row2>div{flex:1;background:var(--box,#F1F2F4);border-radius:10px;padding:8px}.v4 .mo .row2 b.n{font-family:Jost,sans-serif;font-size:17px}
.v4 .ev{background:var(--box,#F1F2F4);padding:12px 14px;font-size:12.5px;line-height:1.75}.v4 .ev dt{font-weight:700;float:left;width:64px}.v4 .ev dd{margin:0 0 0 64px}
.v4 .ev a{color:var(--lk,#2F5FA8)}
.v4 h3{font-size:15px;margin:22px 16px 8px}.v4 h3 small{font-size:12px;font-weight:400;color:var(--mute,#6E6E6E);margin-left:6px}
.v4 .gr{margin:0 16px;border:1px solid var(--line,#E2E2E2);border-radius:12px;padding:12px;font-size:12.5px}.v4 .gr svg{display:block;width:100%;height:auto}
.v4 .lst{margin:0 16px;padding:0;list-style:none}.v4 .lst li{display:flex;gap:10px;padding:11px 0;border-bottom:1px solid var(--line,#E2E2E2)}
.v4 .lst a{display:flex;gap:10px;flex:1;color:inherit;text-decoration:none;min-width:0}
.v4 .lst .rk{width:18px;font-family:Jost,sans-serif;color:var(--mute,#6E6E6E);padding-top:2px;flex:none}
.v4 .lst img,.v4 .lst .ph{width:56px;height:56px}
.v4 .lst .r{text-align:right;min-width:92px;flex:none}.v4 .lst .r b{font-family:Jost,sans-serif;font-size:19px;font-weight:500}
.v4 .tag{white-space:nowrap;display:inline-block;font-size:11px;font-weight:700;padding:0 6px;border-radius:4px;margin-left:4px}
.v4 .na{margin:12px 16px 0;border:1px dashed var(--line,#CFCFCF);border-radius:12px;padding:10px 12px;font-size:12.5px;color:var(--sub,#555)}
.v4 .na a{color:var(--lk,#2F5FA8)}
.v4 .my{margin:12px 16px 0;border:1.5px solid var(--ink,#222);border-radius:14px;padding:12px 14px;background:var(--card,#fff)}
.v4 .my .r1{display:flex;justify-content:space-between;font-size:12px}.v4 .my .r1 b{font-size:14px}
.v4 .my a{display:flex;align-items:center;padding:8px 0;border-top:1px solid var(--line,#E2E2E2);margin-top:6px;color:inherit;text-decoration:none}
.v4 .my .up{font-size:12px;font-weight:700}
.v4 .zero{margin:12px 16px 0;padding:14px;border:1px solid var(--line,#E2E2E2);border-radius:12px;font-size:13px}
.v4 .more{margin:22px 16px 0;font-size:13px}.v4 .more a{color:var(--lk,#2F5FA8)}
.v4 .sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.v4 .n{font-family:Jost,sans-serif}.v4 .mut{color:var(--mute,#6E6E6E)}

.v4top{display:flex;flex-direction:column;align-items:center;text-align:center;border-bottom:0!important;padding:28px 16px 4px!important}
.v4top .en{font-family:Jost,sans-serif;font-size:10px!important;letter-spacing:5px!important;color:#7C8AA0!important}
.v4top b{font-size:25px!important;letter-spacing:3px;margin-top:6px;font-weight:500!important}
.v4 .pr{text-align:center!important;font-size:11px!important;margin:4px 16px 0!important}
.v4 #v4h h1{font-family:"Zen Kaku Gothic New",sans-serif!important;font-size:13.5px!important;font-weight:500!important;text-align:center;margin:8px 16px 0!important;color:#3F3833}
.v4 #v4h h1 br{display:none}
.v4 #v4h .lead{text-align:center;font-size:11.5px!important}
.v4 .kat{position:sticky;top:0;z-index:30;background:#fff;display:flex;gap:6px;overflow-x:auto;padding:9px 16px;margin:12px 0 0;border-bottom:1px solid #ECE8E4;scrollbar-width:none;-webkit-overflow-scrolling:touch}
.v4 .kat::-webkit-scrollbar{display:none}
.v4 .kat .ch{flex:none;margin:0;height:32px;padding:0 13px;border-color:#E2DED9}
.v4 .kat .ch[aria-pressed=true]{background:#fff;color:#2B2622;border:1.5px solid #2B2622}
.v4 .hd{border-top:0!important;padding-top:4px!important;display:flex;align-items:baseline;justify-content:space-between;gap:8px}
.v4 .hd h2{font-family:"Shippori Mincho",serif;font-size:21px!important;font-weight:600}
.v4 .hd .st{border:0;background:none;font:inherit;font-size:12.5px;color:#8C6A55;padding:4px 0;white-space:nowrap;cursor:pointer}
.v4 .chs{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;padding-bottom:2px}.v4 .chs::-webkit-scrollbar{display:none}
.v4 .chs .ch{flex:none;margin:0}
.v4 .kij{margin:6px 16px 0;font-size:11.5px;color:var(--mute,#6E6E6E)}
.v4 .v5l{margin:8px 16px 0}
.v4 .v5l li{display:block;padding:12px 0}
.v4 .v5l li.top{border:1.5px solid #1F7A4D;border-radius:14px;padding:12px;margin:4px 0 6px}
.v4 .v5l li.rec{border:1.5px solid #2F5FA8;border-radius:14px;padding:12px;margin:6px 0}
.v4 .v5l li.top+li,.v4 .v5l li.rec+li{border-top:0}
.v4 .v5l .lb{display:flex;gap:6px;margin-bottom:6px}
.v4 .v5l a{display:flex;gap:10px;align-items:flex-start}
.v4 .v5l .nm2{font-size:13.5px;font-weight:700;line-height:1.45;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.v4 .v5l .go{display:inline-block;margin-top:8px;font-size:12px;font-weight:700;border:1px solid #2B2622;border-radius:99px;padding:3px 12px}
.v4 .v5l li.top .go{background:#2B2622;color:#fff}
.v4 .v5l .r b{font-size:21px!important}
.v4 .kw{margin:16px 16px 0;border:1px solid var(--line,#E2E2E2);border-radius:14px;overflow:hidden}
.v4 .kw>summary{list-style:none;cursor:pointer;padding:13px 14px;font-weight:700;font-size:14px;display:flex;justify-content:space-between}
.v4 .kw>summary::-webkit-details-marker{display:none}
.v4 .kw>summary small{font-weight:400;font-size:12px;color:var(--mute,#6E6E6E)}
.v4 .kw>summary:after{content:"＋";color:#8C6A55}.v4 .kw[open]>summary:after{content:"－"}
.v4 .kw .mo{padding:0 14px 12px;display:block}
.v4 .kw h3{margin:14px 14px 6px!important}.v4 .kw .gr{margin:0 14px!important}
.v4 .kw .ev{margin:12px 0 0}

.v4 .hero{margin:10px 16px 0;border-radius:18px;background:#F3F7F4;padding:14px;position:relative}
.v4 .hero .bd{display:inline-block;background:#1F7A4D;color:#fff;font-size:12px;font-weight:700;border-radius:99px;padding:3px 12px;letter-spacing:.06em}
.v4 .hero .hx{display:flex;gap:14px;margin-top:10px;align-items:center}
.v4 .hero img,.v4 .hero .ph{width:118px;height:118px;border-radius:14px;background:#fff;object-fit:contain;flex:none;border:0}
.v4 .hero .pz{font-family:Jost,sans-serif;font-size:44px;font-weight:500;line-height:1;color:#1F7A4D}
.v4 .hero .pz small{font-size:14px;color:#3F3833;font-family:"Zen Kaku Gothic New",sans-serif;margin-left:2px}
.v4 .hero .nm3{font-size:13px;font-weight:700;line-height:1.45;margin-top:10px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.v4 .hero .sub{font-size:12px;color:#555;margin-top:4px}
.v4 .hero .buy{display:block;margin-top:12px;text-align:center;background:#1F7A4D;color:#fff!important;border-radius:12px;padding:13px;font-weight:700;font-size:15px;text-decoration:none}
.v4 .rec2{margin:10px 16px 0;border-radius:16px;background:#F1F5FB;padding:12px;display:flex;gap:12px;align-items:center;color:inherit;text-decoration:none}
.v4 .rec2 img,.v4 .rec2 .ph{width:72px;height:72px;border-radius:12px;background:#fff;object-fit:contain;flex:none;border:0}
.v4 .rec2 .bd{display:inline-block;background:#2F5FA8;color:#fff;font-size:11px;font-weight:700;border-radius:99px;padding:2px 10px}
.v4 .rec2 .pz{font-family:Jost,sans-serif;font-size:24px;color:#2F5FA8}
.v4 .gh{margin:22px 16px 8px;font-size:15px;font-weight:700}.v4 .gh small{font-weight:400;color:#6E6E6E;font-size:12px;margin-left:6px}
.v4 .grd{margin:0 16px;display:grid;grid-template-columns:1fr 1fr;gap:10px}
.v4 .grd a{display:flex;flex-direction:column;border:1px solid #ECE8E4;border-radius:14px;padding:10px;color:inherit;text-decoration:none;position:relative;background:#fff}
.v4 .grd img,.v4 .grd .ph{width:100%;height:auto;aspect-ratio:1;object-fit:contain;border-radius:10px;background:#fff;border:0}
.v4 .grd .rk2{position:absolute;top:8px;left:8px;background:#2B2622;color:#fff;font-family:Jost,sans-serif;font-size:12px;width:24px;height:24px;border-radius:50%;text-align:center;line-height:24px}
.v4 .grd .nm4{font-size:12.5px;font-weight:700;line-height:1.4;margin-top:8px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:35px}
.v4 .grd .pz{font-family:Jost,sans-serif;font-size:22px;margin-top:4px}.v4 .grd .pz small{font-size:11px;font-family:"Zen Kaku Gothic New",sans-serif}
.v4 .grd .sub{font-size:11px;color:#6E6E6E;line-height:1.5}
.v4 .grd .go2{margin-top:auto;padding-top:8px}.v4 .grd .go2 span{display:block;text-align:center;border:1px solid #2B2622;border-radius:99px;font-size:12px;font-weight:700;padding:5px}
"""

JS = r"""
(function(){
var D=JSON.parse(document.getElementById("v4d").textContent),C={},AT=D.at;D.cats.forEach(function(c){C[c.k]=c;});
var $=function(s){return document.querySelector(s)},main=$("#v4m"),qi=$("#v4q"),rd=$("#v4r");
function esc(x){return String(x==null?"":x).replace(/[<>&"']/g,function(c){return "&#"+c.charCodeAt(0)+";";});}
function yen(v){return v>=100?Math.round(v).toLocaleString():(Math.round(v*10)/10).toString();}
function nz(x){return (x||"").normalize("NFKC").toLowerCase().replace(/[\s　]/g,"").replace(/[ァ-ヶ]/g,function(c){return String.fromCharCode(c.charCodeAt(0)-96);});}
var st={k:"",c:[],u:1,p:0};
function load(){var p=new URLSearchParams(location.search);st.k=C[p.get("k")]?p.get("k"):"";st.c=(p.get("c")||"").split(",").filter(Boolean);st.u=+p.get("u")||1;st.p=+p.get("p")||0;}
function save(push){var p=new URLSearchParams();if(st.k)p.set("k",st.k);if(st.c.length)p.set("c",st.c.join(","));if(st.u!==1)p.set("u",st.u);if(st.p)p.set("p",st.p);
 var u=location.pathname+(p.toString()?"?"+p.toString():"");try{history[push?"pushState":"replaceState"](null,"",u);}catch(e){}}
function track(k){try{navigator.sendBeacon("/c?f=okaimono&s=v4&k="+encodeURIComponent(k));}catch(e){}}
var MY={};try{MY=JSON.parse(localStorage.getItem("okai_my")||"{}");}catch(e){}
function mysave(){try{localStorage.setItem("okai_my",JSON.stringify(MY));}catch(e){}}
/* 前に来た時の値段を「前に見た」にして、いまの値段を覚え直す（次に来た時は、今日からの値動き） */
(function(){var ch=0;Object.keys(MY).forEach(function(k){var c=C[k],o=MY[k];if(!c||!c.o.length||o.d===AT)return;var m=c.o.slice().sort(function(a,b){return a.u-b.u;})[0].u;o.pu=o.u;o.pd=o.d;o.u=m;o.d=AT;ch=1;});if(ch)mysave();})();
function pic(o,s){return o.img?'<img src="'+esc(o.img)+'" alt="'+esc(o.n)+'" width="'+s+'" height="'+s+'" loading="lazy" referrerpolicy="no-referrer" onerror="this.replaceWith(Object.assign(document.createElement(\'span\'),{className:\'ph\'}))">':'<span class="ph" aria-hidden="true"></span>';}
function attrs(c,o){var a=[];if(o.cnt>1){a.push("1個 "+o.one);a.push(o.cnt+"個入り");}else a.push(o.a);
 o.tg.forEach(function(t){if(t!=="名の知れたメーカー")a.push(t);});return '<div class="attr">'+a.map(function(x){return "<span>"+esc(x)+"</span>";}).join("")+"</div>";}
function rv(o){return +o.rc?'★'+o.av+'（レビュー'+(+o.rc).toLocaleString()+'件）':'レビューはまだありません';}
function unitTxt(c,o){return c.unit==="1L・1kg"?(o&&o.ut?o.ut:"1L・1kgあたり（商品ごと）"):c.unit+"あたり";}
function upd(){var m=/(\d{4})-(\d\d)-(\d\d) (\d\d:\d\d)/.exec(AT||"");return m?(+m[2])+"/"+(+m[3])+" "+m[4]:AT;}
function list(c){return c.o.filter(function(o){return (!st.p||o.p<=st.p)&&st.c.every(function(t){return o.tg.indexOf(t)>=0;});});}
function ctxt(){var a=st.c.slice();if(st.p)a.push("総額"+st.p.toLocaleString()+"円以下");return a;}
function buyBtn(o){return '<a class="btn" href="'+esc(o.url)+'" rel="sponsored noopener" target="_blank" data-k="v4:'+esc(o.n.slice(0,20))+'">この商品を'+esc(o.w)+'で見る</a>';}
function card(c,o,lab,why){return '<section><span class="lab '+(lab==="最安"?"c":"r")+'">'+lab+'<small>'+(lab==="最安"?(st.c.length||st.p?"この条件の中で":"全部の中で")+"・送料込み・"+unitTxt(c,o):"名の知れたメーカーの中で安い")+'</small></span>'+
 '<div class="it">'+pic(o,84)+'<div><div class="nm">'+esc(o.n)+'</div>'+attrs(c,o)+'</div></div>'+
 '<div class="pp"><span><b class="big">'+yen(o.u)+'</b>円<span style="font-size:12px">／'+unitTxt(c,o).replace("あたり","")+'</span></span><span class="tot">総額 <b class="n">'+o.p.toLocaleString()+'</b>円（送料込み）<br>'+esc(o.s)+'・'+esc(o.w)+'</span></div>'+
 '<div class="why">'+why+'</div>'+buyBtn(o)+'</section>';}
function months(c,o,u){var q=c.use;if(!q)return null;var cnt=q[2]==="count",tot=cnt?o.cnt:o.p/o.u,m=tot/u,per=cnt?o.p/o.cnt*u:o.u*u;return {m:m,per:per};}
function mtxt(x){var v=x.m>=2?Math.round(x.m):Math.round(x.m*10)/10;return "約"+v+"か月分"+(x.m<1?"（1か月に足りません）":"");}
function graph(c,o){if(!o||!o.h)return "";var ds=Object.keys(o.h).sort();if(ds.length<2)return "";
 var vs=ds.map(function(d){return o.h[d];}),mn=Math.min.apply(null,vs),mx=Math.max.apply(null,vs),lo=Math.floor(mn*0.9/100)*100,hi=Math.ceil(mx*1.1/100)*100;if(hi===lo)hi=lo+100;
 var d0=new Date(ds[0]),d1=new Date(ds[ds.length-1]),span=Math.max(1,(d1-d0)/864e5),X=function(d){return 44+((new Date(d)-d0)/864e5)/span*266;},Y=function(v){return 70-(v-lo)/(hi-lo)*60;};
 var seg=[],cur=[];ds.forEach(function(d,i){if(i&&(new Date(d)-new Date(ds[i-1]))/864e5>1.5){seg.push(cur);cur=[];}cur.push(X(d).toFixed(1)+","+Y(o.h[d]).toFixed(1));});seg.push(cur);
 var s='<svg viewBox="0 0 320 92" role="img" aria-label="'+esc(o.n)+'の値段（送料込み・楽天） '+ds.map(function(d){return (+d.slice(5,7))+"/"+(+d.slice(8))+" "+o.h[d].toLocaleString()+"円";}).join("、")+'">'+
  '<line x1="40" y1="10" x2="40" y2="70" stroke="currentColor" stroke-opacity=".2"/><line x1="40" y1="70" x2="315" y2="70" stroke="currentColor" stroke-opacity=".2"/>'+
  '<text x="0" y="14" font-size="10" fill="currentColor" opacity=".6">'+hi.toLocaleString()+'</text><text x="0" y="73" font-size="10" fill="currentColor" opacity=".6">'+lo.toLocaleString()+'</text>';
 seg.forEach(function(g){s+='<polyline fill="none" stroke="var(--b,#2F5FA8)" stroke-width="2.5" points="'+g.join(" ")+'"/>';});
 ds.forEach(function(d,i){s+='<circle cx="'+X(d).toFixed(1)+'" cy="'+Y(o.h[d]).toFixed(1)+'" r="3" fill="var(--b,#2F5FA8)"/>';if(i===0||i===ds.length-1||ds.length<=7)s+='<text x="'+(X(d)-10).toFixed(1)+'" y="88" font-size="10" fill="currentColor" opacity=".6">'+(+d.slice(5,7))+"/"+(+d.slice(8))+'</text>';});
 s+='</svg>';var a=vs[0],b=vs[vs.length-1],t=b<a?(a-b).toLocaleString()+"円下がりました":b>a?(b-a).toLocaleString()+"円上がりました":"値段の動きはありません";
 return '<h3>値段の動き<small>'+esc(o.n.slice(0,16))+'・総額・送料込み・楽天</small></h3><div class="gr">'+s+'<div>'+(+ds[0].slice(5,7))+"/"+(+ds[0].slice(8))+'から'+t+'（いまは <b class="n">'+b.toLocaleString()+'</b>円）。</div><div class="mut" style="font-size:11.5px">期間 '+ds[0].slice(5).replace("-","/")+'〜'+ds[ds.length-1].slice(5).replace("-","/")+'・1日1点（取れなかった日は線をつなぎません）・'+esc(upd())+' 更新</div></div>';}
function render(){
 document.querySelectorAll(".v4 [data-k2]").forEach(function(b){b.setAttribute("aria-pressed",b.dataset.k2===st.k?"true":"false");});
 /* 選んでいる種類を、横の列の見える所へ（ページは動かさない） */
 var kb=document.querySelector('.kat [aria-pressed="true"]');if(kb){var kt=kb.parentNode;kt.scrollLeft=Math.max(0,kb.offsetLeft-(kt.clientWidth-kb.offsetWidth)/2);}
 var c=C[st.k];if(!c){main.innerHTML='<p class="zero">上のボタンから、くらべたい物を選んでください。</p>';rd.innerHTML="";my();return;}
 var all=c.o,L=list(c).slice().sort(function(a,b){return a.u-b.u;}),tg={};
 /* 11/9 夜#148：1Lあたりと1kgあたりを同じ「安い順」にしない。多い方を先に出し、切りかえボタン */
 var UT={};L.forEach(function(o){if(o.ut)UT[o.ut]=(UT[o.ut]||0)+1;});var uts=Object.keys(UT).sort(function(a,b){return UT[b]-UT[a];});
 if(uts.length>1){if(uts.indexOf(st.ut)<0)st.ut=uts[0];L=L.filter(function(o){return o.ut===st.ut;});}all.forEach(function(o){o.tg.forEach(function(t){tg[t]=(tg[t]||0)+1;});});
 var h='<div class="hd"><h2>'+esc(c.nm)+'</h2><button type="button" class="st" id="v4s">'+(MY[c.k]?"★ いつもの物":"☆ いつもの物に入れる")+'</button></div>';
 var keys=Object.keys(tg).filter(function(t){return tg[t]<all.length||st.c.indexOf(t)>=0;});
 if(keys.length){h+='<div class="chs" role="group" aria-label="条件">'+keys.map(function(t){var on=st.c.indexOf(t)>=0,n=list({o:all.filter(function(o){return o.tg.indexOf(t)>=0;})}).length;
  return '<button type="button" class="ch" data-t="'+esc(t)+'" aria-pressed="'+on+'"'+(!on&&!n?" disabled":"")+'>'+esc(t)+'<i>'+(on?(tg[t]||0):n)+'</i></button>';}).join("")+(st.p?'<button type="button" class="ch" data-p="1" aria-pressed="true">総額'+st.p.toLocaleString()+'円以下 ×</button>':"")+'</div>';}
 else if(st.p)h+='<div class="chs"><button type="button" class="ch" data-p="1" aria-pressed="true">総額'+st.p.toLocaleString()+'円以下 ×</button></div>';
 var shops={};L.forEach(function(o){shops[o.s]=1;});
 var cx=ctxt();h+='<p class="cl"><span>'+(cx.length?"条件「"+esc(cx.join("・"))+"」：":"条件なし：")+'<b class="n">'+L.length+'</b>件（'+Object.keys(shops).length+'店）</span>'+(cx.length?'<button type="button" id="v4x">条件をぜんぶ外す</button>':"")+'</p>';
 if(c.k==="diaper"&&!st.c.some(function(t){return ["新生児","S","M","L","ビッグ"].indexOf(t)>=0;}))h+='<p class="cl" style="color:#B3261E">おむつはサイズで値段がちがいます。サイズ（新生児・S・M・L など）を選ぶと、同じサイズだけでくらべます。</p>';
 if(!L.length){var p0=st.p;st.p=0;var L2=list(c).slice().sort(function(a,b){return a.p-b.p;});st.p=p0;
  h+='<div class="zero">この条件に合う物は、いま比べた中にありません。'+(p0&&L2.length?'<br>値段の条件をのぞくと、総額がいちばん安い物は <b class="n">'+L2[0].p.toLocaleString()+'</b>円（'+esc(L2[0].a)+'）です。':'')+'<br><button type="button" class="ch" id="v4x2" style="margin-top:8px">条件をぜんぶ外す</button></div>';main.innerHTML=h;bind();my();return;}
 var ch=L[0],br=L.filter(function(o){return o.bd;})[0];
 /* 11/6 夜#55：おむつはサイズがちがう物を1つの「最安」にしない。サイズを選ぶまでは、サイズごとの最安を並べる */
 var SZ=["新生児","S","M","L","ビッグ"];
 if(c.k==="diaper"&&!st.c.some(function(t){return SZ.indexOf(t)>=0;})){
  h+='<div class="ans"><section><span class="lab c">サイズごとの最安<small>送料込み・1枚あたり</small></span><ol class="lst" style="margin:0">'+SZ.map(function(z){var o=L.filter(function(o){return o.tg.indexOf(z)>=0;})[0];if(!o)return "";
   return '<li><button type="button" class="ch" data-t="'+z+'" aria-pressed="false" style="flex:none;min-width:64px;align-self:center">'+z+'</button><div style="flex:1;min-width:0;font-size:13px">'+esc(o.n)+'<div class="mut" style="font-size:12px">'+esc(o.s)+'・'+esc(o.w)+'</div></div><div class="r"><b>'+yen(o.u)+'</b>円<span style="font-size:11px">／1枚</span></div></li>';}).join("")+
   '</ol><div class="why">サイズを押すと、そのサイズだけで最安とおすすめを出します。</div></section></div>';
  main.innerHTML=h;bind();my();return;}
 var K='';
 if(c.use){var q=c.use,uu=q[1].indexOf(st.u)>=0?st.u:q[1][1];
  var r1=months(c,ch,uu),r2=br&&br!==ch?months(c,br,uu):null;
  K+='<section class="mo"><b>1か月にいくら？</b><span class="mut" style="font-size:12px">　まとめ買いは何か月分か</span><div style="margin-top:6px"><span class="mut" style="font-size:12.5px">1か月に使う'+esc(q[0])+'　</span>'+
   q[1].map(function(v){return '<button type="button" class="ch" data-u="'+v+'" aria-pressed="'+(v===uu)+'">'+v+esc(q[0]==="L・kg"?"L":q[0])+'</button>';}).join("")+'</div><div class="row2">'+
   '<div><span class="lab c" style="font-size:11px">最安</span><br>'+esc(ch.cnt>1?ch.cnt+"個入り":ch.a)+'＝<b>'+mtxt(r1)+'</b><br>1か月 <b class="n">'+Math.round(r1.per).toLocaleString()+'</b>円</div>'+
   (r2?'<div><span class="lab r" style="font-size:11px">おすすめ</span><br>'+esc(br.cnt>1?br.cnt+"個入り":br.a)+'＝<b>'+mtxt(r2)+'</b><br>1か月 <b class="n">'+Math.round(r2.per).toLocaleString()+'</b>円</div>':"")+
   '</div><div class="why">使う量はご自分で選んでください。1か月の値段は、1個あたりの値段×使う量の目安です。</div></section>';}
 K+=graph(c,br&&br.h?br:ch.h?ch:null);
 var yN=c.o.filter(function(o){return o.w==="Yahoo!";}).length;
 K+='<dl class="ev"><dt>比べた物</dt><dd>楽天の送料込み'+c.seen.toLocaleString()+'件のうち、量が読めた'+c.read+'件から、条件に合う物をメーカー・お店ごとに選んだ'+c.o.filter(function(o){return o.w==="楽天";}).length+'件'+(yN?'と、Yahoo!の'+yN+'件':'')+'。'+(ctxt().length?'いまは条件に合う'+L.length+'件だけを出しています':'この下に全部あります')+'</dd>'+
  '<dt>比べ方</dt><dd>送料込みの値段 ÷ 量（'+unitTxt(c)+'）</dd><dt>更新</dt><dd>'+esc(upd())+'（1日2回）</dd>'+
  '<dt>注意</dt><dd>北海道・沖縄・離島は送料が別にかかることがあります。量は商品名から読んでいるので、買う前にお店のページで確かめてください。<br><a href="/koe?q='+encodeURIComponent("値段のちがい："+c.nm+" ")+'">お店の値段とちがったら教えてください →</a></dd></dl>';
 var ut=unitTxt(c,ch).replace("あたり","");
 if(uts.length>1)h+='<div class="chs" role="group" aria-label="量の単位">'+uts.map(function(u){return '<button type="button" class="ch" data-ut="'+esc(u)+'" aria-pressed="'+(u===st.ut)+'">'+esc(u.replace("あたり",""))+'あたりでくらべる<i>'+UT[u]+'</i></button>';}).join("")+'</div><p class="kij" style="margin-top:4px">液体（L）と粉・ジェル（kg）は、べつべつにくらべています。</p>';
 h+='<p class="kij">送料込みの値段 ÷ 量（'+esc(unitTxt(c))+'）でくらべています　'+esc(upd())+' 更新</p>';
 h+='<section class="hero"><span class="bd">'+(ctxt().length?'この条件でいちばん安い':'いちばん安い')+'</span><div class="hx">'+pic(ch,118)+'<div style="min-width:0"><div class="pz">'+yen(ch.u)+'<small>円／'+esc(ut)+'</small></div><div class="sub">総額 '+ch.p.toLocaleString()+'円（送料込み）<br>'+esc(ch.s)+'・'+esc(ch.w)+(+ch.rc?'　★'+ch.av:'')+'</div></div></div><div class="nm3">'+esc(ch.n)+'</div>'+attrs(c,ch)+
  '<a class="buy" href="'+esc(ch.url)+'" rel="sponsored noopener" target="_blank" data-k="v4:'+esc(ch.n.slice(0,20))+'">'+esc(ch.w)+'で見る ›</a></section>';
 if(br&&br!==ch)h+='<a class="rec2" href="'+esc(br.url)+'" rel="sponsored noopener" target="_blank" data-k="v4r:'+esc(br.n.slice(0,20))+'">'+pic(br,72)+'<div style="min-width:0;flex:1"><span class="bd">おすすめ</span><span style="font-size:11px;color:#555;margin-left:6px">名の知れたメーカーでいちばん安い'+(L.indexOf(br)>0?'・安い順で'+(L.indexOf(br)+1)+'番目':'')+'</span><div style="font-size:12.5px;font-weight:700;margin-top:4px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis">'+esc(br.n)+'</div><div><span class="pz">'+yen(br.u)+'</span>円／'+esc(unitTxt(c,br).replace("あたり",""))+'　<span style="font-size:11.5px;color:#555">'+esc(br.w)+'で見る ›</span></div></div></a>';
 else if(br===ch)h+='<p class="kij">いちばん安い物が、名の知れたメーカー（'+esc(ch.bd)+'）の物です。</p>';
 var R=L.filter(function(o){return o!==ch&&o!==br;});
 if(R.length){h+='<div class="gh">ほかの物も安い順に<small>'+R.length+'件</small></div><div class="grd">';
 R.forEach(function(o){var i=L.indexOf(o);var sm=o.same.map(function(j){return c.o[j];}).filter(function(x){return L.indexOf(x)>=0&&x.p<o.p;})[0];
  h+='<a href="'+esc(o.url)+'" rel="sponsored noopener" target="_blank" data-k="v4l:'+esc(o.n.slice(0,20))+'"><span class="rk2">'+(i+1)+'</span>'+pic(o,160)+'<div class="nm4">'+esc(o.n)+'</div><div class="pz">'+yen(o.u)+'<small>円／'+esc(unitTxt(c,o).replace("あたり",""))+'</small></div><div class="sub">総額 '+o.p.toLocaleString()+'円・送料込み<br>'+esc(o.s)+'・'+esc(o.w)+(sm?'<br><b style="color:#B3261E">同じ物が'+esc(sm.w)+'で'+(o.p-sm.p).toLocaleString()+'円安い</b>':'')+'</div><div class="go2"><span>'+esc(o.w)+'で見る ›</span></div></a>';});
 h+='</div>';}
 h+='<details class="kw"><summary><span>くわしく<br><small>'+(c.use?'1か月にいくら・':'')+'値段の動き・比べ方</small></span></summary>'+K+'</details>';
 h+='<div class="na"><b>順位に入れていない物</b><br>Amazon：送料込みの値段がお店のページでしか分からないため、順位に入れていません。'+(c.amz.length?'<br>'+c.amz.slice(0,2).map(function(a){return '<a href="'+esc(a.url)+'" rel="sponsored noopener" target="_blank">'+esc(a.n||c.nm)+'（Amazonで見る）</a>';}).join("<br>"):"")+'</div>';
 main.innerHTML=h;bind();my();
 /* 見た時の値段を覚える（いつもの物だけ。次に来た時の値動き用） */
 if(MY[c.k]&&!MY[c.k].now){}
}
function bind(){
 main.querySelectorAll("[data-t]").forEach(function(b){b.onclick=function(){var t=b.dataset.t,i=st.c.indexOf(t);if(i>=0)st.c.splice(i,1);else st.c.push(t);save();render();track("条件:"+t);var f=main.querySelector('[data-t="'+t+'"]');if(f)f.focus();};});
 main.querySelectorAll("[data-ut]").forEach(function(b){b.onclick=function(){st.ut=b.dataset.ut;render();};});
 main.querySelectorAll("[data-u]").forEach(function(b){b.onclick=function(){st.u=+b.dataset.u;save();render();var f=main.querySelector('[data-u="'+b.dataset.u+'"]');if(f)f.focus();};});
 ["v4x","v4x2"].forEach(function(id){var x=document.getElementById(id);if(x)x.onclick=function(){st.c=[];st.p=0;rd.innerHTML="";qi.value="";save();render();};});
 main.querySelectorAll("[data-p]").forEach(function(b){b.onclick=function(){st.p=0;rd.innerHTML="";save();render();};});
 var s=document.getElementById("v4s");if(s)s.onclick=function(){var c=C[st.k],L=list(c).slice().sort(function(a,b){return a.u-b.u;});
  if(MY[c.k])delete MY[c.k];else MY[c.k]={u:c.o.slice().sort(function(a,b){return a.u-b.u;})[0].u,d:AT};mysave();render();track("いつもの物:"+c.k);var f=document.getElementById("v4s");if(f)f.focus();};
}
function my(){var box=$("#v4my"),ks=Object.keys(MY).filter(function(k){return C[k];});if(!ks.length){box.hidden=true;$("#v4h").hidden=false;return;}
 box.hidden=false;$("#v4h").hidden=true;
 box.innerHTML='<div class="r1"><b>わが家のいつもの物</b><span class="mut">この端末だけに保存</span></div>'+ks.map(function(k){var c=C[k],m=c.o.slice().sort(function(a,b){return a.u-b.u;})[0],o=MY[k],bu=o.pu!=null?o.pu:o.u,df=bu-m.u,dd=/(\d{4})-(\d\d)-(\d\d)/.exec((o.pu!=null?o.pd:o.d)||"");
  var t=Math.abs(df)<0.05?'<span class="up mut">前に見た'+(dd?(+dd[2])+"/"+(+dd[3]):"時")+'から変わらず</span>':'<span class="up" style="color:'+(df>0?"var(--g,#1F7A4D)":"#B3261E")+'">前に見た'+(dd?(+dd[2])+"/"+(+dd[3]):"時")+'より'+yen(Math.abs(df))+'円'+(df>0?"安い":"高い")+'</span>';
  return '<a href="?k='+k+'" data-my="'+k+'"><div style="flex:1"><b>'+esc(c.nm)+'</b><div class="mut" style="font-size:11.5px">いちばん安い物の'+unitTxt(c)+'</div></div><div style="text-align:right"><span class="n" style="font-size:16px">'+yen(m.u)+'</span>円<div>'+t+'</div></div></a>';}).join("")+
  '<div class="mut" style="font-size:11.5px;margin-top:6px">1日2回とった値段（送料込み）とくらべています</div>';
 box.querySelectorAll("[data-my]").forEach(function(a){a.onclick=function(e){e.preventDefault();pick(a.dataset.my,true);};});}
function pick(k,push){st.k=k;st.c=[];st.u=1;st.p=0;save(push);render();var kb=document.querySelector('.kat [data-k2="'+k+'"]');if(kb)kb.scrollIntoView({block:"nearest",inline:"center"});track("種類:"+k);var hd=main.querySelector(".hd"),kt=document.querySelector(".kat");if(hd&&push)scrollTo(0,hd.getBoundingClientRect().top+scrollY-(kt?kt.offsetHeight:0)-6);}
document.querySelectorAll(".v4 [data-k2]").forEach(function(b){b.onclick=function(){pick(b.dataset.k2,true);var d=b.closest("details");if(d)d.open=false;};});
/* 探す：種類の名前・言いかえを読み取り、残りの言葉は条件ボタンに合わせる。読み取った結果を見せる */
var SYN=D.syn;
/* 11/6 夜#5・#69：値段（〇円以下）と、条件の言葉を、語順・助詞に関係なく読む。ほかの種類にある条件の言葉（無香料など）も条件として残し、無ければ「無い」と出す */
var PARTS=(function(){var m={},X={"無香料":"無香料・微香","無香":"無香料・微香","香りなし":"無香料・微香","2l":"2Lなど大きいボトル","大きいボトル":"2Lなど大きいボトル","500ml":"500mlなど小さいボトル","小さいボトル":"500mlなど小さいボトル","つめかえ":"詰め替え","詰替":"詰め替え","有名":"名の知れたメーカー","メーカー":"名の知れたメーカー"};Object.keys(X).forEach(function(k){m[nz(k)]=[X[k]];});D.cats.forEach(function(c){c.o.forEach(function(o){o.tg.forEach(function(t){[t].concat(t.split("・")).forEach(function(x){var n=nz(x);if(!n)return;if(!(n in m))m[n]=[];if(m[n].indexOf(t)<0)m[n].push(t);});});});});
 return Object.keys(m).sort(function(a,b){return b.length-a.length;}).map(function(n){return [n,m[n]];});})();
function ask(v){var raw=(v||"").normalize("NFKC"),lim=0,pm=/(\d[\d,]*)\s*円?\s*(以下|まで|以内|未満|より安い)/.exec(raw)||/(\d[\d,]*)\s*円/.exec(raw);
 if(pm){lim=+pm[1].replace(/,/g,"");raw=raw.replace(pm[0]," ");}
 var q=nz(raw);if(!q&&!lim){rd.innerHTML="";return;}var hit="",rest=q;
 D.cats.forEach(function(c){var n=nz(c.nm);if(!hit&&q.indexOf(n)>=0){hit=c.k;rest=q.replace(n," ");}});
 if(!hit)Object.keys(SYN).sort(function(a,b){return b.length-a.length;}).forEach(function(w){var n=nz(w);if(!hit&&q.indexOf(n)>=0&&C[SYN[w]]){hit=SYN[w];rest=q.replace(n," ");}});
 /* 11/9 夜#145：「ロイヤルカナン」など商品名・メーカー名でも探す。2つ以上の種類にあれば選んでもらう */
 if(!hit){var bk=[];D.cats.forEach(function(c){var w=q.replace(/\d+(kg|g|l|ml|個|本|枚|袋)/g,"").replace(/[のでがをはにとも、。・]/g,"");if(w.length>=3&&c.o.some(function(o){return nz(o.n).indexOf(w)>=0;}))bk.push(c.k);});
  if(bk.length===1){hit=bk[0];rest="";}
  else if(bk.length>1){rd.innerHTML='「'+esc(v)+'」は、'+bk.map(function(k){return '<button type="button" class="v4bk" data-bk="'+k+'">'+esc(C[k].nm)+'</button>';}).join("・")+'にあります。どちらを見ますか？';main.innerHTML="";
   rd.querySelectorAll("[data-bk]").forEach(function(b){b.onclick=function(){rd.innerHTML="";pick(b.dataset.bk,true);};});track("探す・名前:"+v);return;}}
 if(!hit&&st.k&&lim&&!q.replace(/[のでがをはにとも、。・]/g,""))hit=st.k;
 if(!hit){rd.innerHTML='「'+esc(v)+'」は、くらべている'+D.cats.length+'種類にありません。上の種類のボタンから選べます。<a href="/koe?q='+encodeURIComponent("比べてほしい："+v)+'">比べてほしい物を送る →</a>';main.innerHTML="";track("探す・なし:"+v);return;}
 var prev={k:st.k,c:st.c.slice(),u:st.u,p:st.p};st.k=hit;st.c=[];st.u=1;st.p=lim;var tg={};C[hit].o.forEach(function(o){o.tg.forEach(function(t){tg[t]=1;});});
 PARTS.forEach(function(x){var n=x[0],re=n.length===1?new RegExp("(^|[^0-9a-z])"+n+"(?![a-z])"):null,i=re?rest.search(re):rest.indexOf(n);if(i<0)return;
  var t=x[1].filter(function(t){return tg[t];})[0]||x[1][0];if(st.c.indexOf(t)<0)st.c.push(t);rest=re?rest.replace(re,"$1 "):rest.replace(n," ");});
 var miss=rest.trim().split(/\s+/).filter(function(w){w=w.replace(/^[のでがをはにとも、。・]+|[のでがをはにとも、。・]+$/g,"");return w&&!/^(安い|やすい|最安|おすすめ|買う|かう|ほしい|欲しい|激安|格安|まとめ買い|通販|商品|一番|いちばん|比較|くらべる|値段)$/.test(w);});
 /* 11/9 夜#145：猫砂→キャットフード、単4→単3のように、読めない言葉を外して別の物を出さない。本人に選んでもらう */
 if(miss.length){var want={k:st.k,c:st.c.slice(),p:st.p};st.k=prev.k;st.c=prev.c;st.u=prev.u;st.p=prev.p;
  rd.innerHTML='「'+esc(v)+'」の「'+esc(miss.join(" "))+'」は、いまくらべている物にありません。<br>近い物：<button type="button" id="v4alt">'+esc(C[want.k].nm)+'を見る</button>　<a href="/koe?q='+encodeURIComponent("比べてほしい："+v)+'">比べてほしい物を送る →</a>';
  main.innerHTML="";var al=document.getElementById("v4alt");if(al)al.onclick=function(){st.k=want.k;st.c=want.c;st.u=1;st.p=want.p;save(true);rd.innerHTML="";render();var hd=main.querySelector(".hd");if(hd)hd.scrollIntoView({block:"start"});};track("探す・読めない:"+v);return;}
 save(true);render();var cx=ctxt(),no=st.c.filter(function(t){return !tg[t];});
 rd.innerHTML='読み取った条件：種類＝<b>'+esc(C[hit].nm)+'</b>　条件＝'+(cx.length?esc(cx.join("・")):"なし")+(no.length?'<br>「'+esc(no.join("・"))+'」の'+esc(C[hit].nm)+'は、いま比べた中にありません':'')+(miss.length?'<br>「'+esc(miss.join(" "))+'」は読み取れなかったので外しました':'')+'　<button type="button" id="v4fx">直す</button>';
 var fx=document.getElementById("v4fx");if(fx)fx.onclick=function(){qi.focus();qi.select();};track("探す:"+v);
 var hd=main.querySelector(".hd");if(hd)hd.scrollIntoView({block:"start"});}
$("#v4f").onsubmit=function(e){e.preventDefault();ask(qi.value);};
window.addEventListener("popstate",function(){load();render();});
load();var q0=new URLSearchParams(location.search).get("q");if(q0){qi.value=q0;setTimeout(function(){ask(q0);},0);}
if(!st.k){var ks=Object.keys(MY).filter(function(k){return C[k];});st.k=ks[0]||"tissue";save();}render();
})();
"""


def page(at, cats, head):
    data = {"at": at, "cats": cats, "syn": SYN}
    total = sum(c["seen"] for c in cats)
    have = {c["k"] for c in cats}
    pop = "".join(f'<button type="button" class="ch" data-k2="{k}" aria-pressed="false">{E(NAME[k])}</button>' for k in POP if k in have)
    allb = "".join(f'<p>{E(g)}</p>' + "".join(f'<button type="button" class="ch" data-k2="{k}" aria-pressed="false">{E(NAME[k])}</button>' for k in ks if k in have) for g, ks in GROUPS)
    rest = "".join(f'<button type="button" class="ch" data-k2="{k}" aria-pressed="false">{E(NAME[k])}</button>' for g, ks in GROUPS for k in ks if k in have and k not in POP)
    m = re.match(r"(\d{4})-(\d\d)-(\d\d) (\d\d:\d\d)", at or "")
    up = f"{int(m.group(2))}/{int(m.group(3))} {m.group(4)}" if m else at
    body = f"""<header class="v4top"><a href="/" class="en">LIFE NOTE</a><b>くらべたおかいものリスト</b></header><script>/* 11/7 夜の調査：関西のTOWN NOTEから来た人に、もどる道（おかいものは1つ・入口は2つのHP） */(function(){{try{{var k="okai_from_tn";if(/townnote\\.pages\\.dev/.test(document.referrer)||/[?&]from=tn/.test(location.search))sessionStorage.setItem(k,"1");if(sessionStorage.getItem(k)!=="1")return;var h=document.currentScript.previousElementSibling,a=document.createElement("a");a.href="https://townnote.pages.dev/";var w=document.createElement("div");w.style.cssText="margin:8px 16px 0;padding:9px 12px;border:1px solid #E2E2E2;border-radius:10px;background:#F7F7F8;font-size:12.5px;line-height:1.6;color:#444";w.textContent="ここは TOWN NOTE の姉妹サイト「LIFE NOTE」の、くらべたおかいものリストです。";a.textContent="← 関西のTOWN NOTEにもどる";a.style.cssText="display:block;margin-top:4px;color:#8C6A55;font-weight:600;text-decoration:none";w.appendChild(a);h.insertAdjacentElement("afterend",w);}}catch(e){{}}}})();</script>
<main class="v4" role="main">
<p class="pr">リンクは広告（PR）です</p>
<div id="v4h"><h1>日用品を、送料込みの<br>1個あたりでくらべる</h1>
<p class="lead">{len(cats)}種類・{"楽天とYahoo!" if any(o["w"] == "Yahoo!" for c in cats for o in c["o"]) else "楽天"}の送料込み<b class="n">{total:,}</b>件から　<span class="n">{E(up)}</span> 更新</p></div>
<div class="my" id="v4my" hidden></div>
<form class="srch" id="v4f" role="search"><input id="v4q" type="search" placeholder="例：ダブルのトイレットペーパー" aria-label="くらべたい物を入れる（例：3000円以下のおむつ）" enterkeyhint="search"><button type="submit">くらべる</button></form>
<p class="read" id="v4r" aria-live="polite"></p>
<div class="chs kat" role="group" aria-label="くらべる種類">{pop}{rest}</div>
<div id="v4m" aria-live="polite"></div>
<p class="more">セール・ふるさと納税・宿の予約などのお得は <a href="/otoku">お得まとめ</a> にあります。</p>
<script type="application/json" id="v4d">{json.dumps(data, ensure_ascii=False).replace("</", "<\\/")}</script>
<noscript><p class="zero">このページは JavaScript を使います。<a href="/tanka">1個あたりの一覧</a>もご覧ください。</p></noscript>
</main>"""
    return f"""<!doctype html><html lang="ja"><head>{head}<style>{CSS}</style></head><body>{body}<script>{JS}</script></body></html>"""


OTOKU_JS = r"""
(function(){var f=document.getElementById("kqf"),q=document.getElementById("kq");if(!f)return;
var C=%s;function nz(x){return (x||"").normalize("NFKC").toLowerCase().replace(/[\s　]/g,"").replace(/[ァ-ヶ]/g,function(c){return String.fromCharCode(c.charCodeAt(0)-96);});}
f.onsubmit=function(e){e.preventDefault();var v=q.value.trim();if(!v)return;var n=nz(v),u;
 try{navigator.sendBeacon("/c?f=otoku&s=ask&k="+encodeURIComponent(v.slice(0,40)));}catch(x){}
 if(/ふるさと/.test(n))u="/furusato";else if(/(ぽっきり|まらそん|せーる|買いまわり|かいまわり)/.test(n))u="/kaimawari";else if(/(値下が|ねさが|安くなった)/.test(n))u="/nesage";else if(/(宿|ほてる|旅館|泊まり)/.test(n))u="/tomari";
 else u="/okaimono?q="+encodeURIComponent(v);location.href=u;};
if(location.hash==="#kq")setTimeout(function(){q.focus();},300);})();
"""


def otoku_page(old, head, cats):
    """11/6 夜#14・#15・#17・#68：古いページを丸ごと残すと、くらべる・値下がりと同じ物が別の答えで出る → お得まとめは、
    くらべる以外の入口（買う日の予定・マラソン・ふるさと・セール・宿）と「聞く」だけの短いページにする"""
    m = re.search(r'<ul class="ncal">(.*?)</ul>', old, re.S)
    lis = re.findall(r"<li[^>]*>.*?</li>", m.group(1), re.S) if m else []
    def key(li):
        if 'class="now"' in li:
            return (0, 0, 0)
        d = re.search(r"<span>(\d{1,2})/(\d{1,2})</span>", li)
        return (1, int(d.group(1)), int(d.group(2))) if d else (2, 0, 0)
    lis.sort(key=key)
    ent = re.search(r'<a class="ilk" href="https://event\.rakuten\.co\.jp/[^"]*"[^>]*>.*?</a>(<p class="ilks">.*?</p>)?', old, re.S)
    left = re.search(r"あと<b>(\d+)</b>日", old)
    h = head.replace("<title>日用品を送料込みの1個あたりでくらべる｜くらべたおかいものリスト｜LIFE NOTE</title>",
                     '<meta name="robots" content="noindex"><title>お得まとめ（セール・ふるさと納税・宿）｜くらべたおかいものリスト｜LIFE NOTE</title>')
    h = re.sub(r'<link rel="canonical"[^>]*>', "", h)
    h = re.sub(r'<meta property="og:url"[^>]*>', '<meta property="og:url" content="https://usagi-life-notes.pages.dev/otoku">', h)
    go = [("/okaimono", "くらべる", f"日用品{len(cats)}種類の最安とおすすめ"), ("/nesage", "買い時", "ふだんより安い物"),
          ("/kaimawari", "セール", "買いまわりの1,000円ぽっきり"),
          ("/furusato", "ふるさと納税", "寄付1万円あたりの量" + (f"・あと{left.group(1)}日" if left else "")),
          ("/tomari", "宿の予約", "遠くのおでかけと近くの宿")]
    cards = "".join(f'<a class="ok-c" href="{u}"><b>{E(t)}</b><small>{E(d)}</small><span aria-hidden="true">›</span></a>' for u, t, d in go)
    css = (".ok-c{display:flex;align-items:center;gap:4px 10px;flex-wrap:wrap;margin:10px 16px 0;padding:14px 16px;border:1px solid var(--line,#E2E2E2);border-radius:14px;color:inherit;text-decoration:none;background:var(--card,#fff)}"
           ".ok-c b{font-size:16px}.ok-c small{flex:1;font-size:12.5px;color:var(--sub,#555)}.ok-c span{font-size:20px;color:var(--mute,#6E6E6E)}"
           ".ok-cal{margin:8px 16px 0;padding:0;list-style:none;border:1px solid var(--line,#E2E2E2);border-radius:14px}.ok-cal li{display:grid;grid-template-columns:52px 1fr;gap:2px 12px;align-items:baseline;padding:11px 14px;border-top:1px solid var(--line,#E2E2E2)}.ok-cal li:first-child{border-top:0}"
           ".ok-cal span{width:52px;flex:none;font-size:12.5px;font-weight:700}.ok-cal li.now span{color:#B3261E}.ok-cal small{grid-column:2;display:block;font-size:12px;color:var(--sub,#555)}"
           ".ok-ent{display:block;margin:10px 16px 0;font-size:14px}.ok-ent .ilk{font-weight:700;color:inherit}.ok-ent .ilks{margin:2px 0 0;font-size:12px;color:var(--sub,#555)}")
    body = f"""<header class="v4top"><a href="/" class="en">LIFE NOTE</a><b>くらべたおかいものリスト</b></header><script>/* 11/7 夜の調査：関西のTOWN NOTEから来た人に、もどる道（おかいものは1つ・入口は2つのHP） */(function(){{try{{var k="okai_from_tn";if(/townnote\\.pages\\.dev/.test(document.referrer)||/[?&]from=tn/.test(location.search))sessionStorage.setItem(k,"1");if(sessionStorage.getItem(k)!=="1")return;var h=document.currentScript.previousElementSibling,a=document.createElement("a");a.href="https://townnote.pages.dev/";var w=document.createElement("div");w.style.cssText="margin:8px 16px 0;padding:9px 12px;border:1px solid #E2E2E2;border-radius:10px;background:#F7F7F8;font-size:12.5px;line-height:1.6;color:#444";w.textContent="ここは TOWN NOTE の姉妹サイト「LIFE NOTE」の、くらべたおかいものリストです。";a.textContent="← 関西のTOWN NOTEにもどる";a.style.cssText="display:block;margin-top:4px;color:#8C6A55;font-weight:600;text-decoration:none";w.appendChild(a);h.insertAdjacentElement("afterend",w);}}catch(e){{}}}})();</script>
<main class="v4" role="main"><p class="pr">リンクは広告（PR）です</p>
<h1>お得まとめ</h1><p class="lead">日用品の最安は「くらべる」に。ここは、セール・ふるさと納税・宿など、そのほかのお得の入口です。</p>
<h3>うさぎに聞く<small>探したい物を入れると、合うページを開きます</small></h3>
<form class="srch" id="kqf" role="search"><input id="kq" type="search" placeholder="例：3000円以下のおむつ" aria-label="探したい物を入れる" enterkeyhint="search"><button type="submit">探す</button></form>
<p class="read">入れた言葉は、くらべる種類を増やすために、言葉だけを数えています（名前などは残りません）。</p>
<h3>入口</h3>{cards}
<h3>買う日の予定<small>楽天</small></h3><ul class="ok-cal">{"".join(lis)}</ul>
<div class="ok-ent">{ent.group(0) if ent else ""}</div>
</main>"""
    js = OTOKU_JS % json.dumps({c["k"]: c["nm"] for c in cats}, ensure_ascii=False)
    return f"""<!doctype html><html lang="ja"><head>{h}<style>{CSS}{css}</style></head><body>{body}<script>{js}</script></body></html>"""


def main():
    at, cats = build()
    if len(cats) < 5:
        print("okai_v4: 種類が少ないので今のページのまま", len(cats))
        return
    src = os.path.join(SITE, "okaimono.html")
    old = open(src, encoding="utf-8").read()
    # 今までのページは /otoku に残す（セール・宿・AIに聞く など）
    def meta(pat):
        m = re.search(pat, old, re.S)
        return m.group(0) if m else ""
    head = ('<meta charset="utf-8">' + meta(r'<meta name="google-site-verification"[^>]*>') +
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<title>日用品を送料込みの1個あたりでくらべる｜くらべたおかいものリスト｜LIFE NOTE</title>'
            + meta(r'<link rel="canonical"[^>]*>') +
            '<meta name="description" content="ティッシュ・トイレットペーパー・おむつ・洗剤・水・お米など21種類を、楽天とYahoo!の送料込みの1個あたりでくらべて、最安と名の知れたメーカーのおすすめを毎日2回出しています。広告（PR）を含みます。">'
            + meta(r'<meta property="og:image"[^>]*>') + meta(r'<meta property="og:url"[^>]*>') +
            '<meta property="og:title" content="日用品を送料込みの1個あたりでくらべる｜くらべたおかいものリスト">'
            '<meta name="twitter:card" content="summary"><meta name="theme-color" content="#FFFFFF">'
            '<link rel="icon" href="logo.png"><link rel="apple-touch-icon" href="logo.png">'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=Jost:wght@400;500&display=swap">'
            + meta(r'<script src="/assets/night\.js[^"]*"></script>') + meta(r'<script src="/assets/menu\.js[^"]*"[^>]*></script>') +
            '<link rel="stylesheet" href="/assets/sub.css?v=4"><script src="/assets/v2sub.js?v=11" defer></script>')
    open(src, "w", encoding="utf-8").write(page(at, cats, head))
    open(os.path.join(SITE, "otoku.html"), "w", encoding="utf-8").write(otoku_page(old, head, cats))
    print("okai_v4:", len(cats), "種類", sum(len(c["o"]) for c in cats), "件")


if __name__ == "__main__":
    main()
