"""関東の開店・閉店ニュース（/kaiten）を作る。11/17 月（関西 https://kansai.townnote.app/kaiten と同じ形。usagi tools/kaiten/build.py）。
元は data/kaiten.json（月の毎晩 21:20 の回が「速報の種」の【速報 関東】から足す）。
頭（題・フォント・night.js・menu.js）は関東の紅葉ページ（site/koyo.html）から借り、中身と見た目はここで全部書く。夜の色は night.js が作る。
使い方: python3 scripts/kaiten.py                  （page.yml で koyo.py のあと。失敗してもHPは出す）
        python3 scripts/kaiten.py add '{"d":"2026-11-20","k":"open","p":"東京","n":"名前","pt":"新しい点","pl":"場所","tm":"","u":"https://..."}' …"""
import datetime, html, json, os, re, sys, urllib.parse
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SITE = os.path.join(ROOT, "site")
DATA = os.path.join(ROOT, "data", "kaiten.json")
BASE = "https://usagi-life-notes.pages.dev/"  # page.yml が LIFE_BASE（kanto.townnote.app）に置き換える
E = html.escape
DONE_DAYS = 30
PREFS = ["東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬"]
KL = {"open": "開店", "pop": "期間限定", "close": "閉店"}
WD = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
TODAY = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date()


def add(rows):
    j = json.load(open(DATA, encoding="utf-8"))
    have = {(x["u"], x["n"]) for x in j["items"]}
    n = 0
    for r in rows:
        x = json.loads(r)
        for k in ("d", "k", "p", "n", "pt", "pl", "u"):
            assert x.get(k), f"{k} が無い: {r}"
        assert x["k"] in KL and x["p"] in PREFS and x["u"].startswith("https://"), r
        d = datetime.date.fromisoformat(x["d"])
        if (x["u"], x["n"]) in have or (x["k"] == "close" and d < TODAY) or (d - TODAY).days < -DONE_DAYS:
            print("足さない:", x["n"]); continue
        x.setdefault("tm", ""); x["added"] = TODAY.isoformat()
        j["items"].append(x); have.add((x["u"], x["n"])); n += 1
    json.dump(j, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("足した", n, "件・全部", len(j["items"]), "件")


def bucket(x, t=TODAY):
    n = (datetime.date.fromisoformat(x["d"]) - t).days
    if x["k"] == "close":
        return "close" if n >= 0 else None
    if n >= 0:
        return "soon"
    if x["k"] == "pop" and x.get("end"):
        return "done" if datetime.date.fromisoformat(x["end"]) >= t else None
    return "done" if n >= -DONE_DAYS else None


GEN = [  # (名前, 目印の絵, 言葉)
    ("カフェ", "cup", r"カフェ|CAFE|Cafe|珈琲|コーヒー|喫茶|スタバ|スターバックス|ティー|茶房"),
    ("パン・スイーツ", "cake", r"パン|ベーカリー|ベーグル|スイーツ|ケーキ|洋菓子|和菓子|菓子|カステラ|ドーナツ|チョコ|アイス|クレープ|プリン|まんじゅう|焼き芋|パティスリー"),
    ("ごはん", "bowl", r"ラーメン|らーめん|麺|そば|うどん|寿司|すし|鮨|焼肉|焼鳥|焼き鳥|居酒屋|食堂|レストラン|ダイニング|バル|ビストロ|定食|丼|カレー|パスタ|ピザ|餃子|中華|イタリアン|フレンチ|和食|天ぷら|揚げ|鰻|うなぎ|ステーキ|ハンバーグ|バーガー|酒場|ビュッフェ|料理|グルメ|フード|ごはん|サイゼリヤ|スシロー|くら寿司|王将|丸亀|マクドナルド|肉"),
    ("スーパー・コンビニ", "cart", r"スーパー|マーケット|ローソン|セブン|ファミリーマート|万代|ライフ|イオン(?!モール)|オーケー|ロピア|業務スーパー|コープ|産直|市場|食品館|成城石井|コストコ"),
    ("ドラッグ・薬", "pill", r"ドラッグ|薬局|薬店|調剤|ツルハ|サンドラッグ|ウエルシア|スギ|コスモス|マツキヨ|ココカラ"),
    ("服・雑貨", "bag", r"ファッション|アパレル|服|ドレス|ウェア|バッグ|帽子|時計|ブランド|ジュエリー|アクセサリー|雑貨|インテリア|家具|ニトリ|デコホーム|無印|ユニクロ|GU|しまむら|ワークマン|靴|シューズ|メガネ|眼鏡|DAISO|ダイソー|THREEPPY|Standard Products|キャンドゥ|セリア|3COINS|ショップ|ストア|STORE|SHOP|コムサ|ホームセンター|ホダカ|コーナン|カインズ|ドン・キホーテ|ドンキ|書店|本屋"),
    ("美容・からだ", "spark", r"美容|サロン|THANN|ヘア|ネイル|エステ|コスメ|化粧|ジム|フィットネス|整体|マッサージ|クリニック|歯科|医院|サウナ|スパ|温浴|湯|銭湯"),
    ("遊び・体験", "star", r"ゲーム|GiGO|ギーゴ|アミューズメント|クレーン|カラオケ|ボウリング|体験|ミュージアム|美術館|水族館|映画|シネマ|テーマパーク|キッズ|遊び|プレイ|NICOPA|ラウンジ"),
    ("泊まる", "bed", r"ホテル|旅館|宿|HOTEL|Hotel|ゲストハウス|リゾート"),
    ("施設", "bldg", r"モール|ショッピングセンター|SC|駅ビル|百貨店|商業施設|ルミネ|パルコ|PARCO|ららぽーと|アウトレット|ビル"),
]
ICON = {  # 線の絵（24×24、線1.6）。色は文字の色（夜は night.js が反転）
    "cup": '<path d="M5 9h11v5a5 5 0 0 1-5 5H10a5 5 0 0 1-5-5z"/><path d="M16 10h1.5a2.5 2.5 0 0 1 0 5H16"/><path d="M8 3.5c0 1 1 1.3 1 2.3M11.5 3.5c0 1 1 1.3 1 2.3"/>',
    "cake": '<path d="M4 20h16v-7H4z"/><path d="M4 15c2 1.3 4 1.3 6 0s4-1.3 6 0 3 1.3 4 .5"/><path d="M12 13V9"/><path d="M12 6.5c-.8-.8-.8-2 0-3 .8 1 .8 2.2 0 3z"/>',
    "bowl": '<path d="M3.5 11h17a8.5 8.5 0 0 1-17 0z"/><path d="M9 20h6"/><path d="M14 4l5 5M17 3l3 3"/>',
    "cart": '<path d="M3 4h2.5l2.2 10.5h10.6L20.5 7H7"/><circle cx="9.5" cy="19" r="1.4"/><circle cx="17" cy="19" r="1.4"/>',
    "pill": '<rect x="3.5" y="8.5" width="17" height="7" rx="3.5" transform="rotate(-35 12 12)"/><path d="M9.4 8.3l4.3 6.1"/>',
    "bag": '<path d="M5 8h14l-1 12H6z"/><path d="M9 8V6.5a3 3 0 0 1 6 0V8"/>',
    "spark": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M18.5 16.5l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7z"/>',
    "star": '<path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z"/>',
    "bed": '<path d="M3 18V7M3 14h18v4M21 14v-2.5a3 3 0 0 0-3-3h-7v5.5"/><circle cx="7" cy="11" r="1.8"/>',
    "bldg": '<path d="M4 20V8l8-4 8 4v12z"/><path d="M9 20v-5h6v5M8 10h2M14 10h2"/>',
    "pin": '<path d="M12 21s-6.5-6-6.5-11a6.5 6.5 0 0 1 13 0c0 5-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>',
    "shop": '<path d="M4 9.5L5.5 4h13L20 9.5"/><path d="M4 9.5a2.7 2.7 0 0 0 5.3 0 2.7 2.7 0 0 0 5.4 0 2.7 2.7 0 0 0 5.3 0"/><path d="M5.5 12v8h13v-8M10 20v-4h4v4"/>',
}


def genre(x):
    if x.get("g"):
        for nm, ic, _ in GEN:
            if nm.startswith(x["g"][:2]) or x["g"] in nm:
                return nm, ic
        if x["g"] in ("コンビニ",):
            return "スーパー・コンビニ", "cart"
        if x["g"] in ("100円ショップ",):
            return "服・雑貨", "bag"
    t = x["n"] + " " + x.get("pt", "")
    for nm, ic, w in GEN:
        if re.search(w, x["n"]):
            return nm, ic
    for nm, ic, w in GEN:
        if re.search(w, t):
            return nm, ic
    return "その他", "shop"


LBL = {"カフェ": "CAFE", "パン・スイーツ": "SWEETS", "ごはん": "FOOD", "スーパー・コンビニ": "MARKET", "ドラッグ・薬": "DRUG",
       "服・雑貨": "SHOP", "美容・からだ": "BEAUTY", "遊び・体験": "PLAY", "泊まる": "HOTEL", "施設": "MALL", "その他": "SHOP"}
# おでかけのカード（assets/cardmark.js）と同じ府県の色
PCM = {"大阪": "#B97A62", "京都": "#8A7495", "兵庫": "#4F6681", "奈良": "#6F8C68", "滋賀": "#5F8F98", "和歌山": "#C4925A",
       "東京": "#4F86C6", "群馬": "#9C7BB8", "栃木": "#D2697E", "千葉": "#D9775A", "埼玉": "#E09A3E", "神奈川": "#3FA3B5", "茨城": "#5FA06A"}


def svg(ic, c="gi"):
    return f'<svg class="{c}" viewBox="0 0 24 24" aria-hidden="true">{ICON[ic]}</svg>'


HATSU = re.compile(r"(関東|首都圏|東日本|日本|国内|東京|都内|神奈川|横浜|埼玉|千葉|茨城|栃木|群馬|渋谷|新宿|銀座|池袋|[^\s「」、。・]{1,4}[府県市])初(?:出店|上陸|進出)?|初出店|初上陸|1号店|一号店")


def hatsu(x):
    m = HATSU.search(x.get("pt", "") + " " + x["n"])
    if not m:
        return ""
    t = m.group(0)
    return t if len(t) <= 6 else (m.group(1) + "初" if m.group(1) else "初出店")


def card(x):
    q = urllib.parse.quote(re.sub(r"（.*?）|「|」", " ", x["n"]) + " " + (x["pl"].split("・")[0] or x["p"]))
    end = f' data-end="{x["end"]}"' if x.get("end") else ""
    g, ic = genre(x)
    d = datetime.date.fromisoformat(x["d"])
    lab = KL[x["k"]] if not x.get("sub") else x["sub"]
    pl = x.get("pl") or ""
    stn = ""
    m = re.search(r"・?([^・]{1,14}駅から徒歩\d+分)", pl)
    if m:
        stn, pl = m.group(1), pl.replace(m.group(0), "")
    key = re.sub(r"\W", "", x["n"])[:24] + x["d"]
    fz = x.get("fuzzy")
    md = (re.sub(r"^\d{4}年", "", fz) if fz else f"{d.month}/{d.day}")
    wd = "" if fz else "月火水木金土日"[d.weekday()]
    ch = "1" if x.get("src") in ("lawson", "daiso") or x.get("g") in ("コンビニ", "100円ショップ") else ""
    h1 = hatsu(x)
    aid = "k" + str(abs(hash(key)) % 10**8) if False else "k-" + re.sub(r"[^0-9A-Za-z]", "", urllib.parse.quote(key))[-16:]
    place = E(x["p"]) + (("・" + E(pl.strip("・ "))) if pl.strip("・ ") else "")
    return (f'<article class="it k-{x["k"]}" id="{aid}" data-d="{x["d"]}" data-k="{x["k"]}" data-p="{x["p"]}" data-g="{g}" data-id="{E(key)}"{end}'
            + (' data-ch="1"' if ch else "") + (' data-h="1"' if h1 else "") +
            f' data-s="{E((x["n"] + " " + x["pl"] + " " + x["p"] + " " + g).lower())}">'
            # 11/17 オーナー「おでかけ先の横にロゴつけてたけど開店閉店はなし？」→ おでかけと同じ絵のタイル（下に FOOD などの英字）＋日付の札＋あと何日
            f'<div class="dc cmb" style="--pc:{PCM.get(x["p"], "#8a8f98")}"><div class="ib"><svg viewBox="0 0 24 24">{ICON[ic]}</svg><span class="lb">{LBL.get(g, "SHOP")}</span></div>'
            f'<div class="dd{" tx" if fz else ""}"><b>{E(md)}</b>' + (f'<small class="ddw">{wd}</small>' if wd else "") + '</div><span class="cdn left"></span></div>'
            f'<div class="bd"><div class="tp"><span class="gn">{svg(ic)}{E(g)}</span><span class="tag {x["k"]}">{E(lab)}</span>'
            + (f'<span class="hs">{E(h1)}</span>' if h1 else "") + '</div>'
            f'<h3 class="nm"><a href="{E(x["u"])}" target="_blank" rel="noopener" data-k="公式の発表｜{E(x["n"])}">{E(x["n"])}</a></h3>'
            f'<p class="pt">{E(x["pt"])}</p>'
            f'<p class="mt">{svg("pin", "mi")}<span>{place}{(" ・ " + E(stn)) if stn else ""}{("<i>" + E(x["tm"]) + "</i>") if x.get("tm") else ""}</span></p>'
            '<div class="ln">'
            f'<a class="src" href="{E(x["u"])}" target="_blank" rel="noopener" data-k="公式の発表｜{E(x["n"])}">公式の発表 ↗</a>'
            f'<a class="mpl" href="https://www.google.com/maps/search/?api=1&amp;query={q}" target="_blank" rel="noopener" data-k="地図｜{E(x["n"])}">地図</a>'
            f'<button type="button" class="sh" data-k="送る｜{E(x["n"])}">送る</button>'
            f'<button type="button" class="fv" aria-pressed="false" aria-label="保存" data-k="保存｜{E(x["n"])}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></svg></button>'
            '</div></div></article>')



CSS = """<style>
body{margin:0;background:#fff;color:#2B2622;font-family:"Zen Kaku Gothic New",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:480px;margin:0 auto;padding:0 16px 120px}
.head{text-align:center;padding:30px 0 6px}.head img{border-radius:50%}
.en{font-family:Jost,sans-serif;font-weight:300;font-size:10px;letter-spacing:.42em;color:#8C7B6E;margin-top:8px}
h1{font-family:"Shippori Mincho",serif;font-weight:600;font-size:25px;line-height:1.5;letter-spacing:.1em;color:#231E1B;margin:12px 0 8px;font-feature-settings:"palt"}
h1 span{display:block;font-size:14px;letter-spacing:.08em;color:#6B6058;margin-top:2px}
.sub{font-size:13px;line-height:2;color:#6B6058;margin:0}
.upd{font-size:11px;letter-spacing:.08em;color:#8C7B6E;margin-top:10px}
.note{font-size:12px;line-height:1.9;color:#6B6058;background:#F7F5F2;border-radius:10px;padding:14px 16px;margin-top:24px}
.kfol{margin-top:18px;text-align:center}.kfol p{font-size:13px;line-height:1.9;color:#6B6058;margin:0 0 10px}
.kfol a{display:inline-block;margin:0 4px 8px;font-size:13px;font-weight:700;text-decoration:none;border-radius:99px;padding:9px 16px;background:#2B2622;color:#fff}
.kfol a+a{background:#fff;color:#2B2622;box-shadow:inset 0 0 0 1px #2B2622}
.also{margin-top:22px}.also small{display:block;font-size:11px;letter-spacing:.14em;color:#8C7B6E;margin-bottom:8px}
.also a{display:inline-block;margin:0 8px 8px 0;padding:7px 13px;border:1px solid #D9D2CB;border-radius:99px;color:#2B2622;text-decoration:none;font-size:12.5px}
.back{display:block;text-align:center;border:1px solid #2B2622;border-radius:12px;padding:13px 16px;margin:18px 0 10px;color:#2B2622;text-decoration:none;font-weight:700;font-size:14px}
.sign{text-align:center;font-family:Jost,sans-serif;font-size:11px;letter-spacing:.3em;color:#8C7B6E}
</style>"""


NCSS = ("<style>"
       # 上に固定の絞り込み（見るもの・府県・ジャンル・探す）。高さは合わせて約150px
       ".kbar{position:sticky;top:0;z-index:20;background:#fff;margin:14px -16px 0;padding:10px 16px 8px;border-bottom:1px solid #E6E0D9}"
       ".kbar2{margin:0 -16px;padding:2px 16px 4px}"
       ".seg{display:grid;grid-template-columns:repeat(3,1fr);background:#F1EEEA;border-radius:10px;padding:3px}"
       ".seg button{font:700 13px 'Zen Kaku Gothic New',sans-serif;letter-spacing:.04em;border:0;background:transparent;color:#8C7B6E;padding:8px 0;border-radius:8px;cursor:pointer}"
       ".seg button b{font:500 12px Jost,sans-serif;margin-left:5px;font-variant-numeric:tabular-nums}"
       ".seg button[aria-pressed=true]{background:#fff;color:#2B2622;box-shadow:0 1px 2px rgba(0,0,0,.08)}"
       ".row{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;margin:8px -16px 0;padding:0 16px}.row::-webkit-scrollbar{display:none}"
       ".row button{flex:none;display:inline-flex;align-items:center;gap:4px;font:700 12.5px 'Zen Kaku Gothic New',sans-serif;letter-spacing:.04em;color:#6B6058;background:#fff;border:1px solid #E1D9CF;border-radius:99px;padding:6px 12px;cursor:pointer}"
       ".row button small{font:500 11px Jost,sans-serif;color:#A2958A}"
       ".row button[aria-pressed=true]{background:#2B2622;border-color:#2B2622;color:#fff}.row button[aria-pressed=true] small{color:#D9D2CA}"
       ".row button .gi{width:15px;height:15px}"
       ".sch{display:flex;align-items:center;gap:8px;margin-top:8px;background:#F7F5F2;border-radius:10px;padding:0 12px}"
       ".sch svg{width:16px;height:16px;flex:none;fill:none;stroke:#8C7B6E;stroke-width:1.8}"
       ".sch input{flex:1;min-width:0;border:0;background:transparent;font:500 16px 'Zen Kaku Gothic New',sans-serif;color:#2B2622;padding:9px 0;outline:none}"
       ".sch input::placeholder{color:#A2958A;font-size:14px}"
       # 見出し（きょう・あした・今週・来週・月）
       ".wk{display:flex;align-items:baseline;gap:8px;font:600 15px/1.4 'Shippori Mincho',serif;letter-spacing:.1em;color:#231E1B;margin:22px 0 2px;padding-bottom:6px;border-bottom:1px solid #2B2622}"
       ".wk small{font:400 11.5px 'Zen Kaku Gothic New',sans-serif;letter-spacing:.04em;color:#8C7B6E}"
       # 1件
       ".it{display:grid;grid-template-columns:72px 1fr;gap:0 10px;padding:12px 0 8px;border-top:1px solid #EFEAE4}.wk+.it{border-top:0}"
       # 絵のタイルと札の形は assets/cardmark.js の .cmb をそのまま使う（昼・夜とも）。ここでは置き場所だけ
       "html body .it .dc.cmb{position:static;width:72px;text-align:center;padding-top:2px}"
       "html body .it .dc .ib{width:60px;height:60px;border-radius:20px}html body .it .dc .ib svg{width:30px;height:30px}"
       "html body .it .dc .dd{margin-top:-10px}"
       "html body .it .dc .cdn:empty{display:none}"
       ".bd{min-width:0}.tp{display:flex;align-items:center;gap:6px;flex-wrap:wrap}"
       ".gn{display:inline-flex;align-items:center;gap:4px;font-size:11px;font-weight:700;color:#6B6058;letter-spacing:.04em}"
       ".gi,.mi{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round;flex:none}"
       ".tag{font-size:10.5px;font-weight:700;letter-spacing:.06em;border-radius:4px;padding:1px 6px}"
       ".tag.open{color:#3E6B57;background:#E8F0EB}.tag.pop{color:#7A5A2E;background:#F3ECE0}.tag.close{color:#77706A;background:#EEEBE8}"
       ".nm{font-family:'Shippori Mincho',serif;font-weight:600;font-size:16px;line-height:1.55;letter-spacing:.03em;color:#231E1B;margin:4px 0 0;word-break:auto-phrase}"
       ".nm a{color:inherit;text-decoration:none}"
       ".pt{font-size:12.5px;line-height:1.7;color:#4A423C;margin:2px 0 0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}"
       ".mt{display:flex;gap:4px;align-items:flex-start;margin:4px 0 0;font-size:11.5px;line-height:1.6;color:#6B6058}.mt span{min-width:0;overflow-wrap:anywhere}"
       ".mt i{display:block;font-style:normal}.mt i::before{content:'営業';font-size:10px;color:#A2958A;letter-spacing:.06em;margin-right:6px}"
       ".mt .mi{width:13px;height:13px;margin-top:3px;color:#A2958A}"
       ".ln{display:flex;align-items:center;gap:2px;margin:4px 0 -6px -8px}"
       ".ln a,.ln .sh{font:700 12px 'Zen Kaku Gothic New',sans-serif;color:#7A5230;text-decoration:none;background:none;border:0;padding:8px;line-height:1;cursor:pointer}"
       ".hs{font-size:10.5px;font-weight:700;color:#7A5230;border:1px solid #CDB59E;border-radius:4px;padding:0 5px;letter-spacing:.04em}"
       ".it.same .dc .dd,.it.same .dc .cdn{visibility:hidden}.it.same{border-top:0}"
       ".chn{display:block;width:100%;text-align:left;font:700 12.5px 'Zen Kaku Gothic New',sans-serif;color:#6B6058;background:#F7F5F2;border:0;border-radius:8px;padding:11px 14px;margin:10px 0 2px;cursor:pointer}"
       ".chn b{color:#2B2622}.chn::after{content:'＋';float:right;color:#A2958A}.chn.on::after{content:'－'}"
       ".sum{font-size:12px;color:#6B6058;margin:12px 0 0;letter-spacing:.02em}.sum b{font:500 15px Jost,sans-serif;color:#231E1B;margin:0 2px}"
       # このページだけ頭を小さく（飾りの丸と色はそのまま）
       ".head{padding:16px 16px 6px!important}.head img{width:40px!important;height:40px!important}.head .sub,.head .en{display:none}.head h1{font-size:22px}.head h1 span{font-size:12px}"
       ".fv{margin-left:auto;width:36px;height:36px;border:0;background:none;padding:6px;cursor:pointer;color:#A2958A}"
       ".fv svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:1.6}.fv[aria-pressed=true]{color:#B5643F}.fv[aria-pressed=true] svg{fill:currentColor}"
       # 閉まるお店は静かに（赤は使わない）
       ".k-close .nm,.k-close .pt{color:#6B6058}.k-close .dc .ib{filter:grayscale(.7);opacity:.75}"
       ".it[hidden],.wk[hidden]{display:none}"
       ".more{display:block;width:100%;margin:14px 0 0;font:700 13px 'Zen Kaku Gothic New',sans-serif;color:#2B2622;background:#fff;border:1px solid #2B2622;border-radius:2px;padding:13px;cursor:pointer}"
       ".kempty{font-size:13px;line-height:1.9;color:#6B6058;text-align:center;padding:36px 0;display:none}.kempty button{margin-top:10px;font:700 12.5px 'Zen Kaku Gothic New',sans-serif;border:1px solid #2B2622;background:#fff;border-radius:99px;padding:8px 14px;cursor:pointer}"
       ".kfol{margin-top:18px;text-align:center}.kfol p{font-size:13px;line-height:1.9;color:#6B6058;margin:0 0 10px}"
       ".kfol a{display:inline-block;margin:0 4px 8px;font-size:13px;font-weight:700;text-decoration:none;border-radius:99px;padding:9px 16px;background:#2B2622;color:#fff}"
       ".kfol a+a{background:#fff;color:#2B2622;box-shadow:inset 0 0 0 1px #2B2622}"
       "@media(min-width:700px){.it{grid-template-columns:80px 1fr}}"
       "</style>")

def make_top(cnt, gcount, days_html, live):
    TOP = ('<div class="kbar"><div class="seg" role="group" aria-label="見るもの"><button type="button" data-v="soon" aria-pressed="true">これから<b id="n-soon">%d</b></button>'
           '<button type="button" data-v="done" aria-pressed="false">開いた<b id="n-done">%d</b></button><button type="button" data-v="close" aria-pressed="false">閉まる<b id="n-close">%d</b></button></div>'
           % (cnt["soon"], cnt["done"], cnt["close"])
           + '<div class="row" id="kpref" role="group" aria-label="都県"><button type="button" data-p="" aria-pressed="true">関東すべて</button>'
           + "".join(f'<button type="button" data-p="{p}" aria-pressed="false">{p}<small></small></button>' for p in PREFS if any(x["p"] == p for x in live))
           + '<button type="button" data-p="♡" aria-pressed="false">♡ 保存<small id="n-fav"></small></button></div></div>'
           '<div class="kbar2"><div class="row" id="kgen" role="group" aria-label="ジャンル"><button type="button" data-g="" aria-pressed="true">ぜんぶ</button>'
           + "".join(f'<button type="button" data-g="{g}" aria-pressed="false">{svg(ic)}{g}</button>' for g, ic, _ in GEN + [("その他", "shop", "")] if gcount.get(g))
           + '</div><label class="sch"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg>'
           '<input id="kq" type="search" placeholder="お店・駅・街の名前で探す" enterkeyhint="search" autocomplete="off"></label></div>'
           '<p class="sum" id="ksum"></p>'
           f'<main id="klist">{days_html}<button type="button" class="more" id="kmore" hidden>もっと見る</button>'
           '<div class="kempty" id="kempty"><p>この条件のお店は、いまはありません。</p><button type="button" id="kreset">条件をすべて外す</button></div></main>')
    return TOP


JS = ('<script>(function(){var O=false;try{O=localStorage.getItem("usagi_owner")==="1";}catch(e){}'
      'function c(k){if(O)return;try{var b=JSON.stringify({k:k});if(!(navigator.sendBeacon&&navigator.sendBeacon("/c",b)))fetch("/c",{method:"POST",body:b,keepalive:true});}catch(e){}}'
      'c("表示：開店・閉店ニュース"+(document.referrer&&!/townnote\\.(pages|app)|life-notes|lifenote/.test(document.referrer)?"（外から）":""));'
      'document.addEventListener("click",function(e){var a=e.target.closest?e.target.closest("[data-k]"):null;if(a)c("クリック：開店・閉店ニュース｜"+a.getAttribute("data-k"));});'
      'var N=new Date();N=new Date(N.getTime()+(N.getTimezoneOffset()+540)*6e4);var T=N.getFullYear()+"-"+("0"+(N.getMonth()+1)).slice(-2)+"-"+("0"+N.getDate()).slice(-2);'
      'function dd(a){return Math.round((new Date(a+"T00:00:00")-new Date(T+"T00:00:00"))/864e5)}'
      'var DOW=(N.getDay()+6)%%7;'
      'function bk(x){var n=dd(x.dataset.d),k=x.dataset.k;if(k==="close")return n>=0?"close":"";if(n>=0)return "soon";if(k==="pop"&&x.dataset.end)return dd(x.dataset.end)>=0?"done":"";return n>=-%d?"done":""}'
      # 見出し：これから・閉まる＝きょう/あした/今週/来週/月ごと、開いた＝きょう/この1週間/それより前
      'function hd(x){var n=dd(x.dataset.d),m=+x.dataset.d.slice(5,7);if(view==="done"){return n===0?["きょう",""]:n>=-7?["この1週間",""]:["それより前",""]}'
      'if(n===0)return["きょう",""];if(n===1)return["あした",""];if(n<=6-DOW)return["今週","日曜まで"];if(n<=13-DOW)return["来週",""];return[m+"月",""]}'
      'var view="soon",pref="",gen="",q="",lim=40,FV={};try{FV=JSON.parse(localStorage.getItem("kaiten_fav")||"{}")}catch(e){}'
      'var L=document.getElementById("klist"),I=[].slice.call(L.querySelectorAll(".it")),M=document.getElementById("kmore"),EM=document.getElementById("kempty");'
      'I.forEach(function(x){var b=x.querySelector(".fv");if(FV[x.dataset.id])b.setAttribute("aria-pressed","true");b.onclick=function(){var on=b.getAttribute("aria-pressed")!=="true";b.setAttribute("aria-pressed",on);if(on)FV[x.dataset.id]=1;else delete FV[x.dataset.id];try{localStorage.setItem("kaiten_fav",JSON.stringify(FV))}catch(e){}cnt()}});'
      # 送る：スマホの共有（LINE など）。無ければ LINE の送る画面。送る先はこのページの、そのお店の所
      'I.forEach(function(x){var b=x.querySelector(".sh");b.onclick=function(){var t=x.querySelector(".nm").textContent+"（"+x.querySelector(".dd b").textContent+" "+x.querySelector(".tag").textContent+"）",u=location.origin+location.pathname+"#"+x.id;'
      'if(navigator.share){navigator.share({title:t,text:t,url:u}).catch(function(){})}else{window.open("https://line.me/R/share?text="+encodeURIComponent(t+" "+u),"_blank","noopener")}}});'
      'if(location.hash){var tg=document.getElementById(location.hash.slice(1));if(tg){var b0=tg.dataset;setTimeout(function(){view=bk(tg)||"soon";[].forEach.call(document.querySelectorAll(".seg button"),function(y){y.setAttribute("aria-pressed",y.dataset.v===view)});pref="";go();tg.hidden=false;tg.scrollIntoView({block:"center"});tg.style.background="#FBF6EE"},50)}}'
      'function cnt(){var n=0;for(var k in FV)n++;document.getElementById("n-fav").textContent=n?n:""}'
      'function go(){[].slice.call(L.querySelectorAll(".wk")).forEach(function(h){h.remove()});var c={soon:0,done:0,close:0},pc={},sh=[];'
      'I.forEach(function(x){delete x.dataset.vis;var b=x.dataset.b=bk(x);if(b)c[b]++;if(b===view)pc[x.dataset.p]=(pc[x.dataset.p]||0)+1;'
      'var ok=b===view&&(!pref||(pref==="♡"?FV[x.dataset.id]:x.dataset.p===pref))&&(!gen||x.dataset.g===gen)&&(!q||x.dataset.s.indexOf(q)>=0);x.hidden=true;if(ok)sh.push(x);'
      'var n=dd(x.dataset.d),l=x.querySelector(".left");l.textContent=x.dataset.k==="pop"&&n<0&&x.dataset.end?"〜"+(+x.dataset.end.slice(5,7))+"/"+(+x.dataset.end.slice(8)):n===0?"きょう":n>0?"あと"+n+"日":"オープンから"+(-n)+"日";l.className="cdn left"+(n>=0&&n<=7?" hot":"")});'
      'sh.sort(function(a,b){return view==="done"?(a.dataset.d<b.dataset.d?1:-1):(a.dataset.d<b.dataset.d?-1:a.dataset.d>b.dataset.d?1:0)});'
      # チェーン（コンビニ・100円ショップ）は見出しごとに1行にまとめる。ジャンルで選んだ時・探す時はそのまま出す
      'var fold=!gen&&!q&&pref!=="♡";[].slice.call(L.querySelectorAll(".chn")).forEach(function(b){b.remove()});'
      'var last="",pd="",cb=null,cn=0;function endg(){if(cb){cb.innerHTML="コンビニ・100円ショップの新店 <b>"+cn+"件</b>";}}'
      'sh.forEach(function(x,i){if(i>=lim)return;var h=hd(x);if(h[0]!==last){endg();cb=null;cn=0;last=h[0];pd="";var w=document.createElement("h2");w.className="wk";w.innerHTML=h[0]+(h[1]?"<small>"+h[1]+"</small>":"");L.insertBefore(w,M)}'
      'if(fold&&x.dataset.ch){if(!cb){cb=document.createElement("button");cb.type="button";cb.className="chn";cb.dataset.g=last;cb.onclick=function(){var on=!this.classList.contains("on");this.classList.toggle("on",on);var g=this.dataset.g;I.forEach(function(y){if(y.dataset.ch&&y.dataset.grp===g&&y.dataset.vis)y.hidden=!on})};L.insertBefore(cb,M)}cn++;x.dataset.grp=last;x.dataset.vis="1";x.hidden=true;L.insertBefore(x,M);return}'
      'x.hidden=false;x.classList.toggle("same",x.dataset.d===pd);pd=x.dataset.d;L.insertBefore(x,M)});endg();'
      'var wk=0,hs=0;I.forEach(function(x){if(x.dataset.b==="soon"&&dd(x.dataset.d)<=6-DOW&&(!pref||x.dataset.p===pref)){wk++;if(x.dataset.h)hs++}});'
      'document.getElementById("ksum").innerHTML=view==="soon"?"今週オープン<b>"+wk+"</b>件"+(hs?"・うち初出店など<b>"+hs+"</b>件":""):view==="done"?"この30日に開いたお店<b>"+c.done+"</b>件":"閉まるお店<b>"+c.close+"</b>件";'
      'M.hidden=sh.length<=lim;M.textContent="もっと見る（あと"+(sh.length-lim)+"件）";EM.style.display=sh.length?"none":"block";'
      '["soon","done","close"].forEach(function(k){document.getElementById("n-"+k).textContent=c[k]});'
      '[].forEach.call(document.querySelectorAll("#kpref button"),function(b){var s=b.querySelector("small");if(s&&b.dataset.p!=="♡")s.textContent=pc[b.dataset.p]||"0"});cnt()}'
      'function grp(id,key,set){[].forEach.call(document.querySelectorAll(id+" button"),function(b){b.onclick=function(){set(b.dataset[key]);lim=40;[].forEach.call(document.querySelectorAll(id+" button"),function(x){x.setAttribute("aria-pressed",x===b)});go();c("開店・閉店｜"+(b.textContent||"").replace(/\\d+$/,""))}})}'
      'grp(".seg","v",function(v){view=v});grp("#kpref","p",function(v){pref=v;try{localStorage.setItem("kaiten_pref",v)}catch(e){}});grp("#kgen","g",function(v){gen=v});'
      'var qi=document.getElementById("kq"),qt;qi.oninput=function(){clearTimeout(qt);qt=setTimeout(function(){q=qi.value.trim().toLowerCase();lim=40;go();if(q)c("開店・閉店｜探す")},200)};'
      'M.onclick=function(){lim+=40;go()};document.getElementById("kreset").onclick=function(){q="";qi.value="";["#kpref","#kgen"].forEach(function(id){var f=document.querySelector(id+" button");f&&f.click()})};'
      # 前に選んだ府県を覚える（おでかけと同じ）
      'try{var sp=localStorage.getItem("kaiten_pref");if(sp&&sp!=="♡"){var bb=document.querySelector("#kpref button[data-p=\\""+sp+"\\"]");if(bb){pref=sp;[].forEach.call(document.querySelectorAll("#kpref button"),function(x){x.setAttribute("aria-pressed",x===bb)})}}}catch(e){}'
      'go();})();</script>') % DONE_DAYS


def build():
    items = json.load(open(DATA, encoding="utf-8"))["items"]
    live = [x for x in items if bucket(x)]
    for x in live:
        assert x["p"] in PREFS, x["n"]
    cnt = {k: sum(bucket(x) == k for x in live) for k in ("soon", "done", "close")}
    gcount = {}
    for x in live:
        gcount[genre(x)[0]] = gcount.get(genre(x)[0], 0) + 1
    body = "".join(card(x) for x in sorted(live, key=lambda x: (x["d"], x["k"] != "close", x["n"])))  # 見出し（きょう・今週…）は JS が入れる
    N = len(live)
    k = open(os.path.join(SITE, "koyo.html"), encoding="utf-8").read()
    head = k[:k.index("</head>")]
    head = re.sub(r"<style>.*?</style>", "", head, flags=re.S)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>', "", head, flags=re.S)
    head = re.sub(r'<link rel="stylesheet" href="/assets/sub.css[^>]*>|<script src="/assets/yado.js[^>]*></script>', "", head)
    title = f"関東の開店・閉店ニュース｜新しいお店・閉まるお店を公式の発表で（{TODAY.month}月{TODAY.day}日）"
    desc = (f"東京・神奈川・埼玉・千葉など関東で、これから開くお店{cnt['soon']}件・この{DONE_DAYS}日に開いたお店{cnt['done']}件・閉まるお店{cnt['close']}件。"
            "各社の公式の発表だけを毎日たしかめて足しています。日付・場所と、公式の発表と地図へすぐ行けます。")
    head = re.sub(r"<title>.*?</title>", f"<title>{E(title)}</title>", head, count=1)
    for p in ('name="description"', 'property="og:description"'):
        head = re.sub(rf'(<meta {p} content=")[^"]*', lambda m: m.group(1) + E(desc), head, count=1)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + "関東の開店・閉店ニュース", head, count=1)
    head = re.sub(r'(<meta property="article:modified_time" content=")[^"]*', lambda m: m.group(1) + TODAY.isoformat() + "T07:00:00+09:00", head, count=1)
    head = re.sub(r'(<link rel="canonical" href="[^"]*?/)koyo"', r'\1kaiten"', head, count=1)
    head = re.sub(r'(<meta property="og:url" content="[^"]*?/)koyo"', r'\1kaiten"', head, count=1)
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": "関東の開店・閉店ニュース",
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": x["n"], "url": x["u"]} for i, x in enumerate(sorted(live, key=lambda x: x["d"]))]},
          {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "関東おでかけリスト", "item": BASE + "odekake"},
              {"@type": "ListItem", "position": 2, "name": "関東の開店・閉店ニュース", "item": BASE + "kaiten"}]}]
    head += CSS + NCSS + "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in ld)
    top = make_top(cnt, gcount, body, live)
    s = (head + '</head><body data-kind="開店・閉店ニュース"><div class="wrap"><header class="head"><img src="/logo.png" width="60" height="60" alt="LIFE NOTE のロゴ">'
         '<h1>関東の開店・閉店ニュース<span>新しいお店・閉まるお店を公式の発表で</span></h1>'
         '<p class="sub">お店や施設の公式の発表だけを、毎日たしかめて足しています。<br>日付と街で、近くの新しいお店がすぐ分かります。</p>'
         f'<div class="upd">{TODAY.year}年{TODAY.month}月{TODAY.day}日 更新・{N}件</div></header>' + top
         + '<p class="note">日付・時間・内容は、各社の公式の発表をもとにしています。変わることがあるので、出かける前に「公式の発表」で確かめてください。閉店のセールの日数や値引きの中身は、発表に書かれた物だけを載せています。</p>'
         '<div class="kfol"><p>新しいお店の速報は、毎日 X にも出しています。</p><a href="https://x.com/ai_usagichan" target="_blank" rel="noopener" data-k="速報｜Xで毎日見る">X で毎日見る</a>'
         '<a href="https://www.threads.com/@usagichan_ai_si" target="_blank" rel="noopener" data-k="速報｜Threadsで見る">Threads で見る</a></div>'
         '<nav class="also" aria-label="あわせて見る"><small>あわせて見る</small><a href="/odekake" data-k="あわせて：おでかけリスト">関東おでかけリスト</a>'
         '<a href="/ima" data-k="あわせて：いま行ける">今から行ける所</a><a href="/illumination" data-k="あわせて：イルミネーション">関東のイルミネーション</a></nav>'
         '<a class="back" href="/odekake">関東おでかけリストを見る</a><p class="sign">LIFE NOTE</p></div>' + JS + "</body></html>")
    assert "紅葉" not in s[s.index("<body"):], "紅葉の言葉が残っている"
    open(os.path.join(SITE, "kaiten.html"), "w", encoding="utf-8").write(s)
    sm = os.path.join(SITE, "sitemap.xml")
    if os.path.exists(sm):
        x = open(sm, encoding="utf-8").read()
        if "/kaiten<" not in x:
            open(sm, "w", encoding="utf-8").write(x.replace("</urlset>", f"<url><loc>{BASE}kaiten</loc><lastmod>{TODAY}</lastmod></url></urlset>", 1))
    print("kaiten", N, cnt)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "add":
        add(sys.argv[2:])
    build()
