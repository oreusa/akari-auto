"""人気のおでかけの漏れを見る（10/30 オーナー「おでかけ関係も全部漏れないよな？」）。
ウォーカープラスの都県イベントランキング（上位20＝1ページ目と2ページ目）を毎日読み、
HP（data/page-spots.json と予定表）に無い物を notes/popular.md に×で書く。
14:13の集め係が×を公式ページで確かめて載せるか、載せない理由を data/popular-skip.json に書く。
10/29 東京の上位10のうち、HPにあったのは4件だけだった。"""
import datetime as dt, glob, html, json, os, re, sys, time, unicodedata, urllib.request

JST = dt.timezone(dt.timedelta(hours=9))
PREF = [('東京', '13'), ('神奈川', '14'), ('埼玉', '11'), ('千葉', '12'), ('茨城', '08'), ('栃木', '09'), ('群馬', '10')]
TOP = 20
OUT, SKIP = 'notes/popular.md', 'data/popular-skip.json'
UA = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    s = re.sub(r'[（(][^）)]*[）)]', '', s)  # （東京）などの添え字を外す
    return re.sub(r'[\s・〜~\-ー―!！?？「」『』【】、。,.:：/／&＆]', '', s)


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode('utf-8', 'replace')


def ranking(code):
    """(順位, 名前, URL) を上位から。イベントのページへのリンク /event/ar03..e数字/ の文字を順に拾う"""
    out, seen = [], set()
    for page in ('', '2.html'):
        try:
            h = fetch(f'https://www.walkerplus.com/ranking/event/ar03{code}/{page}')
        except Exception as e:
            print('ranking err', code, page, e)
            continue
        for m in re.finditer(r'<a[^>]+href="((?:https://www\.walkerplus\.com)?/event/ar03\d+e\d+/)"[^>]*>(.*?)</a>', h, re.S):
            url, name = m.group(1), html.unescape(re.sub(r'<[^>]+>', ' ', m.group(2))).strip()
            name = re.sub(r'\s+', ' ', name)
            if url in seen or len(name) < 3:
                continue
            seen.add(url)
            out.append((len(out) + 1, name, url if url.startswith('http') else 'https://www.walkerplus.com' + url))
        time.sleep(1)
    return out[:TOP]


def hp_names():
    names = []
    try:
        for x in json.load(open('data/page-spots.json', encoding='utf-8'))['items']:
            names += [x.get('title', ''), x.get('name', '')]
    except Exception:
        pass
    today = dt.datetime.now(JST).date()
    for f in sorted(glob.glob('schedule/*.json'))[-21:]:
        try:
            for p in json.load(open(f, encoding='utf-8')).get('posts', []):
                names += [p.get('name', ''), ' '.join(p.get('threads') or [])[:200], ' '.join(p.get('x') or [])[:200]]
        except Exception:
            pass
    return [norm(n) for n in names if n]


def found(name, hp):
    k = norm(name)
    # 頭の8字・6字か、空白で区切った日本語の言葉（場所の言葉で合わないよう「in」より前だけ）。英語だけの言葉は使わない（characters などで間違って合う）
    toks = [norm(t) for t in re.split(r'[\s〜~（）()]+', re.split(r'\sin\s?|＠|@', name)[0])]
    keys = [k[:8], k[:6]] + [t for t in toks if not t.isascii()]
    return any(len(n) >= 5 and any(n in h for h in hp) for n in keys if n)


def main():
    hp = hp_names()
    skip = {}
    if os.path.exists(SKIP):
        skip = json.load(open(SKIP, encoding='utf-8'))
    now = dt.datetime.now(JST)
    lines, miss, got = [], 0, 0
    for pref, code in PREF:
        rows = ranking(code)
        got += len(rows)
        lines.append(f'\n## {pref}（上位{len(rows)}件）')
        if not rows:
            lines.append('- × ランキングが読めなかった（集め係が https://www.walkerplus.com/ranking/event/ar03' + code + '/ を自分で見る）')
            miss += 1
            continue
        for rank, name, url in rows:
            if found(name, hp):
                lines.append(f'- ○ {rank}位 {name}')
            elif norm(name)[:8] in skip:
                lines.append(f'- － {rank}位 {name}（載せない：{skip[norm(name)[:8]]}）')
            else:
                lines.append(f'- × {rank}位 {name}｜{url}')
                miss += 1
    head = [f'# 人気のおでかけの漏れ（{now:%m/%d %H:%M} 機械が調べた）', '',
            f'判定：{"×" if miss else "○"} HPに無い人気のおでかけ {miss}件（ウォーカープラスの都県ランキング上位{TOP}、{got}件を照らした）', '',
            '集め係は×を上から全部、公式ページで日付・場所・料金を確かめて data/page-spots.json に足す。',
            '終わった・関東の外・おすすめできない物は、data/popular-skip.json に {"名前の頭8字（記号・空白なし）": "理由"} を書いて外す。']
    os.makedirs('notes', exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write('\n'.join(head + lines) + '\n')
    print('\n'.join(head + lines))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('popular しっぱい', e)
        sys.exit(0)
