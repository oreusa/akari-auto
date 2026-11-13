"""漏れの見張り（10/29 オーナー「もっと全てミスないか常に確認しろ」）。
予約係（book.yml、2時間おき）の最後に動き、notes/miss.md に「いま直っていない物」を全部書く。
朝の見回り・夜の見回り・集め係・夜の回は、最初に notes/miss.md を読み、×の行を全部直してから自分の仕事をする。
見る物：①今日・明日の予定表と4コマ・おでかけリール ②記録の×で、あとから予約OK・出たが無い物
③HPの在庫の× ④地図のピンが出ないカード ⑤開かないリンク（重いだけは除く）⑥動かなかった機械（GitHub Actions）
⑦売上0とHPクリック0の続いた日数 ⑧使える量（Actions の分数・Buffer の残り・HPの数えの上限）。
読むだけで何も直さない（直すのは見回りの燈）。しっぱいしても予約は止めない。"""
import datetime as dt, glob, json, os, re, sys, urllib.request

JST = dt.timezone(dt.timedelta(hours=9))
OUT = 'notes/miss.md'
BAD = ('×', '出なかった', '中止', 'しっぱい', '失敗')
GOOD = ('予約OK', '出た', '予約済', '直した', '出し直しOK')
SKIP = ('リール直接', '試し')  # 直接投稿は止めていて Buffer で出る（10/29）。ここで数えると毎回×が残る


def load(p, d=None):
    try:
        return json.load(open(p, encoding='utf-8'))
    except Exception:
        return d


def files(now):
    out = []
    today, tmr = now.date().isoformat(), (now.date() + dt.timedelta(days=1)).isoformat()
    days = [today] + ([tmr] if now.hour >= 23 else [])  # 明日の分は夜の回（22:11）のあとから見る
    for d in days:
        s = load(f'schedule/{d}.json')
        if not s:
            out.append(f'予定表 schedule/{d}.json が無い')
        else:
            n = len(s.get('posts', []))
            need = 7 if d >= '2026-11-14' else 5 if d >= '2026-11-13' else 9  # 11/14 から1日7本＝関西と同じ6本＋PR1本（オーナー 11/13「一緒で、ってお願いしたはず」「関東はもう1本増やしてpr載せないと」）
            if n < need:
                out.append(f'予定表 {d} の投稿が{n}本（決まりは{need}本）')
        if d < '2026-11-13' and not os.path.exists(f'koma4/{d}.json'):  # 11/13 から4コマはやめた（オーナー 11/12）
            out.append(f'4コマ koma4/{d}.json が無い')
        if d >= '2026-10-30':  # 07:30 の関東おでかけリール（10/30から）
            if os.path.exists(f'reel-hp/{d}.json'):  # 11/2 HPリールの日は、おでかけリールを翌週に回す
                if not (load(f'reel-hp/out/{d}.json') or {}).get('url') and (d != today or now.hour < 18):
                    out.append(f'HPリールの動画 reel-hp/out/{d}.json に url が無い（hp-reel.yml を動かす）')
            elif not os.path.exists(f'reel/{d}.json'):
                out.append(f'おでかけリール reel/{d}.json が無い（docs/outing-reel.md）')
            elif not (load(f'reel/out/{d}.json') or {}).get('url') and (d != today or now.hour < 8):
                out.append(f'おでかけリールの動画 reel/out/{d}.json に url が無い（outing-reel.yml を動かす）')
    # 予備の4コマ（11/11。今日の絵が出せない日に代わりに出す、先に描いてある4コマ。docs/koma4-prompt.md ■必ず出す）
    yb = [load(f) or {} for f in glob.glob('koma4/yobi-*.json')]
    ready = sum(1 for y in yb if y.get('image_url') and not y.get('used'))
    left = sum(1 for y in yb if not y.get('used'))
    if False and ready < 2 and now.date().isoformat() >= '2026-11-15':  # 予備の4コマも要らない（11/12 4コマをやめた）  # 雫が描きためるまでの3日は数えない
        out.append(f'予備の4コマ すぐ出せる物が{ready}本（2本より少ない。台本の残り{left}本）→ 残りが3本より少なければ夜の回で台本を2本足す（docs/nightly-prompt.md）')
    return out


def logs(now):
    """今日と昨日の記録で、最後の状態が×のままの投稿"""
    out = []
    for d in (now.date() - dt.timedelta(days=1), now.date()):
        p = f'log/{d.isoformat()}.md'
        if not os.path.exists(p):
            continue
        last = {}
        for line in open(p, encoding='utf-8'):
            m = re.match(r'- (\d\d:\d\d) (\S+ \S+) (.*)', line.strip())
            if not m or any(k in line for k in SKIP):
                continue
            key, rest = m.group(2), m.group(3)[:30]
            if any(k in rest for k in GOOD):
                last[key] = None
            elif any(k in rest for k in BAD):
                last[key] = f'{d.month}/{d.day} {m.group(1)} {key} {m.group(3)[:60]}'
        out += [v for v in last.values() if v]
    return out


def stock():
    p = 'notes/stock.md'
    if not os.path.exists(p):
        return ['在庫 notes/stock.md が無い']
    t = open(p, encoding='utf-8').read()
    m = re.search(r'^判定：(.*)$', t, re.M)
    if not m or not m.group(1).startswith('×'):
        return []
    n = len(re.findall(r' ×', t.split('## 足りない物')[0]))
    return [f'HPの在庫 ×{n}か所：{m.group(1)[2:150]}']


def geo(now):
    """いまHPにあるカードだけ（ページを作るたびに取れなかった物は日付が今日になる。古い日付は消えたカード）"""
    g = load('data/townnotes-geo.json', {}) or {}
    recent = {(now.date() - dt.timedelta(days=i)).isoformat() for i in range(2)}
    # 11/10 都県の無いカード（「いまが買い時の日用品のページ」などお店のページの案内）は場所ではないので数えない
    none = [k for k, v in g.items() if v and v[0] is None and (v + ['', '', '', ''])[3] in recent and not k.startswith('｜')]
    return [f'地図のピンが出ないカード{len(none)}件：' + '、'.join(k.split('｜')[-1] for k in none[:8])] if none else []


def popular():
    """人気のおでかけの漏れ（notes/popular.md、毎日13:30に機械が書く）"""
    p = 'notes/popular.md'
    if not os.path.exists(p):
        return []
    t = open(p, encoding='utf-8').read()
    rows = re.findall(r'^- × (.*?)(?:｜|$)', t, re.M)
    return [f'HPに無い人気のおでかけ{len(rows)}件：' + '、'.join(r[:30] for r in rows[:8])] if rows else []


def links():
    p = 'notes/linkcheck.md'
    if not os.path.exists(p):
        return []
    sec = open(p, encoding='utf-8').read().split('## 直す所')
    if len(sec) < 2:
        return []
    rows = [l for l in sec[1].split('\n## ')[0].splitlines() if l.startswith('- ') and '｜重い' not in l]
    return [f'リンク（重い以外）{len(rows)}件：' + '、'.join(r[2:].split('（')[0] for r in rows[:6])] if rows else []


def actions(now):
    """この24時間でしっぱいした機械（最後の回が×の物だけ）"""
    tok, repo = os.environ.get('GITHUB_TOKEN'), os.environ.get('GITHUB_REPOSITORY')
    if not tok or not repo:
        return []
    since = (now - dt.timedelta(hours=24)).astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    req = urllib.request.Request(f'https://api.github.com/repos/{repo}/actions/runs?per_page=100&created=%3E{since}',
                                 headers={'Authorization': f'Bearer {tok}', 'Accept': 'application/vnd.github+json'})
    try:
        runs = json.load(urllib.request.urlopen(req, timeout=20)).get('workflow_runs', [])
    except Exception as e:
        return [f'機械の確かめができない（{e}）']
    last = {}
    for r in sorted(runs, key=lambda r: r['created_at']):
        if r.get('status') == 'completed':
            last[r['name']] = r
    out = []
    for name, r in last.items():
        if r.get('conclusion') not in ('success', 'skipped', 'cancelled'):
            t = dt.datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')).astimezone(JST)
            out.append(f'機械 {name} が×（{t:%m/%d %H:%M}）{r["html_url"]}')
    return out


def money(now):
    out = []
    st = load('data/page-stats.json', {}) or {}
    days = sorted((st.get('days') or {}).items())
    n = 0
    for _, v in reversed(days):
        if v.get('clicks'):
            break
        n += 1
    if n >= 3:
        out.append(f'HPの商品クリック0が{n}日続いている')
    p = 'notes/sales-board.md'
    if os.path.exists(p):
        m = re.search(r'成果0の連続：([^。（]*)', open(p, encoding='utf-8').read())
        if m:
            out.append(f'売上：成果0の連続 {m.group(1)}')
    return out


def capacity():
    """使える量（10/29 オーナー「全容量確認」）：GitHub Actions の分数・Buffer の残り・HPの数えの上限"""
    out = []
    if os.path.exists('notes/actions-minutes.md'):
        t = open('notes/actions-minutes.md', encoding='utf-8').read()
        for m in re.finditer(r'^- (判定|来月[^：]*)：(.*)$', t, re.M):
            if '×' in m.group(2).replace('分×30', '') and '公開なので無料' not in m.group(2):  # 11/8 公開リポジトリは無料
                out.append(f'Actions の分数 {m.group(1)}：{m.group(2)[:80]}')
    b = load('state/buffer_limit.json', {}) or {}
    rem = (b.get('headers') or {}).get('x-ratelimit-remaining')
    if rem and int(rem) < 500:
        out.append(f'Buffer の残りが{rem}回（30日で3,000回）')
    st = load('data/page-stats.json', {}) or {}
    for d, v in sorted((st.get('days') or {}).items())[-1:]:
        if (v.get('views') or 0) >= 450 or (v.get('clicks') or 0) >= 270:
            out.append(f'HPの数えが上限に近い（{d} 見られた{v.get("views")}/500・押された{v.get("clicks")}/300）')
    return out


def main():
    now = dt.datetime.now(JST)
    parts = [('予定表・4コマ・リール', files(now)), ('出ていない投稿', logs(now)), ('HPの在庫', stock()), ('人気のおでかけ', popular()), ('地図', geo(now)),
             ('リンク', links()), ('機械', actions(now)), ('売上', money(now)), ('使える量', capacity())]
    n = sum(len(v) for _, v in parts)
    lines = [f'# 漏れの見張り（{now:%m/%d %H:%M} 機械が調べた）', '',
             f'判定：{"×" if n else "○"} {n}件' + ('' if n else '（漏れなし）'), '',
             '見回りの燈・集め係・夜の回は、最初にここを読み、×の行を全部直してから自分の仕事をする。直せない物は理由を基本スレに1行。', '']
    for title, rows in parts:
        lines.append(f'## {title}（{len(rows)}）')
        lines += [f'- × {r}' for r in rows] or ['- ○']
        lines.append('')
    os.makedirs('notes', exist_ok=True)
    body = '\n'.join(lines[1:])
    prev = open(OUT, encoding='utf-8').read().split('\n', 1) if os.path.exists(OUT) else ['', '']
    if len(prev) == 2 and prev[1] == body:
        print('前と同じ（書き直さない）')
        return
    open(OUT, 'w', encoding='utf-8').write(lines[0] + '\n' + body)
    print('\n'.join(lines))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('misscheck しっぱい（予約はそのまま）', e)
        sys.exit(0)
