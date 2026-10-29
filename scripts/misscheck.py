"""漏れの見張り（10/29 オーナー「もっと全てミスないか常に確認しろ」）。
予約係（book.yml、2時間おき）の最後に動き、notes/miss.md に「いま直っていない物」を全部書く。
朝の見回り・夜の見回り・集め係・夜の回は、最初に notes/miss.md を読み、×の行を全部直してから自分の仕事をする。
見る物：①今日・明日の予定表と4コマ・おでかけリール ②記録の×で、あとから予約OK・出たが無い物
③HPの在庫の× ④地図のピンが出ないカード ⑤開かないリンク（重いだけは除く）⑥動かなかった機械（GitHub Actions）
⑦売上0とHPクリック0の続いた日数。
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
            if n < 9:  # 8:00 の4コマは koma4 にあるので、予定表は9本
                out.append(f'予定表 {d} の投稿が{n}本（決まりは4コマと合わせて10本＝予定表9本）')
        if not os.path.exists(f'koma4/{d}.json'):
            out.append(f'4コマ koma4/{d}.json が無い')
        if d >= '2026-10-30':  # 07:30 の関東おでかけリール（10/30から）
            if not os.path.exists(f'reel/{d}.json'):
                out.append(f'おでかけリール reel/{d}.json が無い（docs/outing-reel.md）')
            elif not (load(f'reel/out/{d}.json') or {}).get('url') and (d != today or now.hour < 8):
                out.append(f'おでかけリールの動画 reel/out/{d}.json に url が無い（outing-reel.yml を動かす）')
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
    none = [k for k, v in g.items() if v and v[0] is None and (v + ['', '', '', ''])[3] in recent]
    return [f'地図のピンが出ないカード{len(none)}件：' + '、'.join(k.split('｜')[-1] for k in none[:8])] if none else []


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


def main():
    now = dt.datetime.now(JST)
    parts = [('予定表・4コマ・リール', files(now)), ('出ていない投稿', logs(now)), ('HPの在庫', stock()), ('地図', geo(now)),
             ('リンク', links()), ('機械', actions(now)), ('売上', money(now))]
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
