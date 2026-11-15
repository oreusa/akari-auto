"""独自ドメイン townnote.app を両方のHPにつなぐ（11/15 オーナーが購入。関西 kansai.townnote.app＝Pages townnote、関東 kanto.townnote.app＝Pages lifenote-kanto）。
鍵は CLOUDFLARE_API_TOKEN。鍵の中身・ID は出さない。足りない権限があれば、その名前だけ出す。"""
import json, os, sys, urllib.request, urllib.error
T = os.environ.get('CLOUDFLARE_API_TOKEN', '')
if not T: sys.exit('鍵がない')
ZONE = 'townnote.app'
MAP = [('kansai.townnote.app', 'townnote'), ('kanto.townnote.app', 'lifenote-kanto')]
DO = os.environ.get('DO', 'status')


def api(path, method='GET', body=None):
    r = urllib.request.Request('https://api.cloudflare.com/client/v4' + path, method=method,
                               data=json.dumps(body).encode() if body is not None else None,
                               headers={'Authorization': 'Bearer ' + T, 'Content-Type': 'application/json'})
    try:
        return json.loads(urllib.request.urlopen(r, timeout=60).read())
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read())
        except Exception: return {'success': False, 'errors': [{'message': f'HTTP {e.code}'}]}


def err(j): return '／'.join(f"{x.get('code','')} {x.get('message','')}" for x in j.get('errors', []))


acc = api('/accounts')
if not acc.get('success'): sys.exit('アカウントを読めない：' + err(acc))
print('アカウント数', len(acc['result']))
A = acc['result'][0]['id']
z = api('/zones?name=' + ZONE)
zid = z['result'][0]['id'] if z.get('success') and z.get('result') else ''
print('ゾーン', ZONE, '見える' if zid else '見えない（鍵にゾーンの権限がない）', (z['result'][0].get('status') if zid else err(z)))
if DO == 'perm':
    for path in ['/user/tokens/verify', f'/accounts/{A}/workers/scripts', f'/accounts/{A}/workers/domains', f'/zones/{zid}/workers/routes', f'/zones/{zid}/settings/ssl']:
        j = api(path); print('権限', path.replace(A, 'A').replace(zid or 'x', 'Z'), 'OK' if j.get('success') else err(j))
for host, proj in MAP:
    p = api(f'/accounts/{A}/pages/projects/{proj}')
    print('Pages', proj, 'ある' if p.get('success') else 'ない：' + err(p))
    if not p.get('success'): continue
    if DO == 'add':
        r = api(f'/accounts/{A}/pages/projects/{proj}/domains', 'POST', {'name': host})
        print('  追加', host, 'OK' if r.get('success') else err(r))
    d = api(f'/accounts/{A}/pages/projects/{proj}/domains')
    for x in d.get('result') or []:
        print('  ドメイン', x.get('name'), x.get('status'), (x.get('validation_data') or {}).get('status', ''), (x.get('verification_data') or {}).get('status', ''))
    if zid:
        rec = api(f'/zones/{zid}/dns_records?name={host}')
        have = rec.get('result') or []
        print('  DNS', host, [(x['type'], x['content'], x.get('proxied')) for x in have] if have else 'なし', '' if rec.get('success') else err(rec))
        if DO == 'add' and not have:
            c = api(f'/zones/{zid}/dns_records', 'POST', {'type': 'CNAME', 'name': host, 'content': proj + '.pages.dev', 'proxied': True, 'ttl': 1})
            print('  DNS 作成', 'OK' if c.get('success') else err(c))
