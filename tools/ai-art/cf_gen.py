"""リール用の絵を Cloudflare Workers AI（無料 1日10,000 Neurons）で描く。11/23 owner OK「（Cloudflare の鍵を画像AIに）いいよ」。鍵は表に出さない。
使い方: python3 cf_gen.py req.json 出力フォルダ   （req の items を models の各モデルで描く）"""
import base64, json, os, sys, urllib.request, urllib.error
T = os.environ['CLOUDFLARE_API_TOKEN'].strip(); req = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True); log = []
def call(method, path, body=None, ctype='application/json'):
    r = urllib.request.Request('https://api.cloudflare.com/client/v4' + path, method=method, data=body, headers={'Authorization': 'Bearer ' + T, 'Content-Type': ctype})
    try:
        with urllib.request.urlopen(r, timeout=240) as x: return x.status, x.headers.get('Content-Type', ''), x.read()
    except urllib.error.HTTPError as e: return e.code, e.headers.get('Content-Type', ''), e.read()
s, ct, d = call('GET', '/accounts'); j = json.loads(d); accs = [a['id'] for a in j.get('result') or []]
log.append(f'accounts {s} n={len(accs)} err={j.get("errors")}')
A = accs[0] if accs else (os.environ.get('CF_ACCOUNT_ID') or '').strip() or None
models = req.get('models', ['@cf/black-forest-labs/flux-2-klein-4b'])
for it in req['items'] if A else []:
    P = f"{it['prompt']}. {req['style']}"
    for model in models:
        name = f"{it['name']}-{model.split('/')[-1]}"
        if 'flux-2' in model:
            bd = 'xBOUNDARYx'; parts = {'prompt': P, 'width': str(it.get('W', 1088)), 'height': str(it.get('H', 1920))}
            if 'dev' in model: parts['steps'] = '28'
            raw = ''.join(f'--{bd}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n' for k, v in parts.items()) + f'--{bd}--\r\n'
            s, ct, d = call('POST', f'/accounts/{A}/ai/run/{model}', raw.encode(), ctype=f'multipart/form-data; boundary={bd}')
        else:
            s, ct, d = call('POST', f'/accounts/{A}/ai/run/{model}', json.dumps({'prompt': P, 'steps': 8, 'width': it.get('W', 1088), 'height': it.get('H', 1920)}).encode())
        if ct.startswith('image'): open(f'{out}/{name}.jpg', 'wb').write(d); log.append(f'{name} {s} OK {len(d)}'); continue
        try:
            j = json.loads(d); img = (j.get('result') or {}).get('image')
            if img: open(f'{out}/{name}.jpg', 'wb').write(base64.b64decode(img)); log.append(f'{name} {s} OK'); continue
            log.append(f'{name} {s} {str(j.get("errors"))[:300]}')
        except Exception: log.append(f'{name} {s} {ct} {d[:200]!r}')
open(f'{out}/log.txt', 'w').write('\n'.join(log)); print('\n'.join(log))
