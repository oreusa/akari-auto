"""おでかけリール（11/11 型：地図 → 縦書きの題と線画 → 声は4か所）を作る。関西・関東で同じファイル。
使い方: python3 tools/outing_reel/make.py spec.json out.mp4 [静止画の時刻,…]
  - spec の欄は README.md（"voice" に声の台本4行：始まり・日付・見どころ・最後の案内）。
  - 声は VOICEVOX（環境変数 VOICE_URL。.github/workflows/outing-reel.yml の中で動く）で作る。
    VOICE_URL が無い所では、先に作った声（shots/voice/reel-<specの名前>/）を使う。
  - spec に "voice" があるのに声を作れない時は止まる（声なしの動画を本番に出さないため）。
    見た目だけ確かめたい時は、静止画の時刻を付けるか NOVOICE=1 を付ける。
  - 場所ごとの違い（表紙の2行・さし色・地図・リストの画面・曲）は region.py。前の型は make_old.py。
"""
import json, os, subprocess, sys, shutil, tempfile, wave, datetime, re, time, urllib.request, urllib.parse
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
sys.path.insert(0, D); import region
spec = json.load(open(sys.argv[1])); OUT = os.path.abspath(sys.argv[2]); STILL = sys.argv[3] if len(sys.argv) > 3 else ''
NAME = os.path.splitext(os.path.basename(sys.argv[1]))[0]
V = os.path.join(ROOT, spec.get('voice_dir', f'shots/voice/reel-{NAME}')); SP = '20'
VOICE = dict(speedScale=1.0, intonationScale=1.2, pitchScale=-0.03, pauseLengthScale=0.8, prePhonemeLength=0.05, postPhonemeLength=0.1)   # 11/11 オーナーが選んだ声（落ち着いた大人の女性を少しだけ低く）
t = spec['text']
px, py = region.xy(spec['lat'], spec['lon'])
W = tempfile.mkdtemp()
for f in ('grain.png', 'logo.png'): shutil.copy(f'{D}/{f}', W)
open(f'{W}/shot.js', 'w').write(region.shot_js(ROOT, spec, W)); subprocess.run(['node', f'{W}/shot.js'], check=True)

# 声を作る（VOICE_URL がある時）
VU = os.environ.get('VOICE_URL', '')
lines = spec.get('voice') or []
if lines and len(lines) != 4: sys.exit('voice は4行（始まり・日付・見どころ・最後の案内）')
if lines and VU:
    def vreq(path, data=None):
        r = urllib.request.Request(VU + path, data=data, method='POST' if data is not None else 'GET', headers={'Content-Type': 'application/json'})
        return urllib.request.urlopen(r, timeout=120).read()
    for i in range(150):
        try: vreq('/version'); break
        except Exception: time.sleep(2)
    V = f'{W}/voice'; os.makedirs(V); kana = []
    for n, line in enumerate(lines):
        q = json.loads(vreq(f'/audio_query?speaker={SP}&text=' + urllib.parse.quote(line), b'')); q.update(VOICE); kana.append(q.get('kana', ''))
        open(f'{V}/{SP}-{n:02d}.wav', 'wb').write(vreq(f'/synthesis?speaker={SP}', json.dumps(q).encode()))
    print('声の読み', kana)

# 声の長さ → 場面の長さ
def dur(n):
    w = wave.open(f'{V}/{SP}-{n:02d}.wav'); return w.getnframes() / w.getframerate()
HASV = bool(lines) and all(os.path.exists(f'{V}/{SP}-{n:02d}.wav') for n in range(4))
if lines and not HASV and not STILL and not os.environ.get('NOVOICE'):
    sys.exit('声を作れない：この動画は .github/workflows/outing-reel.yml が作る（spec を main に入れるだけ）。手元で試すなら NOVOICE=1')
VMAP = {0: 0, 2: 1, 3: 2, 5: 3}   # 場面 → 声の行（声の無い場面は画面と曲だけ）
VD = [dur(VMAP[n]) if HASV and n in VMAP else 0 for n in range(7)]
LEAD = 0.5; TAIL = 0.5
MIN = [3.0, 4.3, 3.8, 5.2, 4.5, 3.6, 2.8]
LEN = [max(MIN[i], VD[i] + LEAD + TAIL) for i in range(7)]
LEN[6] += 0.4
ST = [sum(LEN[:i]) for i in range(7)]; TOTAL = sum(LEN)

# 日付の帯（開催日を1日ずつ）
y = int(spec['date'][:4])
def md(s):
    m, d = s.split('.'); return datetime.date(y, int(m), int(d))
d0, d1 = md(t['date'][0]), md(t['date'][2])
if d1 < d0: d1 = d1.replace(year=y + 1)
days = [(d0 + datetime.timedelta(i)) for i in range((d1 - d0).days + 1)]
cal = ''
def tcy(x):   # 縦書きの中の1〜2桁の数字を横に並べる
    return re.sub(r'(?<![\d])(\d{1,2})(?![\d])', r'<span class="tc">\1</span>', x)
def vlen(x): return len(re.sub(r'\d{1,2}', '0', x))
NOW = datetime.date.fromisoformat(spec['date'])
if len(days) > 21:
    p = max(0.0, min(1.0, (NOW - d0).days / max(1, (d1 - d0).days)))
    cal = f'<div id="span" data-p="{p:.3f}"><div id="spl"></div><div id="spf"></div><i style="left:0"></i><i style="left:100%"></i><b id="spn"><u>きょう</u></b></div>'
elif 2 <= len(days) <= 21:
    cal = ''.join(f'<div class="cd{" we" if x.weekday() >= 5 else ""}"><i></i><b>{x.day}</b><s>{"月火水木金土日"[x.weekday()]}</s></div>' for x in days)

h = open(f'{D}/template.html').read()
css = """
#cal{display:flex;justify-content:center;gap:6px;margin-top:84px}
.tc{text-combine-upright:all;-webkit-text-combine:horizontal}
#span{position:relative;width:760px;height:60px}
#spl{position:absolute;left:0;right:0;top:29px;height:1.5px;background:rgba(43,38,34,.4)}
#spf{position:absolute;left:0;top:28px;height:3px;background:#B5532F;width:0}
#span i{position:absolute;top:22px;width:16px;height:16px;margin-left:-8px;border-radius:50%;background:#FDFCFA;border:1.5px solid #2B2622}
#spn{position:absolute;top:17px;width:26px;height:26px;margin-left:-13px;border-radius:50%;background:#B5532F;border:5px solid #FDFCFA;box-shadow:0 0 0 1.5px #B5532F}
#spn u{position:absolute;left:-60px;width:146px;top:44px;text-align:center;text-decoration:none;font-family:GoM;font-weight:400;font-size:26px;color:#B5532F}
.cd{position:relative;width:46px;text-align:center}
.cd i{display:block;width:46px;height:46px;border-radius:50%;border:1.5px solid rgba(43,38,34,.4);margin:0 auto}
.cd b{position:absolute;left:0;right:0;top:10px;font-family:Jost;font-weight:400;font-size:23px;line-height:26px;color:#2B2622}
.cd s{display:block;text-decoration:none;font-size:21px;color:#8A7F76;margin-top:10px}
.cd.we s{color:#B5532F}
.leaf{position:absolute;left:0;top:0;width:60px;height:60px;z-index:2}
#vt{position:absolute;left:0;right:0;top:420px;height:700px;display:flex;flex-direction:row-reverse;justify-content:center;align-items:flex-start;gap:34px}
.vc{writing-mode:vertical-rl;overflow:hidden;height:700px;white-space:nowrap}
.vc>span{display:block}
#c1{font-family:Min;font-size:100px;letter-spacing:.1em;line-height:1.2}
.vp{font-size:42px;letter-spacing:.1em;line-height:1.5;padding-top:36px}
#vr{width:1.5px;height:560px;background:rgba(43,38,34,.4);margin:10px 14px 0;transform-origin:top}
#pg3{position:absolute;left:340px;top:1130px;width:400px;height:520px;overflow:visible}
#pg3 path,#pg3 line,#pg3 circle{fill:none;stroke-linecap:round;stroke-linejoin:round}
.pk{stroke:#2B2622;stroke-width:2}.pa{stroke:#B5532F;stroke-width:2.4}
#bar{position:absolute;left:40px;bottom:40px;height:3px;background:#B5532F;z-index:40;width:0}
#tm{font-family:Jost;font-weight:300;font-size:128px;letter-spacing:.02em;line-height:1;display:flex;justify-content:center;align-items:center;gap:36px}
#tm u{display:block;text-decoration:none;width:90px;height:2px;background:#2B2622;transform-origin:left}
#tmj{font-size:34px;color:#6E625A;margin-top:26px}
.row span em{font-style:normal;font-family:Jost;font-size:56px;letter-spacing:.02em;margin-right:6px}
#sun{position:absolute;left:340px;top:440px;width:400px;height:200px}
#s5>div:first-child{top:330px}
#s5 .h.ln{position:absolute;top:150px;height:900px;writing-mode:vertical-rl;font-size:66px!important;letter-spacing:.14em;margin:0!important;text-align:left}
#s5 .h.ln:nth-of-type(2){right:236px}#s5 .h.ln:nth-of-type(3){right:132px;padding-top:70px}
#phone{left:96px;top:540px}
#s6 #f0{margin-top:330px!important;width:120px!important}
#s6 .h.ln{writing-mode:vertical-rl;height:800px;margin:50px auto 0!important;font-size:72px!important;letter-spacing:.14em;display:block;width:100px}
#s6 #f2{margin-top:50px!important;letter-spacing:.12em}#s6 #f3{position:absolute;left:0;right:0;top:1700px;margin:0!important}
"""
h = h.replace('</style>', css + '</style>')
a = h.index('<!-- 2 date -->'); b = h.index('<!-- 5 list -->')
def tparse(v):   # 「17時半〜21時」「17:00〜20:30」「17時ごろ〜20時ごろ」→ ('17:30', '21:00')
    m = re.match(r'^(\d{1,2})(?:時(半)?|:(\d{2}))(?:ごろ)?[〜～~](\d{1,2})(?:時(半)?|:(\d{2}))(?:ごろ)?$', v)
    return (f"{m.group(1)}:{'30' if m.group(2) else m.group(3) or '00'}", f"{m.group(4)}:{'30' if m.group(5) else m.group(6) or '00'}") if m else None
ti = next((i for i, r in enumerate(t['info']) if tparse(r[1])), None)
fi = ti if ti is not None else 3
rows = [r for i, r in enumerate(t['info']) if i != fi]; feat = t['info'][fi]
tm = tparse(feat[1])
tmh = (f'<div class="ln"><span id="tm" style="display:flex"><span id="tma">{tm[0]}</span><u id="tml"></u><span id="tmb">{tm[1]}</span></span></div>'
       if tm else f'<div class="ln"><span id="tm" class="h" style="display:block;font-size:{min(84, int(760 / max(1, len(feat[1]))))}px;font-family:Min;line-height:1.5">{feat[1]}</span></div>')
def val(v):
    m = re.match(r'^([\d,]+)円$', v)
    return f'<em data-n="{m.group(1).replace(",", "")}">{m.group(1)}</em>円' if m else v
mid = f"""<!-- 2 date -->
<div class="sc" id="s2">
 <div class="k ln ctr" style="position:absolute;left:0;right:0;top:330px"><span id="b0">DATE</span></div>
 <div style="position:absolute;left:130px;top:470px">
  <div class="ln"><span class="big" id="b1" style="font-size:196px">{t['date'][0]}</span></div><div class="pl" id="b1d" style="margin-top:20px;font-size:28px">{t['date'][1]}</div>
  <div id="bl" style="width:2px;height:150px;background:#B5532F;transform-origin:top;margin:44px 0 44px 8px"></div>
  <div class="ln"><span class="big" id="b2" style="font-size:196px">{t['date'][2]}</span></div><div class="pl" id="b2d" style="margin-top:20px;font-size:28px">{t['date'][3]}</div>
 </div>
 <div style="position:absolute;right:130px;top:470px;height:760px;display:flex;flex-direction:row-reverse;gap:30px">
  <div class="vc" style="height:760px"><span id="b3" class="h" style="font-size:84px;letter-spacing:.12em;line-height:1.2">{tcy(t['date_title'])}</span></div>
  <div class="vc" style="height:760px;padding-top:40px"><span id="b4" style="font-size:36px;letter-spacing:.14em;color:#6E625A">{tcy(t['date_note'])}</span></div>
 </div>
 <div id="cal" style="position:absolute;left:0;right:0;top:1400px;margin:0">{cal}</div>
</div>
<!-- 3 point -->
<div class="sc ctr" id="s3"><div id="leaves"></div>
 <div class="k ln" style="position:absolute;left:0;right:0;top:330px"><span id="c0">{t['point_kicker']}</span></div>
 <div id="vt">
  <div class="vc"><span id="c1" style="font-size:{min(100, int(680 / (vlen(t['point_title']) * 1.1)))}px">{tcy(t['point_title'])}</span></div>
  <div id="vr"></div>
  <div class="vc vp"><span id="c2">{tcy(t['points'][0])}</span></div>
  <div class="vc vp"><span id="c3">{tcy(t['points'][1])}</span></div>
  <div class="vc vp" style="font-size:34px;color:#6E625A"><span id="c4">{tcy(t['points'][2])}</span></div>
 </div>
 <svg id="pg3" viewBox="0 0 500 650"><g id="pgd">
<circle class="pa" cx="250" cy="16" r="6" pathLength="1"/><path class="pa" pathLength="1" d="M250 22 V112"/>
<path class="pa" pathLength="1" d="M240 40 H260 M238 54 H262 M236 68 H264 M234 82 H266 M232 96 H268"/>
<path class="pk" pathLength="1" d="M250 112 Q196 142 112 152 Q104 150 96 144 Q104 160 128 166 H372 Q396 160 404 144 Q396 150 388 152 Q304 142 250 112 Z"/>
<path class="pk" pathLength="1" d="M206 166 V214 M294 166 V214 M228 166 V214 M250 166 V214 M272 166 V214 M200 214 H300"/>
<path class="pk" pathLength="1" d="M166 250 Q166 214 250 214 Q334 214 334 250"/>
<path class="pk" pathLength="1" d="M196 250 Q150 284 40 298 Q30 296 20 288 Q30 308 62 314 H438 Q470 308 480 288 Q470 296 460 298 Q350 284 304 250 Z"/>
<path class="pk" pathLength="1" d="M112 314 V424 M388 314 V424 M181 314 V424 M250 314 V424 M319 314 V424 M112 332 H388 M112 424 H388"/>
<path class="pk" pathLength="1" d="M86 424 H414 M86 424 V440 M414 424 V440 M66 440 H434"/></g>
  <line id="wt" class="pk" x1="-150" y1="452" x2="650" y2="452" pathLength="1" style="stroke:rgba(43,38,34,.55);stroke-width:1.5"/>
  <g id="pgr" transform="translate(0,904) scale(1,-1)" opacity=".34"><g id="pgd2">
<circle class="pa" cx="250" cy="16" r="6" pathLength="1"/><path class="pa" pathLength="1" d="M250 22 V112"/>
<path class="pa" pathLength="1" d="M240 40 H260 M238 54 H262 M236 68 H264 M234 82 H266 M232 96 H268"/>
<path class="pk" pathLength="1" d="M250 112 Q196 142 112 152 Q104 150 96 144 Q104 160 128 166 H372 Q396 160 404 144 Q396 150 388 152 Q304 142 250 112 Z"/>
<path class="pk" pathLength="1" d="M206 166 V214 M294 166 V214 M228 166 V214 M250 166 V214 M272 166 V214 M200 214 H300"/>
<path class="pk" pathLength="1" d="M166 250 Q166 214 250 214 Q334 214 334 250"/>
<path class="pk" pathLength="1" d="M196 250 Q150 284 40 298 Q30 296 20 288 Q30 308 62 314 H438 Q470 308 480 288 Q470 296 460 298 Q350 284 304 250 Z"/>
<path class="pk" pathLength="1" d="M112 314 V424 M388 314 V424 M181 314 V424 M250 314 V424 M319 314 V424 M112 332 H388 M112 424 H388"/>
<path class="pk" pathLength="1" d="M86 424 H414 M86 424 V440 M414 424 V440 M66 440 H434"/></g></g>
  <g id="rip"></g>
 </svg>
</div>
""" + f"""<!-- 4 info -->
<div class="sc" id="s4"><svg id="sun" viewBox="0 0 400 200"><path id="arc" d="M 20 190 A 180 180 0 0 1 380 190" fill="none" stroke="#B5532F" stroke-width="2" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/><circle id="sund" r="9" fill="#B5532F"/></svg>
 <div class="in" style="position:absolute;left:150px;right:150px;top:330px">
  <div class="k ln ctr"><span id="d0">INFORMATION</span></div>
  <div class="ctr" style="margin-top:370px">{tmh}<div id="tmj">{feat[0]}</div></div>
  <div style="margin-top:70px;border-top:1.5px solid rgba(43,38,34,.35)">
   <div class="row" id="d1"><b>{rows[0][0]}</b><span>{val(rows[0][1])}</span></div>
   <div class="row" id="d2"><b>{rows[1][0]}</b><span>{val(rows[1][1])}</span></div>
   <div class="row" id="d3"><b>{rows[2][0]}</b><span>{val(rows[2][1])}</span></div>
  </div>
  <div id="d5" style="margin-top:44px;font-size:30px;color:#8A7F76;text-align:center">{t['info_note']}</div>
 </div>
</div>

"""
h = h[:a] + mid + h[b:]
KICKER = region.KICKER
rep = dict(CORNER=t['corner'], K1=KICKER[0], K2=KICKER[1], A1=t['title'][0], A2=t['title'][1], A3=t['place'],
           MT1=t['map_tag'][0], MT2=t['map_tag'][1], MT3=t['map_tag'][2], MC1=t['map_caption'],
           E2=t['list_caption'], LISTPNG='list.png', FONTS=f'{ROOT}/tools/fonts')
for k, v in rep.items(): h = h.replace(f'__{k}__', v)

a = h.index("mk($('lamp')"); b = h.index('render(0);')
js = """
const ST=%s, LEN=%s, IDS=['s1','sm','s2','s3','s4','s5','s6'], SL=1.25;
function up(id,v){$(id).style.transform=`translateY(${(1-v)*110}%%)`;}
const LV=[[130,.0,1.0,34],[960,.3,.85,-20],[200,.55,.7,26],[890,.75,1.0,-30],[110,.9,.8,18]];
const LB=[[0,28],[58,25],[-58,25],[116,18],[-116,18]].sort((p,q)=>p[0]-q[0]);
function leafPath(){const P=(d,r)=>{const a=d*Math.PI/180;return [(Math.sin(a)*r).toFixed(1),(-Math.cos(a)*r).toFixed(1)]};let d='';
 LB.forEach(([ang,len],i)=>{const n0=P(ang-29,len*.42),c0=P(ang-13,len*.74),tp=P(ang,len),c1=P(ang+13,len*.74),n1=P(ang+29,len*.42);
  d+=(i?'L':'M')+n0+' Q'+c0+' '+tp+' Q'+c1+' '+n1+' ';});return d+'L1.2,9 L1.2,27 L-1.2,27 L-1.2,9 Z';}
LV.forEach((l,i)=>{const s=document.createElementNS(NS,'svg');s.setAttribute('class','leaf');s.setAttribute('viewBox','-30 -30 60 60');s.id='lf'+i;
 s.innerHTML=`<path d="${leafPath()}" fill="rgba(181,83,47,${i%%2?.78:.5})" stroke="none"/>`;$('leaves').appendChild(s);});
for(let i=0;i<4;i++){const e=document.createElementNS(NS,'line');e.setAttribute('class','pk');e.id='rp'+i;e.style.stroke='rgba(181,83,47,.55)';e.style.strokeWidth='1.5';$('rip').appendChild(e);}
document.querySelectorAll('#pgd [pathLength],#pgd2 [pathLength],#wt').forEach(e=>e.setAttribute('stroke-dasharray','1'));
const bar=document.createElement('div');bar.id='bar';document.body.appendChild(bar);const TOTAL=ST[6]+LEN[6];
function render(T){
 const idx=Math.max(0,ST.findIndex((s,i)=>T>=s&&T<s+LEN[i]));
 IDS.forEach((id,i)=>{const a=ST[i],b=a+LEN[i],on=T>=a&&T<b,e=$(id);e.style.visibility=on?'visible':'hidden';
  const fi=i?out((T-a)/.55):1,fo=i<6?out((b-T)/.4):1;e.style.opacity=on?Math.min(fi,fo):0;
  const dr=on&&i>=2&&i<=4?1+.022*(T-a)/LEN[i]:1;e.style.transform=`translateY(${(1-fi)*24}px) scale(${dr})`;});
 let w=$('w');w.style.display='block';w.style.height='0px';
 ST.slice(1).forEach(a=>{const p=(T-(a-.32))/.64;if(p>0&&p<1){const top=p<.5?0:(p-.5)*2*1920,hh=p<.5?ease(p*2)*1920:1920-top;w.style.top=top+'px';w.style.height=hh+'px';}});
 $('bar').style.width=(1000*cl(T/TOTAL))+'px';
 $('pg').textContent=`0${Math.min(idx,4)+1} / 05`;$('pg').style.visibility=idx<5?'visible':'hidden';
 const L=i=>(T-ST[i])/SL;   // その場面が始まってからの時間（ゆっくり）
 let t,a;
 // 表紙
 ['a0','a1','a2','a3'].forEach(i=>up(i,1));t=T/SL;
 [...$('rings').children].forEach((c,i)=>{const Lc=2*Math.PI*(330+i*70);c.setAttribute('stroke-dasharray',Lc);c.setAttribute('stroke-dashoffset',Lc*(1-seg(t,.2+i*.12,1.6+i*.12)));c.setAttribute('transform',`rotate(${-90+t*6*(i%%2?1:-1)} 540 900)`);});
 // 地図
 {const a=0,u=L(1),t=u,PX=%s,PY=%s;
  %s.forEach((k,i)=>{const e=$('m_'+k);e.style.opacity=so(t,a+.05+i*.08,a+.7+i*.08);});
  $('mb').style.clipPath=`circle(${8+70*so(t,a,a+1.1)}%% at 50%% 50%%)`;$('m_%s').style.fill=`rgba(181,83,47,${.14*seg(t,a+.8,a+1.2)})`;
  document.querySelectorAll('.mo').forEach(e=>e.style.opacity=so(t,a,a+.8));
  const z=seg(t,a+.2,a+1.2), Wv=(80-(80-42)*z)*(1-.07*cl((u-1.2)/3)), cx=225+(PX-1.5-225)*z, cy=267.6+(PY+1.2-267.6)*z;
  $('msvg').setAttribute('viewBox',[cx-Wv/2,cy-Wv/2,Wv,Wv].join(' '));
  const s=1000/Wv, px=40+(PX-(cx-Wv/2))*s, py=250+(PY-(cy-Wv/2))*s;
  const d=(u-1.05)/.45; let off; if(d<0)off=-260; else if(d<.6){const q=d/.6;off=-260*(1-q*q);} else {const q=(d-.6)/.4;off=d<1?-34*Math.sin(Math.PI*q):0;}
  const p=$('mpin'); p.style.left=px+'px'; p.style.top=py+'px'; const sq=d>.55&&d<.75?1.25:1;
  $('mdot').style.transform=`translateY(${off}px) scale(1,${1/sq})`; $('mdot').style.opacity=d>0?1:0;
  $('msh').style.opacity=d>0?.3+.7*cl(1+off/260):0; $('msh').style.transform=`scale(${.4+.6*cl(1+off/260)})`;
  [['mr1',0],['mr2',.8]].forEach(([id,o])=>{const r=((u-1.35-o)%%1.6+1.6)%%1.6/1.6;$(id).style.opacity=u>1.35+o?(1-r)*.7:0;$(id).style.transform=`scale(${1+r*3.4})`;});
  $('mlead').style.display='none';
  const Tg=$('mtag'); Tg.style.left=(px-120)+'px'; Tg.style.top=(py-330)+'px';
  up('mt1',so(t,a+1.45,a+1.95)); up('mt2',so(t,a+1.55,a+2.1)); up('mt3',so(t,a+1.7,a+2.2));
  up('mc0',so(t,a+.5,a+1.0)); up('mc1',so(t,a+.65,a+1.2));
 }
 // 日付：数字 → 開催日が1日ずつ灯る
 t=L(2); up('b0',so(t,.15,.7));up('b1',so(t,.3,.95));up('b2',so(t,.6,1.25));$('bl').style.transform=`scaleY(${seg(t,.5,1.2)})`;$('b1d').style.opacity=so(t,.6,1.1);$('b2d').style.opacity=so(t,.9,1.4);
 {const cs=[...document.querySelectorAll('.cd')],n=cs.length,span=Math.min(2.2,LEN[2]/SL-2.0);
  cs.forEach((c,i)=>{const v=so(t,1.0+span*i/n,1.0+span*i/n+.35);c.style.opacity=so(t,.7+i*.02,1.1+i*.02);
   c.children[0].style.background=`rgba(181,83,47,${v})`;c.children[0].style.borderColor=`rgba(${43+138*v},${38+45*v},${34+13*v},${.4+.6*v})`;
   c.children[0].style.transform=`scale(${1+.25*Math.sin(Math.PI*cl((t-1.0-span*i/n)/.35))})`;c.children[1].style.color=v>.5?'#FDFCFA':'#2B2622';});}
 {const vu=(id,v)=>{$(id).style.transform=`translateY(${-(1-v)*104}%%)`;};vu('b3',so(t,.5,1.4));vu('b4',so(t,.9,1.7));}
 if($('span')){const p=+$('span').dataset.p,v=seg(t,1.0,2.4);$('span').style.opacity=so(t,.7,1.2);$('spf').style.width=(p*v*100)+'%%';$('spn').style.left=(p*v*100)+'%%';$('spn').style.opacity=so(t,.9,1.3);}
 // 見どころ：縦書きの題、線で描く塔と水面
 t=L(3); up('c0',so(t,.15,.7));
 const vu=(id,v)=>{$(id).style.transform=`translateY(${-(1-v)*104}%%)`;};
 vu('c1',so(t,.3,1.2));$('vr').style.transform=`scaleY(${seg(t,.6,1.5)})`;vu('c2',so(t,1.2,2.0));vu('c3',so(t,1.5,2.3));vu('c4',so(t,1.8,2.6));
 {const ps=[...document.querySelectorAll('#pgd [pathLength]')],p2=[...document.querySelectorAll('#pgd2 [pathLength]')],n=ps.length;
  $('wt').setAttribute('stroke-dashoffset',1-seg(t,.2,1.4));
  ps.forEach((e,i)=>{const k=n-1-i,v=seg(t,.5+k*.2,1.5+k*.2);e.setAttribute('stroke-dashoffset',1-v);p2[i].setAttribute('stroke-dashoffset',1-v);});
  $('pgr').setAttribute('transform',`translate(${Math.sin(t*1.5)*3},904) scale(1,-1) skewX(${Math.sin(t*1.1)*1.6})`);$('pgr').setAttribute('opacity',.34*so(t,1.0,2.4));
  for(let i=0;i<4;i++){const q=((t*.22+i*.25)%%1),w=40+q*190,yy=480+i*46+q*10;const e=$('rp'+i);e.setAttribute('x1',250-w);e.setAttribute('x2',250+w);e.setAttribute('y1',yy);e.setAttribute('y2',yy);e.style.opacity=Math.sin(Math.PI*q)*.7*so(t,1.2,2.2);}}
 LV.forEach((l,i)=>{const e=$('lf'+i),q=(t*.085*l[2]+l[1])%%1,yy=150+q*1500,xx=l[0]+Math.sin(q*5+i)*34;
  e.style.transform=`translate(${xx}px,${yy}px) rotate(${l[3]+q*170*(i%%2?1:-1)}deg) scale(${l[2]*2.3},${l[2]*2.3*(.8+.2*Math.abs(Math.cos(q*7+i)))})`;e.style.opacity=Math.min(1,q*6,(1-q)*6)*so(t,0,.6);});
 // 料金：時間の弧 → 金額が数え上がる
 t=L(4); up('d0',so(t,.15,.7));up('tm',so(t,.3,.95));
 {const v=seg(t,.5,2.3);$('arc').setAttribute('stroke-dashoffset',1-v);const an=Math.PI*(1-v);$('sund').setAttribute('cx',200-180*Math.cos(Math.PI-an)*-1*-1);
  $('sund').setAttribute('cx',200-180*Math.cos(Math.PI*v));$('sund').setAttribute('cy',190-180*Math.sin(Math.PI*v));$('sun').style.opacity=$('tml')?so(t,.3,.8):0;
  if($('tml'))$('tml').style.transform=`scaleX(${seg(t,.6,1.3)})`;$('tmj').style.opacity=so(t,.9,1.5);}
 ['d1','d2','d3'].forEach((d,i)=>{const s0=1.9+i*.28,v=so(t,s0,s0+.6);$(d).style.opacity=v;$(d).style.transform=`translateX(${(1-v)*60}px)`;
  const em=$(d).querySelector('em');if(em){const n=+em.dataset.n,c=so(t,s0,s0+.9);em.textContent=(Math.round(n*c/10)*10).toLocaleString();}});
 $('d5').style.opacity=so(t,3.0,3.6);
 // リスト
 t=L(5); up('e0',so(t,.15,.7));up('e1',so(t,.3,.9));up('e2',so(t,.45,1.05));
 const pin=so(t,.1,1.0);$('phone').style.transform=`translateY(${(1-pin)*900}px)`;
 $('im').style.transform=`translateY(${-(260+440*seg(t,.9,LEN[5]/SL-.3))*600/390}px)`;
 // おわり
 t=L(6); $('f0').style.opacity=so(t,.2,.8);$('f0').style.transform=`translateY(${30*(1-so(t,.2,.8))}px)`;up('f1',so(t,.4,1.0));$('f2').style.opacity=so(t,.8,1.3);$('f3').style.opacity=so(t,1.1,1.6);
}
""" % (json.dumps(ST), json.dumps(LEN), f'{px:.2f}', f'{py:.2f}', json.dumps(region.PREFS), region.pref(spec))
h = h[:a] + js + h[b:]
# 絵柄：text.motif = tahoto（多宝塔）/ tou13・tou5 など（重ねた塔）/ tsuki（月。書かなければこれ）
def tou(n):
    o = '<circle class="pa" cx="250" cy="16" r="5" pathLength="1"/><path class="pa" pathLength="1" d="M250 21 V70 M242 34 H258 M240 46 H260 M238 58 H262"/>'
    th = (424 - 70) / n
    for i in range(n):          # 上から下へ
        y = 70 + th * i; w = 60 + (150 - 60) * i / max(1, n - 1); e = th * .42
        o += (f'<path class="pk" pathLength="1" d="M{250-w-14:.0f} {y+e-5:.0f} Q{250-w:.0f} {y+e+2:.0f} {250-w*.55:.0f} {y+e:.0f} L250 {y:.0f} L{250+w*.55:.0f} {y+e:.0f} Q{250+w:.0f} {y+e+2:.0f} {250+w+14:.0f} {y+e-5:.0f}'
              + (f' M{250-w*.5:.0f} {y+e:.0f} V{y+th:.0f} M{250+w*.5:.0f} {y+e:.0f} V{y+th:.0f}' if n <= 5 else f' M{250-w*.4:.0f} {y+e+4:.0f} H{250+w*.4:.0f}') + '"/>')
    return o + '<path class="pk" pathLength="1" d="M86 424 H414 M86 424 V440 M414 424 V440 M66 440 H434"/>'
mt = t.get('motif', 'tsuki')
if mt != 'tahoto':
    g = tou(int(mt[3:])) if mt.startswith('tou') else '<circle class="pa" cx="250" cy="250" r="130" pathLength="1"/><path class="pk" pathLength="1" d="M70 330 H250 M300 362 H450 M150 394 H330"/>'
    h = re.sub(r'<g id="pgd">.*?</g>', '<g id="pgd">' + g + '</g>', h, count=1, flags=re.S)
    h = re.sub(r'<g id="pgd2">.*?</g>', '<g id="pgd2">' + g + '</g>', h, count=1, flags=re.S)
fall = t.get('fall', 'leaf' if re.search('もみじ|紅葉', json.dumps(t, ensure_ascii=False)) else 'none')
if fall != 'leaf': h = h.replace('<div id="leaves">', '<div id="leaves" style="display:none">')
if region.ACC.upper() != '#B5532F':   # さし色を場所の色に
    r_, g_, b_ = (int(region.ACC[i:i + 2], 16) for i in (1, 3, 5))
    h = h.replace('rgba(${43+138*v},${38+45*v},${34+13*v}', 'rgba(${43+%d*v},${38+%d*v},${34+%d*v}' % (r_ - 43, g_ - 38, b_ - 34))
    h = h.replace('#B5532F', region.ACC).replace('181,83,47', f'{r_},{g_},{b_}')
left = re.findall(r'__[A-Z0-9]+__', h); assert not left, left
open(f'{W}/reel.html', 'w').write(h)
rec = f"""const {{chromium}}=require('playwright');const fs=require('fs');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://{W}/reel.html');await p.waitForTimeout(900);fs.mkdirSync('{W}/fr',{{recursive:true}});
const only=process.argv[2];if(only){{for(const t of only.split(',')){{await p.evaluate(t=>render(t),+t);await p.screenshot({{path:'{W}/c-'+t+'.jpg',type:'jpeg',quality:85}});}}await b.close();return;}}
for(let i=0;i<30*{TOTAL:.3f};i++){{await p.evaluate(t=>render(t),i/30);await p.screenshot({{path:'{W}/fr/'+String(i).padStart(4,'0')+'.jpg',type:'jpeg',quality:92}});}}await b.close()}})();"""
open(f'{W}/rec.js', 'w').write(rec)
print('場面', [round(x, 2) for x in ST], '全体', round(TOTAL, 1), '声', [round(x, 2) for x in VD])
if STILL:
    subprocess.run(['node', f'{W}/rec.js', STILL], check=True); print(W); sys.exit()
subprocess.run(['node', f'{W}/rec.js'], check=True)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', '0.2', '-i', f'{ROOT}/{region.BGM}', '-t', f'{TOTAL + 1:.2f}', '-af', 'loudnorm=I=-17:TP=-1.5:LRA=11', '-ar', '48000', f'{W}/bgm.wav'], check=True)
ins = []; flt = []
if not HASV:
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '30', '-i', f'{W}/fr/%04d.jpg', '-i', f'{W}/bgm.wav', '-map', '0:v', '-map', '1:a', '-af', f'afade=t=in:d=0.4,afade=t=out:st={TOTAL-2.2}:d=2.2', '-t', f'{TOTAL:.2f}',
                    '-c:v', 'libx264', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-crf', '20', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', OUT], check=True)
    print(OUT, '（声なし）'); sys.exit()
for k, (sc, n) in enumerate(VMAP.items()):
    ins += ['-i', f'{V}/{SP}-{n:02d}.wav']; flt.append(f'[{k+2}:a]aresample=48000,adelay={int((ST[sc]+LEAD)*1000)}:all=1[v{k}]')
flt.append(''.join(f'[v{n}]' for n in range(len(VMAP))) + f'amix=inputs={len(VMAP)}:normalize=0:duration=longest,volume=1.7,asplit=2[vo][sc]')
flt.append(f'[1:a]afade=t=in:d=0.4,afade=t=out:st={TOTAL-2.2}:d=2.2[bg0]')
flt.append('[bg0][sc]sidechaincompress=threshold=0.02:ratio=5:attack=40:release=600:makeup=1[bg]')
flt.append('[bg][vo]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]')
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '30', '-i', f'{W}/fr/%04d.jpg', '-i', f'{W}/bgm.wav'] + ins +
               ['-filter_complex', ';'.join(flt), '-map', '0:v', '-map', '[a]', '-t', f'{TOTAL:.2f}', '-c:v', 'libx264', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-crf', '20',
                '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', OUT], check=True)
print(OUT)
