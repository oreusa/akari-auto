"""「1個あたりで比べた」ページ（site/tanka.html）と data/tanka.json を作る。

11/1 オーナー「すごいって思わせてないと買われない」「数が多ければいいってもんじゃない」。
人が手でできない比べ方＝楽天の送料込みの商品を毎回100件以上取り、商品名から量（ml・本・kg・ロール・m）を読んで
「1Lあたり」「1kgあたり」「100mあたり」に直し、レビュー1,000件以上・★4.0以上の中で安い順に並べる。
量がはっきり読めない物（24本・48本を選ぶ物など）は比べない＝数字をまちがえない。
data/tanka.json は夜の回が投稿に使う（「楽天の水◯件を1Lあたりで比べたら1位は◯円」）。page.yml で毎回作る。
"""
import html
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))
import lib  # noqa: E402

JST = timezone(timedelta(hours=9))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://usagi-life-notes.pages.dev"
PAGE = "tanka"
WEEK = "月火水木金土日"
PAGES = 4  # 1つの物で 30件×4ページ＝最大120件
TOP = 5

NUM = r"(\d+(?:\.\d+)?)"
MUST = {"soda": "炭酸", "tp": "トイレット", "rice": "米", "tea": "茶", "coffee": ("コーヒー", "珈琲", "BOSS", "ブラック"), "detergent": "洗剤",
        "softener": ("柔軟剤", "柔軟仕上げ"), "shampoo": "シャンプー", "bodysoap": ("ボディソープ", "ボディーソープ", "ボディウォッシュ"),
        "dish": "食器", "tissue": "ティッシュ", "diaper": ("メリーズ", "ムーニー", "オヤスミマン", "パンパース", "グーン", "マミーポコ", "GENKI", "ナチュラルムーニー"), "wipes": ("おしり",),
        "trash": "袋", "battery": ("単3", "単三"), "mask": "マスク", "pasta": ("パスタ", "スパゲッティ", "スパゲティ"), "protein": "プロテイン",
        "beans": ("豆", "コーヒー", "珈琲"), "dogfood": ("ドッグフード", "犬", "ドッグ"), "catfood": ("キャットフード", "猫", "キャット")}


# 11/4 オーナーの奥さんがお買い物リストを使った感想「知らないメーカーが上位だと、そりゃ安いだろと思って買う気にならない。
# おしりふきならムーニーやパンパースが無い」→ 名の知れたメーカー（下の BRAND）の物を先に、その中で安い順に並べる。
# 名の知れた物が3つに足りない時だけ、そのメーカー名で楽天をもう1回ずつ探し、それでも足りなければ他の物で埋める。
BRAND = {
    "water": ("サントリー", "いろはす", "い・ろ・は・す", "エビアン", "evian", "ボルヴィック", "volvic", "クリスタルガイザー", "アルカリイオンの水", "森の水だより", "六甲のおいしい水", "キリン", "アサヒ", "伊藤園", "コカ・コーラ"),
    "soda": ("ウィルキンソン", "WILKINSON", "サントリー", "アサヒ", "キリン", "ペリエ", "サンペレグリノ", "伊藤園", "アイリスオーヤマ", "VOX"),
    "rice": ("コシヒカリ", "あきたこまち", "ひとめぼれ", "ななつぼし", "ゆめぴりか", "つや姫", "はえぬき", "ヒノヒカリ", "青天の霹靂", "雪若丸", "ミルキークイーン", "さがびより", "にこまる", "まっしぐら", "ふさこがね"),
    "tp": ("エリエール", "スコッティ", "ネピア", "クリネックス", "シャワートイレ", "アイリスオーヤマ"),
    "tea": ("伊藤園", "お〜いお茶", "お～いお茶", "おーいお茶", "綾鷹", "伊右衛門", "生茶", "サントリー", "キリン", "アサヒ", "十六茶", "爽健美茶", "からだすこやか茶", "健康ミネラルむぎ茶", "コカ・コーラ"),
    "coffee": ("BOSS", "ボス", "ジョージア", "GEORGIA", "UCC", "ワンダ", "ファイア", "キーコーヒー", "ドトール", "スターバックス", "AGF", "ネスカフェ", "ブレンディ", "クラフトボス"),
    "detergent": ("アタック", "アリエール", "ボールド", "トップ", "ナノックス", "さらさ", "ライオン", "花王", "P&G"),
    "softener": ("レノア", "ハミング", "ソフラン", "フレア", "ダウニー", "ファーファ", "花王", "ライオン", "P&G"),
    "shampoo": ("パンテーン", "いち髪", "TSUBAKI", "メリット", "ラックス", "LUX", "エッセンシャル", "ボタニスト", "BOTANIST", "ダイアン", "ハーバルエッセンス", "h&s", "スカルプD", "&honey", "アンドハニー", "ディアボーテ", "花王", "資生堂", "ミノン"),
    "bodysoap": ("ビオレ", "ダヴ", "Dove", "ナイーブ", "ミノン", "牛乳石鹸", "カウブランド", "ボタニスト", "BOTANIST", "ミューズ", "hadakara", "ハダカラ", "花王", "ライオン"),
    "dish": ("ジョイ", "JOY", "キュキュット", "チャーミー", "ファミリーフレッシュ", "マジカ", "花王", "ライオン", "P&G"),
    "tissue": ("エリエール", "スコッティ", "ネピア", "クリネックス", "鼻セレブ", "アイリスオーヤマ"),
    "diaper": ("メリーズ", "ムーニー", "オヤスミマン", "パンパース", "グーン", "マミーポコ", "GENKI", "ナチュラルムーニー"),
    "wipes": ("ムーニー", "パンパース", "メリーズ", "グーン", "マミーポコ", "ピジョン", "Pigeon", "ネピア", "和光堂", "GENKI", "ユニ・チャーム", "ユニチャーム", "大王製紙"),
    "trash": ("サニパック", "ジャパックス", "アイリスオーヤマ", "ケミカルジャパン", "日泉", "オルディ"),
    "battery": ("パナソニック", "Panasonic", "エボルタ", "富士通", "FDK", "東芝", "TOSHIBA", "マクセル", "maxell", "三菱", "デュラセル", "Duracell", "アイリスオーヤマ"),
    "mask": ("ユニ・チャーム", "ユニチャーム", "超快適", "超立体", "アイリスオーヤマ", "白元", "快適ガード", "ハクゾウ", "興和", "三次元"),
    "pasta": ("マ・マー", "ママー", "ディ・チェコ", "ディチェコ", "DE CECCO", "バリラ", "Barilla", "ボルカノ", "日清"),
    "protein": ("ザバス", "SAVAS", "マイプロテイン", "MYPROTEIN", "ゴールドスタンダード", "ビーレジェンド", "be LEGEND", "グロング", "GronG", "エクスプロージョン", "X-PLOSION", "DNS", "VALX", "バルクス"),
    "beans": ("UCC", "キーコーヒー", "KEY COFFEE", "ドトール", "スターバックス", "澤井珈琲", "小川珈琲", "カルディ", "AGF"),
    "dogfood": ("ロイヤルカナン", "ヒルズ", "サイエンス・ダイエット", "サイエンスダイエット", "ピュリナ", "ニュートロ", "ペディグリー", "ビタワン", "ユニ・チャーム", "愛犬元気", "グラン・デリ", "アイムス", "モグワン", "カナガン", "ブッチ"),
    "catfood": ("ロイヤルカナン", "ヒルズ", "サイエンス・ダイエット", "サイエンスダイエット", "ピュリナ", "ニュートロ", "カルカン", "モンプチ", "ねこ元気", "銀のスプーン", "アイシア", "オールウェル", "フリスキー", "アイムス", "モグニャン", "カナガン"),
}
BRAND_MIN = 3  # 名の知れた物がこれより少ない時だけ、メーカー名で探し足す
BRAND_ASK = 3  # 探し足すメーカーは前から3つまで（楽天APIを使いすぎない）


# 11/6 夜「ジョイとJOYを別のメーカーのように数える」→ 書き方がちがうだけの名前は1つにそろえる
ALIAS = {"JOY": "ジョイ", "WILKINSON": "ウィルキンソン", "ボス": "BOSS", "クラフトボス": "BOSS", "GEORGIA": "ジョージア", "LUX": "ラックス",
         "BOTANIST": "ボタニスト", "Dove": "ダヴ", "Panasonic": "パナソニック", "エボルタ": "パナソニック", "TOSHIBA": "東芝", "maxell": "マクセル",
         "Duracell": "デュラセル", "Pigeon": "ピジョン", "ユニチャーム": "ユニ・チャーム", "サイエンス・ダイエット": "ヒルズ", "サイエンスダイエット": "ヒルズ",
         "ディチェコ": "ディ・チェコ", "DE CECCO": "ディ・チェコ", "Barilla": "バリラ", "ママー": "マ・マー", "KEY COFFEE": "キーコーヒー",
         "evian": "エビアン", "volvic": "ボルヴィック", "い・ろ・は・す": "いろはす", "お〜いお茶": "伊藤園", "お～いお茶": "伊藤園", "おーいお茶": "伊藤園",
         "SAVAS": "ザバス", "MYPROTEIN": "マイプロテイン", "GronG": "グロング", "X-PLOSION": "エクスプロージョン", "be LEGEND": "ビーレジェンド",
         "バルクス": "VALX", "ハダカラ": "hadakara", "アンドハニー": "&honey", "カウブランド": "牛乳石鹸", "ナチュラルムーニー": "ムーニー", "オヤスミマン": "ムーニー"}


def brand_of(key, name):
    """名の知れたメーカーなら、その名前（大文字小文字は見ない）。書き方ちがいは ALIAS で1つに。"""
    low = name.lower()
    b = next((b for b in BRAND.get(key, ()) if b.lower() in low), "")
    return ALIAS.get(b, b)


def brand_first(key, rows, n):
    """名の知れたメーカーの物を先に（その中で安い順）、足りない分だけ他の物で埋める。rows は安い順。"""
    a = [r for r in rows if r.get("bd")]
    return (a + [r for r in rows if r not in a])[:n]


def must_ok(key, name):
    """名前に必ずある言葉（どれか1つ）。検索で別の物が混ざるため。"""
    m = MUST.get(key)
    if not m:
        return True
    return any(w in name for w in ((m,) if isinstance(m, str) else m))


# 11/3 楽天で調べたら、洗剤・おむつ・ペットフードなどはレビュー1,000件の物がほとんど無い（1商品のレビューが散らばる）。
# 水・お米などの4つは今まで通り1,000件、足した物は100件以上・★4.0以上（カードにレビュー数をそのまま出す）
RMIN = {"water": 1000, "soda": 1000, "rice": 1000, "tp": 1000,
        # 洗剤・おむつなどは1商品のレビューが特に少ない（11/3 楽天で見たら多くて50件ほど）
        "detergent": 20, "softener": 20, "bodysoap": 20, "dish": 20,
        # おむつのケース売りは楽天でレビューがほぼ0件（11/3）→ レビューでしぼらず、大手の名前（MUST）の物だけにする
        "diaper": 0,
        "coffee": 50, "trash": 50, "pasta": 50, "battery": 50, "tissue": 50, "wipes": 50, "tea": 50}
RMIN_NEW = 100
NGKW = "ふるさと 定期便 お試し サンプル"  # 楽天の検索で先に外す（30件の枠を使わない）
NG = ("ふるさと", "定期", "お試し", "サンプル")
KIND = {"tea": "vol", "coffee": "vol", "detergent": "vol", "softener": "vol", "shampoo": "vol", "bodysoap": "vol", "dish": "vol",
        "tissue": "kumi", "diaper": "pcs", "wipes": "pcs", "trash": "pcs", "mask": "pcs", "battery": "hon",
        "pasta": "wt", "protein": "wt", "beans": "wt", "dogfood": "wt", "catfood": "wt"}
EXTRAQ = {"softener": ("無香料",), "detergent": ("無香料", "ジェルボール"), "dish": ("無香料",), "bodysoap": ("無添加",),
          "diaper": ("パンツ L", "パンツ ビッグ", "テープ 新生児", "テープ S"), "tp": ("シングル",), "tissue": ("箱",)}
NEWPAGES = 2  # 足した物は 30件×2ページ（楽天APIを使いすぎない）  # 名前に必ずある言葉（検索で別の物が混ざるため）
# key, 見出し, 検索の言葉, ジャンル, 単位, 入れない言葉, 1単位のありえる値段の幅
CATS = [
    ("water", "水（ミネラルウォーター）", "水 天然水 ミネラルウォーター", "100316", "1L",
     ("炭酸", "茶", "サーバー", "定期", "コーヒー", "ジュース", "スポーツ", "ふるさと"), (15, 400)),
    ("soda", "炭酸水", "炭酸水 強炭酸", "100316", "1L",
     ("サーバー", "定期", "ジュース", "コーラ", "ふるさと", "茶"), (20, 500)),
    ("rice", "お米", "米 精米 kg", "100227", "1kg",
     ("ふるさと", "定期", "雑穀", "もち米", "玄米", "パック", "レトルト", "無洗米ではない"), (200, 2500)),
    ("tp", "トイレットペーパー", "トイレットペーパー ロール まとめ買い", "", "100m",
     ("ふるさと", "定期", "ホルダー", "ケース", "収納", "ラック"), (5, 200)),
] + [
    # 11/3 オーナー「もっと比べさせろ。項目もっとあるだろ。ここが運営資金」→ 毎日使う物を一気に足す。
    # 量の読み方は KIND（vol＝ml×本、wt＝g/kg×袋、pcs＝枚、hon＝本、kumi＝ティッシュの組×箱）。読めない物は比べない（数字をまちがえない）
    (k, t, q, "", u, NG + ng, rg) for k, t, q, u, ng, rg in [
        ("tea", "お茶（ペットボトル）", "お茶 ペットボトル 緑茶 ケース", "1L", ("紅茶", "ティーバッグ", "茶葉", "粉末", "パウダー"), (30, 500)),
        ("coffee", "コーヒー（ボトル）", "コーヒー ペットボトル 無糖 ケース", "1L", ("豆", "粉", "ドリップ", "インスタント", "カプセル"), (50, 800)),
        ("detergent", "洗濯洗剤（詰め替え）", "洗濯洗剤 詰め替え 超特大", "1L・1kg", ("粉", "シート", "ジェルボール", "柔軟剤"), (100, 3000)),
        ("softener", "柔軟剤（詰め替え）", "柔軟剤 詰め替え 超特大", "1L・1kg", ("洗濯洗剤", "シート", "ビーズ", "せっけん", "石けん", "石鹸", "柔軟剤不要", "柔軟剤いらず", "柔軟剤なし", "洗濯用"), (100, 3000)),  # 11/9 夜#158：柔軟剤のランキングに洗濯せっけん（柔軟剤不要）が入っていた
        ("shampoo", "シャンプー（詰め替え）", "シャンプー 詰め替え 大容量", "1L・1kg", ("トリートメント", "プレシャンプー", "ボディソープ", "全身", "ボディ", "ディスペンサー", "ボトル", "容器", "アダプター", "ホルダー", "ケース"), (200, 8000)),
        ("bodysoap", "ボディソープ（詰め替え）", "ボディソープ 詰め替え 大容量", "1L・1kg", ("固形", "石鹸 個", "ディスペンサー", "ボトル", "容器", "アダプター", "スクラブ", "シャンプー"), (100, 5000)),
        ("dish", "食器用洗剤（詰め替え）", "食器用洗剤 詰め替え 大容量", "1L・1kg", ("食洗機", "タブレット", "粉", "ディスペンサー", "自動", "ボトル"), (100, 3000)),
        ("tissue", "ティッシュ", "ティッシュペーパー まとめ買い", "100組", ("ウェット", "トイレット", "ティッシュケース", "カバー", "ポケット", "ペーパータオル"), (2, 200)),
        ("diaper", "おむつ", "おむつ ケース 枚 ベビー", "1枚", ("大人", "介護", "ペット", "防水シート", "パッド", "ストッカー", "ポーチ", "巾着", "収納", "バッグ", "おしりふき", "処理"), (10, 200)),
        ("wipes", "おしりふき", "おしりふき まとめ買い", "1枚", ("手口", "手・口", "除菌", "おむつ", "ケース単体", "フタ", "ペット", "おしり拭きケース"), (0.3, 15)),
        ("trash", "ゴミ袋", "ゴミ袋 45L 枚", "1枚", ("ゴミ箱", "ホルダー", "スタンド"), (1, 60)),
        ("battery", "乾電池（単3）", "単3 乾電池 アルカリ", "1本", ("充電器", "単4", "単四", "ケース", "ホルダー", "充電池"), (15, 400)),
        ("mask", "マスク", "マスク 不織布 枚", "1枚", ("ケース", "ストラップ", "ホルダー", "シートマスク", "パック"), (1, 120)),
        ("pasta", "パスタ", "パスタ スパゲッティ kg", "1kg", ("ソース", "レトルト", "冷凍", "マシン"), (150, 3000)),
        ("protein", "プロテイン", "プロテイン ホエイ kg", "1kg", ("バー", "シェイカー", "ドリンク 本"), (1000, 15000)),
        ("beans", "コーヒー豆", "コーヒー豆 kg 焙煎", "1kg", ("ドリップバッグ", "インスタント", "ミル", "カプセル"), (800, 15000)),
        ("dogfood", "ドッグフード", "ドッグフード ドライ kg", "1kg", ("おやつ", "ウェット", "缶", "パウチ", "生肉", "冷凍", "療法食", "トッピング"), (100, 6000)),
        ("catfood", "キャットフード", "キャットフード ドライ kg", "1kg", ("おやつ", "ウェット", "缶", "パウチ", "ちゅ", "療法食"), (100, 6000)),
    ]
]


def esc(s):
    return html.escape(str(s or ""), quote=True)


# 11/9 夜#147：売り文句（クーポン・時刻・倍率）で商品名が切れて「米」「ジョージア 01:59まで コカ」になった → 切る前に外す
PRE = [r"【[^】]*】", r"＼[^／]*／", r"\d+[%％]\s*OFF\S*", r"クーポン\S*", r"エントリーで\S*", r"全品\S*", r"ポイント(?:最大)?[\d.]+倍\S*",
       r"P\d+倍\S*", r"\d+/\d+\S*", r"\d+月\d+日\S*", r"\d+日\d+:\d\d\S*", r"\d{1,2}:\d\d\S*", r"\S*限定[!！]*", r"ランキング\S*",
       r"[★☆]", r"先着\S*", r"さらに\S*", r"[!！]+"]


def short(name, n=46):
    name = str(name)
    for p in PRE:
        name = re.sub(p, " ", name)
    name = " ".join(name.replace("【", " ").replace("】", " ").split()).strip(" ｜|&＆・")
    if len(name) <= n:
        return name
    # 11/9 全文点検：「…60個 バ」のように言葉の途中で切れていた → 言葉の切れ目で切る
    cut = name[:n]
    return (cut.rsplit(" ", 1)[0] if " " in cut[n // 2:] else cut) + "…"


def z2h(s):
    t = str(s).translate(str.maketrans("０１２３４５６７８９．，ｍｌＭＬｋｇＫＧｘＸ＊*", "0123456789.,mlMLkgKG××××"))
    t = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", t)  # 2,580g → 2580g
    t = re.sub(r"1\s*(?:枚|本|個|kg|L)\s*(?:あたり|当たり)[^\s　]*", " ", t)  # 「1枚あたり12円」は量ではない
    # 11/3 「※お一人様5個まで」を5個入りと読んでいた（ドッグフード1.5kgが7.5kgに）→ 買える数の決まりは量ではない
    t = re.sub(r"(?:お一人様|おひとり様|お1人様|1人|一人)?\s*\d+\s*(?:個|点|本|袋|セット)\s*(?:まで|限り|限定)", " ", t)
    return re.sub(r"[(（]\s*\d{6,}\s*[)）]", " ", t)  # (52902061) のような品番


def one(vals):
    """読めた数がちょうど1種類の時だけ使う（24本・48本のように選ぶ物は比べない）。"""
    s = sorted(set(vals))
    return s[0] if len(s) == 1 else None


def amount(cat, name):
    """商品名から量を読む。読めなければ None。戻りは (単位の数, 量の説明)。"""
    t = z2h(name)
    if cat in ("water", "soda"):
        ml = [float(v) for v in re.findall(NUM + r"\s*(?:ml|mL|ML|ミリリットル)", t)]
        ml += [float(v) * 1000 for v in re.findall(NUM + r"\s*(?:L|ℓ|リットル)(?![a-zA-Z])", t)]
        n = [int(v) for v in re.findall(r"(\d+)\s*本", t)]
        a, b = one(ml), one(n)
        if not a or not b or a < 200 or a > 2500:
            return None
        return a * b / 1000, f"{a:g}ml×{b}本"
    if cat == "rice":
        kg = [float(v) for v in re.findall(NUM + r"\s*(?:kg|KG|Kg|キロ)", t)]
        a = one(kg)
        if not a or a < 1 or a > 30:
            return None
        return a, f"{a:g}kg"
    if cat == "tp":
        m = [float(v) for v in re.findall(NUM + r"\s*(?:m|M|メートル)(?![mlLa-zA-Z])", t)]
        r = [int(v) for v in re.findall(r"(\d+)\s*(?:ロール|R(?![a-zA-Z]))", t)]
        pk = re.findall(r"(\d+)\s*(?:ロール|R)\s*[x×]\s*(\d+)\s*(?:パック|袋|セット)", t)
        a, b = one(m), one(r)
        if pk and len(set(pk)) == 1 and a:  # 12ロール×4パック の形は掛ける
            b = int(pk[0][0]) * int(pk[0][1])
        if not a or not b or a < 10 or a > 300:
            return None
        return a * b / 100, f"{a:g}m×{b}ロール"
    k = KIND.get(cat)
    if k == "vol":
        ml = [float(v) for v in re.findall(NUM + r"\s*(?:ml|mL|ML|ミリリットル)", t)]
        ml += [float(v) * 1000 for v in re.findall(NUM + r"\s*(?:L|ℓ|リットル)(?![a-zA-Z])", t)]
        isg = False
        if cat not in ("tea", "coffee") and not ml:  # 洗剤などの液体は g で売る物が多い（水に近い重さ）→ 1L・1kgあたりで同じに比べる
            ml += [float(v) for v in re.findall(NUM + r"\s*(?:g|グラム)(?![a-zA-Z])", t)]
            ml += [float(v) * 1000 for v in re.findall(NUM + r"\s*(?:kg|KG|Kg|キロ)", t)]
            isg = True
        return _per_pack(t, ml, 100, 20000, lambda a: (f"{a / 1000:g}kg" if a >= 1000 else f"{a:g}g") if isg else
                         (f"{a / 1000:g}L" if a >= 1000 else f"{a:g}ml"), 1000)
    if k == "wt":
        g = [float(v) for v in re.findall(NUM + r"\s*(?:g|グラム)(?![a-zA-Z])", t)]
        g += [float(v) * 1000 for v in re.findall(NUM + r"\s*(?:kg|KG|Kg|キロ)", t)]
        # 11/3 「福袋 1.6kg 4種」は合計1.6kg（4袋分ではない）→ 種類の数を袋の数と読まない
        if re.search(r"\d+\s*種|福袋|飲み比べ|詰め合わせ|各\s*\d", t):
            v = sorted(set(g))
            if len(v) == 1 and 100 <= v[0] <= 30000:
                return v[0] / 1000, (f"{v[0] / 1000:g}kg" if v[0] >= 1000 else f"{v[0]:g}g")
            if len(v) == 2:  # 「各400g 1.6kg」は大きい方が合計
                return v[1] / 1000, (f"{v[1] / 1000:g}kg" if v[1] >= 1000 else f"{v[1]:g}g")
            return None
        return _per_pack(t, g, 100, 30000, lambda a: f"{a / 1000:g}kg" if a >= 1000 else f"{a:g}g", 1000)
    if k in ("pcs", "hon"):
        w = "枚" if k == "pcs" else "本"
        tot = re.findall(r"(?:合計|計)\s*(\d+)\s*" + w, t)
        if len(set(tot)) == 1:
            a = int(tot[0])
        else:
            n = sorted(set(int(v) for v in re.findall(r"(\d+)\s*" + w, t)))
            pk = set(int(x) * int(y) for x, y in re.findall(r"(\d+)\s*" + w + r"\s*(?:入り?)?\s*[)）]?\s*[x×]?\s*(\d+)\s*(?:" + PACK + ")", t))
            pk |= set(int(x) * int(y) for x, y in re.findall(r"(\d+)\s*" + w + r"\s*(?:入り?)?\s*[)）]?\s*[x×]\s*(\d+)", t))
            if len(pk) == 1:
                a = pk.pop()
                if any(v != a and a % v for v in n):  # 「80枚×12個」のほかに合わない枚数があれば読まない
                    return None
            elif len(pk) > 1:
                return None
            elif len(n) == 1:
                a = n[0]
                if k == "pcs":  # 「【4個セット】38枚」＝4袋
                    c = set(int(v) for v in re.findall(r"(\d+)\s*(?:" + PACK + r")\s*セット", t))
                    if len(c) == 1:
                        a *= c.pop()
            elif len(n) == 2 and n[1] % n[0] == 0 and str(n[1] // n[0]) in re.findall(r"(\d+)\s*(?:" + PACK + ")", t):
                a = n[1]  # 「200枚 50枚 4箱」
            else:
                return None
        if not a or a < 2 or a > 5000:
            return None
        return a, f"{a}{w}"
    if k == "kumi":
        kumi = sorted(set(int(v) for v in re.findall(r"(\d+)\s*組", t)))
        box = sorted(set(int(v) for v in re.findall(r"(\d+)\s*(?:箱|個|パック|袋)", t)))
        if len(kumi) != 1 or len(box) != 1:
            return None
        a, b = kumi[0], box[0]
        if a < 50 or a > 1000:
            return None
        return a * b / 100, f"{a}組×{b}" + ("袋" if re.search(str(b) + r"\s*袋", t) else "箱")
    return None


PACK = r"本|個|袋|パック|箱|小箱|缶|冊|コ|ケース|セット|点"


def _count(t):
    """何個（本・袋・箱）入りか。読めない時は None、書いていない時は 1。
    「12本入り×2ケース」「24本×2箱」は掛ける。「24本 48本 選べる」のように2つ以上あれば読まない。"""
    tot = re.findall(r"(?:合計|計)\s*(\d+)\s*(?:本|個|袋|缶)", t)
    if len(set(tot)) == 1:
        return int(tot[0])
    pk = set(int(x) * int(y) for x, y in re.findall(r"(\d+)\s*(?:本|個|袋|パック|缶|コ)\s*(?:入り?)?\s*[)）]?\s*[x×]\s*(\d+)", t))
    one_ = set(int(v) for v in re.findall(r"(?<![\d.])(\d+)\s*(?:本|個|袋|パック|缶|コ)(?!\s*[x×]\s*\d|パック|分)", t))
    one_ |= set(int(v) for v in re.findall(r"[x×]\s*(\d+)(?![\d.]|\s*(?:ml|mL|L|g|kg|枚|組|m|cm|mm))", t))
    if len(pk) == 1:
        a = next(iter(pk))
        return a if all(v == a or a % v == 0 for v in one_) else None
    if len(pk) > 1:
        return None
    if not one_:
        return 1
    return one_.pop() if len(one_) == 1 else None


def _per_pack(t, vals, lo, hi, fmt, div):
    """1袋（1本）の量 × 何袋。「15kg (5kg×3袋)」「500g×4個 2kg」のように合計も書いてある時は合計を使う。"""
    v = sorted(set(vals))
    c = _count(t)
    if len(v) == 2 and c and c > 1 and abs(v[0] * c - v[1]) < 1:
        return v[1] / div, f"{fmt(v[0])}×{c}"
    if len(v) == 2 and not c:
        cs = set(int(x) for x in re.findall(r"[x×]\s*(\d+)", t))
        if len(cs) == 1 and abs(v[0] * next(iter(cs)) - v[1]) < 1:
            return v[1] / div, f"{fmt(v[0])}×{next(iter(cs))}"
    if len(v) != 1 or not c or c > 200:
        return None
    a = v[0]
    if a < lo or a > hi:
        return None
    return a * c / div, fmt(a) + (f"×{c}" if c > 1 else "")


def item_page(it):
    """楽天の商品ページURL（itemCode「店:番号」から。投稿の2つ目のリンクと expect に使う）。"""
    shop, _, no = str(it.get("itemCode") or "").partition(":")
    return f"https://item.rakuten.co.jp/{shop}/{no}/" if shop and no else ""


# 11/6 テスター「キャットフード 4kg×2 6,190円 と出るが、6,190円は4kg単品。2個は12,140円」
# → 1つのページで量や個数を選べる物は、楽天の値段がいちばん安い選び方の値段になり、名前の量と合わない。
#   値段と量が1つに決まらない物は、1個あたりの順位に入れない（まちがった安さを出さない）
AMBIG = re.compile(r"選べる|選択|さらにお得|セットがお得|セットでお得|単品|よりどり|バリエーション|[1１][個袋本箱]・|[1１][個袋本箱]/")


def ambiguous(name, it=None):
    if AMBIG.search(name or ""):
        return True
    it = it or {}
    lo_, hi_ = it.get("itemPriceMin1"), it.get("itemPriceMax1")
    try:
        return bool(lo_ and hi_ and int(lo_) != int(hi_))
    except (TypeError, ValueError):
        return False


def fetch(cat):
    key, _, kw, gid, unit, ng, (lo, hi) = cat
    rows, seen, n_all, err = [], set(), 0, ""

    def take(items):
        nonlocal n_all
        for it in items:
            code = it.get("itemCode")
            if code in seen:
                continue
            seen.add(code)
            n_all += 1
            name = it.get("itemName") or ""
            if any(w in name for w in ng) or not must_ok(key, name):
                continue
            am = amount(key, name)
            price = int(it.get("itemPrice") or 0)
            if not am or not price or ambiguous(name, it):
                continue
            per = price / am[0]
            if not (lo <= per <= hi):  # 読みまちがいらしい物は入れない
                continue
            aff = it.get("affiliateUrl") or ""
            if not aff.startswith("https://hb.afl.rakuten.co.jp/"):
                continue
            rows.append({"name": short(name), "price": price, "per": round(per, 1), "amt": am[1],
                         "rc": int(it.get("reviewCount") or 0), "av": float(it.get("reviewAverage") or 0),
                         "shop": it.get("shopName") or "", "url": aff, "plain": item_page(it),
                         "img": lib._item_image(it), "bd": brand_of(key, name),
                         "ship": ship_note(name + " " + (it.get("itemCaption") or ""))})

    for page in range(1, (NEWPAGES if key in KIND else PAGES) + 1):
        q = {"keyword": kw, "postageFlag": 1, "availability": 1, "sort": "-reviewCount", "hits": 30, "page": page}
        if gid:
            q["genreId"] = gid
        if key in KIND:
            q["NGKeyword"] = NGKW + (" 大人 介護" if key == "diaper" else "")
        items, err = lib._rakuten_search(q)
        time.sleep(1.1)  # 楽天APIは1秒に1回まで
        if not items:
            break
        take(items)
    # 11/6 夜#69「無香料の柔軟剤」などで探す人がいる → よく探す条件の言葉でも1回ずつ探して、くらべる物に入れる（30件×数回）
    for w in EXTRAQ.get(key, ()):
        q = {"keyword": f"{kw.split()[0]} {w}", "postageFlag": 1, "availability": 1, "sort": "-reviewCount", "hits": 30}
        if gid:
            q["genreId"] = gid
        if key in KIND:
            q["NGKeyword"] = NGKW + (" 大人 介護" if key == "diaper" else "")
        items, _ = lib._rakuten_search(q)
        time.sleep(1.1)
        take(items or [])
    # 名の知れた物が少ない時は、メーカー名でもう1回ずつ探す（最初の言葉＋メーカー名、30件）
    have = {r["bd"] for r in rows} - {""}
    if len(have) < BRAND_MIN:
        for b in [b for b in BRAND.get(key, ()) if b not in have][:BRAND_ASK]:
            q = {"keyword": f"{kw.split()[0]} {b}", "postageFlag": 1, "availability": 1, "sort": "-reviewCount", "hits": 30}
            if gid:
                q["genreId"] = gid
            items, _ = lib._rakuten_search(q)
            time.sleep(1.1)
            take(items or [])
    rmin = RMIN.get(key, RMIN_NEW)
    # 名の知れたメーカーの物は、レビューの数を10件まで下げてよい（1商品のレビューが散らばるため。★4.0以上は同じ）。
    def passes(r):
        # 11/5 オーナー「ノーブランドで安いのは当たり前」：水・トイレットペーパーなど1,000件の種類でも、名の知れたメーカーは100件まで下げる
        # （1位がメーカー名なしの物ばかりになっていた）。名の知れていない物は1,000件のまま
        m = (min(rmin, 10) if rmin < 1000 else 100) if r["bd"] else rmin
        return r["rc"] >= m and (r["av"] >= 4.0 or not m)
    ok = sorted([r for r in rows if passes(r)], key=lambda r: r["per"])
    # 11/3 点検：読んだ全部の真ん中の値段より極端に安い物は、量の読みちがいの事が多い → 外してログに残す
    if len(rows) >= 8:
        med = sorted(r["per"] for r in rows)[len(rows) // 2]
        # 11/3 オーナーに見せる前の見直し：本当に安い大袋（マスク1020枚・ドッグフード10kg）まで外していた。
        # 「×3」のように数をかけた時だけ読みちがいを疑う。かけていない物は、真ん中の15%未満の時だけ外す
        bad = [r for r in ok if r["per"] < med * 0.15 or (r["per"] < med * 0.3 and "×" in str(r.get("amt") or ""))]
        for r in bad:
            print("安すぎて外した（量の読みちがいかも）", key, r["per"], r["amt"], r["name"][:40])
        ok = [r for r in ok if r not in bad]
    # 11/6 夜：「4kg×2 6,190円」は4kg 1つの値段だった。同じメーカーの1つ（4kg）の値段×数より、まとめ買いがずっと安い物は、
    #   1つの値段を読んでいる見込みが高い → 外してログに残す（本当のまとめ割はふつう2〜3割引きまで）
    singles = {}
    for r in rows:
        a = str(r.get("amt") or "")
        if r["bd"] and "×" not in a:
            singles.setdefault((r["bd"], a), []).append(r["price"])
    def bundle_bad(r):
        a = str(r.get("amt") or "")
        m = re.match(r"(.+?)×(\d+)", a)
        if not (m and r["bd"]):
            return False
        sp = singles.get((r["bd"], m.group(1)))
        return bool(sp) and r["price"] < min(sp) * int(m.group(2)) * 0.7
    for r in [r for r in ok if bundle_bad(r)]:
        print("まとめ買いなのに安すぎて外した（1つの値段かも）", key, r["price"], r["amt"], r["name"][:40])
    ok = [r for r in ok if not bundle_bad(r)]
    out, shops = [], set()
    names = set()
    for r in ok:  # 同じ店は1つ（並びが1店で埋まらないように）。11/3 同じ商品名（別の店の同じ物）も1つ
        nk = re.sub(r"\W", "", re.sub(r"[【\[＼(（].*?[】\]／)）]", "", r["name"]))[:20]
        if r["shop"] in shops or nk in names:
            continue
        shops.add(r["shop"])
        names.add(nk)
        out.append(r)
    avg = round(sum(r["per"] for r in rows) / len(rows), 1) if rows else 0
    top = brand_first(key, out, TOP)
    # 11/6 条件の言葉（無香料・パンツLなど）の物が上に1つも無い時は、その中の安い物を2つまで足す（条件で選んだ時に0件にならないように）
    for w in EXTRAQ.get(key, ()):
        ws = w.split()
        if not any(all(x in r["name"] for x in ws) for r in top):
            top += [r for r in sorted(out, key=lambda r: r["per"]) if all(x in r["name"] for x in ws) and r not in top][:2]
    print("名の知れた物", key, sum(1 for r in top if r["bd"]), "/", len(top))
    return {"key": key, "title": cat[1], "unit": unit, "seen": n_all, "read": len(rows), "ok": len(ok),
            "avg": avg, "rmin": rmin, "top": top}, err


AMZ_WORDS = {"water": ("天然水", "ミネラルウォーター", "水 "), "soda": ("炭酸",), "rice": ("米",), "tp": ("トイレット",)}


def amazon_rows(key, unit_lo_hi):
    """凪がブラウザで確かめたAmazonの商品（7日以内・○・レビュー1,000件以上・★4.0以上）のうち、この物に当たる物。
    11/1 オーナー「Amazonも、使えよ」。Amazonは値段を隠すことが多いので、値段が読めた物だけ1Lあたりを出し、
    読めない物は「値段はAmazonのページで」として並べる（数字は作らない）。"""
    lo, hi = unit_lo_hi
    out = []
    for asin, it in lib.amazon_checked().items():
        name = str(it.get("name", ""))
        if not any(w in name for w in AMZ_WORDS.get(key, ())) or (key == "water" and "炭酸" in name):
            continue
        res = lib.amazon_link(asin, max_age_h=168)
        if not res.get("ok"):
            continue
        m = re.search(r"[￥¥]\s*([\d,]+)|([\d,]+)\s*円", str(it.get("price", "")))
        price = int((m.group(1) or m.group(2)).replace(",", "")) if m else 0
        am = None if ambiguous(name) else amount(key, name + " " + str(it.get("specs", "")))
        per = round(price / am[0], 1) if price and am else 0
        if per and not (lo <= per <= hi):
            per = 0
        out.append({"name": short(name), "price": price, "per": per, "amt": am[1] if am else str(it.get("specs", ""))[:30],
                    "rc": int(it.get("reviews") or 0), "av": float(it.get("stars") or 0), "url": res["link"], "asin": asin})
    return sorted(out, key=lambda r: (r["per"] == 0, r["per"]))[:2]


# 11/3 オーナー「楽天だけじゃねぇだろ」→ Yahoo!ショッピングも同じ物差しで比べる（鍵 YAHOO_APP_ID がある時だけ。無ければ今までどおり）
MOSHIMO_YAHOO = "https://af.moshimo.com/af/c/click?a_id=5877817&p_id=1225&pc_id=1925&pl_id=18502&url="
# 11/3 バリューコマース（Yahoo!ショッピングの公式の窓口）が通った。LIFE NOTE のサイトID 3786665。
# pid（Yahoo!ショッピングの広告番号）が入ったら、Yahoo!の検索がそのまま報酬つきのリンクを返す（affiliate_type=vc）。空の間は もしも のまま
VC_SID = "3786665"
VC_PID = ""


def yahoo_rows(cat):
    """Yahoo!ショッピング商品検索（v3）で、送料無料・レビュー多い順の物を同じ読み方で1個あたりに直し、安い2つ。"""
    import urllib.parse
    import urllib.request
    appid = os.environ.get("YAHOO_APP_ID", "").strip()
    if not appid:
        return []
    key, _, kw, _, _, ng, (lo, hi) = cat
    qd = {"query": kw, "results": 50, "sort": "-review_count", "shipping": "free", "in_stock": "true"}
    if VC_PID:
        qd.update(affiliate_type="vc", affiliate_id=f"https://ck.jp.ap.valuecommerce.com/servlet/referral?sid={VC_SID}&pid={VC_PID}&vc_url=")
    q = urllib.parse.urlencode(qd)
    # 11/3 鍵だけだと 403。Yahoo!は User-Agent に「Yahoo AppID: 鍵」を入れる決まり
    req = urllib.request.Request("https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch?" + q,
                                 headers={"User-Agent": f"Yahoo AppID: {appid}"})
    with urllib.request.urlopen(req, timeout=20) as r:
        hits = json.load(r).get("hits") or []
    time.sleep(1.1)
    out, shops = [], set()
    for it in hits:
        name = it.get("name") or ""
        if any(w in name for w in ng) or not must_ok(key, name):
            continue
        am = amount(key, name)
        price = int(it.get("price") or 0)
        if ambiguous(name):
            continue
        rv = it.get("review") or {}
        rc, av = int(rv.get("count") or 0), float(rv.get("rate") or 0)
        if not am or not price or rc < min(300, RMIN.get(key, RMIN_NEW)) or av < 4.0:
            continue
        per = price / am[0]
        shop = (it.get("seller") or {}).get("name") or ""
        if not (lo <= per <= hi) or shop in shops:
            continue
        shops.add(shop)
        out.append({"name": short(name), "price": price, "per": round(per, 1), "amt": am[1], "rc": rc, "av": av, "shop": shop, "bd": brand_of(key, name),
                    "url": (it.get("url") or "") if VC_PID else MOSHIMO_YAHOO + urllib.parse.quote(it.get("url") or "", safe=""), "img": (it.get("image") or {}).get("medium") or ""})
    return brand_first(key, sorted(out, key=lambda r: r["per"]), 2)


def yh_card(r, unit):
    return (f'<li class="it"><a class="cd" href="{esc(r["url"])}" rel="sponsored noopener" target="_blank" data-k="yh" data-bd="{esc(r.get("bd") or "")}">'
            + (f'<img class="ph" src="{esc(r["img"])}" alt="" loading="lazy" referrerpolicy="no-referrer">' if r.get("img") else "")
            + f'<span class="rk az" style="background:#FF0033">Y</span><span class="tx"><span class="nm">{esc(r["name"])}</span>'
            f'<span class="pu">{unit}あたり <b>{yen(r["per"])}円</b></span>'
            f'<span class="mt">{r["price"]:,}円（送料無料・{esc(r["amt"])}）　★{r["av"]:.2f}　レビュー{r["rc"]:,}件</span>'
            f'<span class="go">Yahoo!ショッピングで見る →</span></span></a></li>')


def amz_card(r, unit):
    pu = f'<span class="pu">{unit}あたり <b>{yen(r["per"])}円</b>（{r["price"]:,}円で計算・送料はページで）</span>' if r["per"] else \
        '<span class="pu">値段はAmazonのページで（Amazonはページを開かないと値段が出ない物があります）</span>'
    return (f'<li class="it"><a class="cd" href="{esc(r["url"])}" rel="sponsored noopener" target="_blank" data-k="amz:{esc(r["asin"])}">'
            f'<span class="rk az">A</span><span class="tx"><span class="nm">{esc(r["name"])}</span>{pu}'
            f'<span class="mt">{esc(r["amt"])}　★{r["av"]:.1f}　レビュー{r["rc"]:,}件</span>'
            f'<span class="go">Amazonで見る →</span></span></a></li>')


def yen(v):
    return f"{v:,.0f}" if v >= 100 else f"{v:,.1f}".rstrip("0").rstrip(".")


# 11/9 売上の調査 11/8：最安の水が「11月中旬～11月下旬頃発送予定」だった。すぐ届かない物は、カードに発送の予定を1行出す
SHIP_RE = re.compile(r"(\d{1,2}月\s*(?:\d{1,2}日|上旬|中旬|下旬|末)[^。、\n<>]{0,14}?(?:発送|出荷|お届け)(?:予定)?)")


def ship_note(text):
    m = SHIP_RE.search(text or "")
    if m:
        return m.group(1).replace(" ", "")[:24]
    if re.search(r"予約(?:商品|販売|受付)|入荷待ち|お取り寄せ", text or ""):
        return "予約・取り寄せ（届く日はリンク先で）"
    return ""


def card(r, i, unit, avg):
    img = f'<img src="{esc(r["img"])}" alt="" width="84" height="84" loading="lazy" onerror="this.remove()">' if r["img"] else ""
    diff = f'<span class="df">比べた全部の平均より {round((1 - r["per"] / avg) * 100)}% 安い</span>' if avg and r["per"] < avg * 0.95 else ""
    return (f'<li class="it"><a class="cd" href="{esc(r["url"])}" rel="sponsored noopener" target="_blank" data-k="{esc(r["name"][:30])}" data-bd="{esc(r.get("bd") or "")}">'
            f'<span class="rk">{i}</span>{img}<span class="tx"><span class="nm">{esc(r["name"])}</span>'
            f'<span class="pu">{unit}あたり <b>{yen(r["per"])}円</b></span>{diff}'
            f'<span class="mt">{r["price"]:,}円（送料込み・{esc(r["amt"])}）　★{r["av"]:.2f}　レビュー{r["rc"]:,}件</span>'
            + (f'<span class="df">発送：{esc(r["ship"])}（すぐには届きません）</span>' if r.get("ship") else "")
            + f'<span class="go">楽天で見る →</span></span></a></li>')


def render(cats, now):
    upd = f"{now.month}/{now.day}（{WEEK[now.weekday()]}）{now:%H:%M} 楽天で確かめた値段"
    seen = sum(c["seen"] for c in cats)
    tabs = "".join(f'<button type="button" data-f="{c["key"]}">{esc(c["title"].split("（")[0])}</button>' for c in cats)
    secs = ""
    for c in cats:
        lis = "".join(card(r, i, c["unit"], c["avg"]) for i, r in enumerate(c["top"], 1))
        secs += (f'<section class="ps" data-p="{c["key"]}"><h2>{esc(c["title"])}</h2>'
                 f'<p class="how">楽天の送料込みの{c["seen"]}件を見て、量が読めた{c["read"]}件を{c["unit"]}あたりに直しました。'
                 + (f'レビュー{c.get("rmin", 1000):,}件以上・評価4.0以上は{c["ok"]}件。' if c.get("rmin", 1000) else f'大手の{c["ok"]}件（ケース売りはレビューがほぼ無いので、メーカー名でしぼりました）。')
                 + f'名の知れたメーカーの物を先に、その中で安い順です（同じお店は1つ）。'
                 f'{"比べた全部の平均は" + c["unit"] + "あたり" + yen(c["avg"]) + "円。" if c["avg"] else ""}</p>'
                 f'<ul>{lis}</ul>'
                 + (f'<h3 class="az3">Yahoo!ショッピングでは（送料無料・同じ物差し）</h3><ul>{"".join(yh_card(r, c["unit"]) for r in c["yh"])}</ul>'
                    if c.get("yh") else "")
                 + (f'<h3 class="az3">Amazonでは（Amazonのページを開いて確かめた物）</h3><ul>{"".join(amz_card(r, c["unit"]) for r in c["amz"])}</ul>'
                    if c.get("amz") else "") + '</section>')
    names = "・".join(c["title"].split("（")[0] for c in cats)
    amz = any(c.get("amz") for c in cats)
    title = f"1個あたりで比べた 楽天{'とAmazon' if amz else ''}の{names}｜うさぎ│LIFE NOTES"
    desc = f"楽天の送料込みの商品{seen}件を、1Lあたり・1kgあたり・100mあたりに直して比べました。レビューの多い評価4.0以上の中で安い順。"
    css = open(os.path.join(ROOT, "scripts", "kaimawari.py"), encoding="utf-8").read()
    css = css[css.index("<style>") + 7:css.index("</style>")].replace("{{", "{").replace("}}", "}")
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}/{PAGE}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}/og-v10.png"><meta property="og:url" content="{SITE}/{PAGE}"><meta name="twitter:card" content="summary">
<link rel="icon" href="logo.png"><link rel="apple-touch-icon" href="logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=Jost:wght@300;400&display=swap">
<style>{css}
.how{{font-size:12px;line-height:1.85;color:var(--sub);margin:0 0 12px}}
.rk{{flex:none;width:22px;font:600 18px/1 var(--min);color:var(--brown);padding-top:4px;text-align:center}}
.pu{{font-size:12.5px;color:var(--sub)}}.pu b{{font-size:19px;color:var(--red);letter-spacing:.02em}}
.df{{font-size:11.5px;color:var(--red)}}
.az{{font:700 13px/22px var(--en);color:#fff;background:#2B2622;border-radius:50%;width:22px;height:22px;padding:0;margin-top:2px}}
.az3{{font:600 13px/1.5 var(--go);color:var(--sub);margin:16px 0 8px}}
.big{{background:#fff;border:1px solid var(--line);border-radius:4px;padding:14px;margin:18px 0 0;text-align:center}}
.big b{{display:block;font:600 30px/1.2 var(--min);color:var(--ink);letter-spacing:.04em}}.big span{{font-size:12px;color:var(--mute)}}
</style><script src="/assets/night.js?v=14"></script><script src="/assets/menu.js?v=33" defer></script><link rel="stylesheet" href="/assets/sub.css?v=4"><script src="/assets/v2sub.js?v=11" defer></script></head>
<body><div class="wrap">
<header class="head"><img src="logo-s.png" alt="うさぎ│LIFE NOTES のロゴ" width="64" height="64">
<p class="en">PER UNIT</p>
<h1>1個あたりで比べた<small>楽天{"とAmazon" if amz else ""}の、毎日なくなる物</small></h1>
<p class="up">{esc(upd)}</p>
<div class="big"><b>{seen:,}件</b><span>今回、楽天で見て比べた商品の数</span></div>
<p class="lead">値段だけでは、どれがいちばん安いか分かりません。楽天の送料込みの商品を毎回取り直し、商品名の量（ml・本・kg・ロール・m）から1Lあたり・1kgあたり・100mあたりに直して比べました。24本・48本を選ぶ物のように量がひとつに決まらない物は、数字をまちがえないよう比べていません。</p>
</header>
<nav class="tabs" aria-label="物"><button type="button" data-f="" class="on">すべて</button>{tabs}</nav>
<main>{secs}</main>
<footer class="foot">
<p>値段・送料・レビューは、このページを作った時に楽天で確かめた物です。量は商品名から読んでいるので、買う前にリンク先で内容量を確かめてください。</p>
<p>このページのリンクは楽天アフィリエイト・Amazonアソシエイトの広告（PR）です。Amazonのアソシエイトとして、うさぎ│LIFE NOTES は適格販売により収入を得ています。</p>
<a class="back" href="./">関東おでかけリストを見る</a>
<p class="sign">うさぎ│LIFE NOTES</p>
</footer></div>
<script>
(function(){{
  var bs=document.querySelectorAll('.tabs button');
  bs.forEach(function(b){{b.addEventListener('click',function(){{var f=b.dataset.f;
    document.querySelectorAll('.ps').forEach(function(s){{s.hidden=!!f&&s.dataset.p!==f}});
    bs.forEach(function(x){{x.classList.toggle('on',x===b)}});}})}});
  document.querySelectorAll('.cd').forEach(function(a){{a.addEventListener('click',function(){{
    try{{navigator.sendBeacon("/c?f=tanka&s=tanka&k="+encodeURIComponent(a.dataset.k||''))}}catch(e){{}}}})}});
}})();
</script></body></html>
"""


def main():
    now = datetime.now(JST)
    cats, errs = [], []
    if os.environ.get("TANKA_FROM_CACHE"):  # 手元で見た目を確かめる時だけ：前の回の data/tanka.json から作る（楽天は呼ばない・保存しない）
        d = json.load(open(os.path.join(ROOT, "data", "tanka.json"), encoding="utf-8"))
        for c in d["cats"]:
            c["top"] = [r for r in c["top"] if not ambiguous(r["name"])]
            cats.append(c | {"yh": [], "amz": []})
        site = os.path.join(ROOT, "site")
        open(os.path.join(site, f"{PAGE}.html"), "w", encoding="utf-8").write(render(cats, now))
        return
    # 11/7 GitHubの分数が11月の2,000分を超える見込み（notes/actions-minutes.md）。楽天を100件以上呼ぶこの係が1回3分。
    # 前の取り直しから10時間たっていなければ、楽天を呼ばずに前の data/tanka.json でページを作る（値段の時刻は前に確かめた時刻のまま出す）。
    # 定時の 7:30・18:30 は11時間あくので、毎回取り直す。TANKA_FRESH=1 でいつも取り直す。
    try:
        d = json.load(open(os.path.join(ROOT, "data", "tanka.json"), encoding="utf-8"))
        at = datetime.strptime(d["at"], "%Y-%m-%d %H:%M").replace(tzinfo=JST)
        cached = d["cats"] if (now - at).total_seconds() < 10 * 3600 and not os.environ.get("TANKA_FRESH") else None
    except Exception:
        cached = None
    if cached and len(cached) >= 2:
        cats = [{"rmin": RMIN.get(c["key"], RMIN_NEW)} | c | {"yh": c.get("yahoo") or [], "amz": c.get("amazon") or []} for c in cached]
        site = os.path.join(ROOT, "site")
        os.makedirs(site, exist_ok=True)
        open(os.path.join(site, f"{PAGE}.html"), "w", encoding="utf-8").write(render(cats, at))
        print(f"前の取り直し（{d['at']}）から10時間たっていないので、楽天を呼ばずに作った")
        return
    for c in CATS:
        try:
            r, err = fetch(c)
        except Exception as e:  # 楽天につながらない時は、その物を出さない
            r, err = None, str(e)[:80]
        if err:
            errs.append(f"{c[0]}: {err[:80]}")
        if r and r["top"]:
            try:
                r["yh"] = yahoo_rows(c)
                if r.get("avg"):  # 11/3 楽天の平均の3割より安いYahoo!は読みちがいとして外す
                    for y in [y for y in r["yh"] if y["per"] < r["avg"] * 0.15 or (y["per"] < r["avg"] * 0.3 and "×" in str(y.get("amt") or ""))]:
                        print("安すぎて外した（Yahoo!）", c[0], y["per"], y["amt"], y["name"][:40])
                    r["yh"] = [y for y in r["yh"] if not (y["per"] < r["avg"] * 0.15 or (y["per"] < r["avg"] * 0.3 and "×" in str(y.get("amt") or "")))]
            except Exception as e:  # Yahoo!が読めなくても楽天の比べは出す
                errs.append(f"{c[0]} yahoo: {str(e)[:60]}")
            try:
                r["amz"] = amazon_rows(c[0], c[6])
            except Exception as e:  # Amazonが読めなくても楽天の比べは出す
                errs.append(f"{c[0]} amazon: {str(e)[:60]}")
            cats.append(r)
    print(json.dumps({"tanka": [(c["key"], c["seen"], c["read"], c["ok"], len(c["top"])) for c in cats], "errs": errs},
                     ensure_ascii=False))
    if len(cats) < 2:  # 少なすぎる時は前のページを残す
        return
    site = os.path.join(ROOT, "site")
    os.makedirs(site, exist_ok=True)
    open(os.path.join(site, f"{PAGE}.html"), "w", encoding="utf-8").write(render(cats, now))
    slim = [{k: c[k] for k in ("key", "title", "unit", "seen", "read", "ok", "avg")} | {"rmin": c.get("rmin", 1000)} |
            {"top": [{k: r.get(k, "") for k in ("name", "price", "per", "amt", "rc", "av", "shop", "plain", "bd", "url", "img", "ship")} for r in c["top"]],
             "amazon": [{k: r.get(k, "") for k in ("asin", "name", "price", "per", "amt", "rc", "av", "url")} for r in c.get("amz", [])],
             "yahoo": [{k: r.get(k, "") for k in ("name", "price", "per", "amt", "rc", "av", "shop", "bd", "url", "img")} for r in c.get("yh", [])]}
            for c in cats]
    lib.save_json(os.path.join(ROOT, "data", "tanka.json"), {"at": now.strftime("%Y-%m-%d %H:%M"), "cats": slim})


if __name__ == "__main__":
    main()
