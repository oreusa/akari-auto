/* 11/19 激変版（見本・?mihon=2 を付けた人だけ。night.js が mihon.js のあとに読む・?mihon=0 で消える）
   オーナー「HPもめちゃくちゃハイテクなUI/UXに激変」「えぐいくらいすごい出来で・どちらも（関西・関東）」。
   今の部品（ロゴ・下のバー・MENU・夜の星・カードの絵と日付の札・地図）はそのまま。上に足す物：
   ①ストーリー（インスタと同じ丸い輪→全画面で写真をめくる） ②ダイナミックアイランド（上の黒い札：いま開いてる数・押すと広がる）
   ③さがす（全画面・打つたびに出る・写真つき） ④カードを押すと下から出る板（写真・期間のバー・行きたい・送る・地図）
   ⑤今週ほかにも＝Embla（指に吸いつく・写真が奥行きで動く） ⑥写真を押すと大きく（PhotoSwipe・2本指で拡大）
   ⑦写真が出る前のぼかし色（ThumbHash） ⑧iPhone の日本語の改行（BudouX） ⑨並び替えの動き（auto-animate）
   部品は /assets/hx-lib.js（Embla・auto-animate・ThumbHash をまとめた物）・hx-bx.js（BudouX）・pswp/（PhotoSwipe）。作る元 tools/hx/。 */
(function(){
if(window.__hx)return;window.__hx=1;
var DOC=document,H=DOC.documentElement,RM=matchMedia('(prefers-reduced-motion: reduce)').matches;
var KANTO=/kanto/.test(location.hostname)||location.port==='8788';
var PC={"大阪":"#B97A62","京都":"#8A7495","兵庫":"#4F6681","奈良":"#6F8C68","滋賀":"#5F8F98","和歌山":"#C4925A","東京":"#B97A62","神奈川":"#4F6681","埼玉":"#C4925A","千葉":"#5F8F98","茨城":"#6F8C68","栃木":"#8A7495","群馬":"#9A6B5B"};
var PFO=KANTO?['東京','神奈川','埼玉','千葉','茨城','栃木','群馬']:['大阪','京都','兵庫','奈良','滋賀','和歌山'];
var D=[],ID={},PHH={},W='日月火水木金土';
/* lucide.dev のアイコン（ISC） */
var IC={search:'<path d="m21 21-4.34-4.34"/><circle cx="11" cy="11" r="8"/>',x:'<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
pin:'<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
star:'<path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"/>',
share:'<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" x2="15.42" y1="13.51" y2="17.49"/><line x1="15.41" x2="8.59" y1="6.51" y2="10.49"/>',
cal:'<path d="M16 18h6"/><path d="M16 2v3"/><path d="M19 15v6"/><path d="M21 11.5V5a2 2 0 00-2-2H5a2 2 0 00-2 2v14a2 2 0 002 2h8.3"/><path d="M3 9h18"/><path d="M8 2v3"/>',
clock:'<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',arr:'<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',up:'<path d="m5 12 7-7 7 7"/><path d="M12 19V5"/>',
spark:'<path d="M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z"/>',
hist:'<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/>'};
function ic(n,c){return '<svg class="hxi'+(c?' '+c:'')+'" viewBox="0 0 24 24" aria-hidden="true">'+IC[n]+'</svg>'}
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function jst(){return new Date(Date.now()+9*36e5)}
function ymd(d){return d.toISOString().slice(0,10)}
function md(s){return (+s.slice(5,7))+'/'+(+s.slice(8,10))}
function dd(a,b){return Math.round((Date.parse(b)-Date.parse(a))/864e5)}
function closed(o,d){var t=ymd(d),w=d.getUTCDay();if(o.cl){if(o.cl.indexOf('-'+t)>=0)return true;if(o.cl.indexOf('+'+t)>=0)return false}
  if(o.dy&&/^wd:/.test(o.dy)&&o.dy.slice(3).indexOf(String(w))<0)return true;return false}
/* いま開いてる？（mihon.js と同じ決まり） */
function now(o){if(!o||!o.h)return null;var d=jst(),t=ymd(d);if(!(o.s<=t&&o.e>=t)||closed(o,d))return null;
  var m=d.getUTCHours()*60+d.getUTCMinutes(),x=o.h.split('-').map(function(v){var a=v.split(':');return a[0]*60+ +a[1]});if(x.length<2)return null;
  var nt=x[0]>=15*60;if(m>=x[0]&&m<x[1]){var l=x[1]-m;return{on:1,t:l<=60?'あと'+l+'分で終わり':nt?'いまライトアップ中':'いま開いています'}}
  if(m<x[0]&&x[0]-m<=180)return{on:0,t:(nt?'今夜':'きょう')+o.h.split('-')[0]+'から'};return null}
function stat(o){var t=ymd(jst());if(!o.s)return'見頃';if(o.s>t)return md(o.s)+'から';if(o.e&&o.e<t)return'終わりました';var l=o.e?dd(t,o.e):99;return l===0?'きょうまで':l<=7?'あと'+l+'日':'開催中'}
function per(o){return o.s?(md(o.s)+(o.e&&o.e!==o.s?'〜'+md(o.e):'')):''}
function vib(){try{navigator.vibrate&&navigator.vibrate(6)}catch(e){}}
function ph(o,sz){return '/assets/ph/'+(sz?sz+'/':'')+o.im}
function thb(o){var h=PHH[o.im];if(!h||!window.HX)return'';try{var b=atob(h),a=new Uint8Array(b.length);for(var i=0;i<b.length;i++)a[i]=b.charCodeAt(i);return HX.th(a)}catch(e){return''}}
function go(o){vib();try{sessionStorage.setItem('tn_mph',JSON.stringify({id:o.id,im:o.im}))}catch(e){}location.href='/o/'+o.id}
function favs(){try{return JSON.parse(localStorage.getItem('tn_fav')||'[]')||[]}catch(e){return[]}}
function load(src,cb){var s=DOC.createElement('script');s.src=src;s.onload=cb||null;DOC.head.appendChild(s)}

/* ---------- 見た目 ---------- */
var SP='linear(0,0.009,0.035 2.1%,0.141 4.4%,0.723 12.9%,0.938 16.7%,1.017 19.4%,1.067,1.099 24.3%,1.108 26%,1.1,1.077 30.6%,1.017 35.6%,0.991 38.3%,0.977 40.9%,0.98 46%,0.999 55.4%,1.003 61.7%,1)';
var EO='cubic-bezier(.2,.8,.2,1)';
var css=
'.hxi{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;flex:none}'+
/* ①ストーリーの輪 */
'.hxst{display:flex;gap:14px;overflow-x:auto;scrollbar-width:none;margin:12px -16px 4px;padding:10px 16px 6px;-webkit-overflow-scrolling:touch;}.hxst::-webkit-scrollbar{display:none}'+
'.hxst button{flex:none;width:70px;border:0;background:none;padding:0;cursor:pointer;font:700 11px/1.3 "Zen Kaku Gothic New",sans-serif;color:#2B2622;text-align:center;-webkit-tap-highlight-color:transparent}'+
'.hxst .h-rg{position:relative;display:block;width:66px;height:66px;margin:0 auto 6px;border-radius:50%;padding:3px;background:conic-gradient(from 210deg,var(--pc),#E7B36A,#D9645C,var(--pc));transition:transform .5s '+SP+'}'+
'.hxst button:active .h-rg{transform:scale(.92)}'+
'.hxst .h-rg i{display:block;width:100%;height:100%;border-radius:50%;border:2.5px solid #fff;overflow:hidden;background:#eee center/cover}'+
'.hxst .h-rg i img{width:100%!important;height:100%!important;max-width:none!important;margin:0!important;border-radius:0!important;object-fit:cover;display:block}.hxst .h-rg,.hxst .h-rg i{box-sizing:border-box}'+
'.hxst .h-seen .h-rg{background:#D8D2CC}'+
'.hxst .h-rg b{position:absolute;right:-2px;bottom:-1px;min-width:22px;height:22px;padding:0 6px;border-radius:11px;background:#2B2622;color:#fff;border:2px solid #fff;font:600 11px/18px Jost,sans-serif;box-sizing:border-box}'+
'.hxst .h-rg b.h-lv{background:#1F9254}'+
'.hxst .h-rg b.h-lv::before{content:"";display:inline-block;width:5px;height:5px;border-radius:50%;background:#fff;margin:0 3px 1px 0;vertical-align:middle;animation:hxp 1.6s infinite}'+
'@keyframes hxp{50%{opacity:.25}}'+
'html.night .hxst .h-rg i{filter:invert(1) hue-rotate(180deg)}html.night .hxst .h-rg i img{filter:none!important}'+
/* ②ストーリーの全画面 */
'.hxsv{position:fixed;inset:0;z-index:2147483000;background:#000;color:#fff;touch-action:none;user-select:none;-webkit-user-select:none;opacity:0;transform:scale(.94);transition:opacity .28s,transform .45s '+SP+'}'+
'.hxsv:not(.on),.hxsr:not(.on),.hxbd:not(.on),.hxsh:not(.on){pointer-events:none}.hxsv:not(.on),.hxsr:not(.on){visibility:hidden;transition-property:opacity,transform,visibility;transition-delay:0s,0s,.32s}'+
'.hxsv.on{opacity:1;transform:none}.hxsv.out{opacity:0;transform:translateY(40px) scale(.96);transition:opacity .22s,transform .3s}'+
'html.night .hxsv{filter:invert(1) hue-rotate(180deg)}'+
'.hxsv .h-im{position:absolute;inset:0;overflow:hidden;background:#111 center/cover}'+
'.hxsv .h-im img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .35s}'+
'.hxsv .h-im img.h-in{opacity:1;animation:hxkb 7s linear forwards}@keyframes hxkb{from{transform:scale(1.04)}to{transform:scale(1.16) translate3d(-1.5%,-1%,0)}}'+
'.hxsv .h-im::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55) 0,rgba(0,0,0,0) 22%,rgba(0,0,0,0) 45%,rgba(0,0,0,.88) 100%)}'+
'.hxsv .h-bars{position:absolute;left:10px;right:10px;top:calc(10px + env(safe-area-inset-top));display:flex;gap:4px;z-index:2}'+
'.hxsv .h-bars i{flex:1;height:2.5px;border-radius:2px;background:rgba(255,255,255,.32);overflow:hidden}.hxsv .h-bars i b{display:block;height:100%;width:0;background:#fff}'+
'.hxsv .h-bars i.h-dn b{width:100%}'+
'.hxsv .h-tp{position:absolute;left:14px;right:8px;top:calc(22px + env(safe-area-inset-top));display:flex;align-items:center;gap:10px;z-index:2}'+
'.hxsv .h-tp .h-av{width:34px;height:34px;border-radius:50%;background:#333 center/cover;border:1.5px solid rgba(255,255,255,.85)}'+
'.hxsv .h-tp b{font:700 14px "Zen Kaku Gothic New",sans-serif;letter-spacing:.02em}.hxsv .h-tp small{font:500 12px Jost,sans-serif;opacity:.75;margin-left:2px}'+
'.hxsv .h-tp button{margin-left:auto;width:44px;height:44px;border:0;background:none;color:#fff;display:grid;place-items:center;cursor:pointer}.hxsv .h-tp .hxi{width:26px;height:26px}'+
'.hxsv .h-tx{position:absolute;left:20px;right:20px;bottom:calc(30px + env(safe-area-inset-bottom));z-index:2}'+
'.hxsv .h-tg{display:inline-flex;align-items:center;gap:7px;font:700 12px "Zen Kaku Gothic New",sans-serif;background:rgba(255,255,255,.95);color:#2B2622;border-radius:999px;padding:6px 12px;margin-bottom:14px}.hxsv .h-tg i{font-style:normal;color:var(--pc)}'+
'.hxsv .h-tg.h-lv::before{content:"";width:7px;height:7px;border-radius:50%;background:#1F9254;animation:hxp 1.6s infinite}'+
'.hxsv h2{font:700 clamp(25px,7.2vw,32px)/1.4 "Shippori Mincho","Noto Serif JP",serif;letter-spacing:.03em;margin:0;text-shadow:0 2px 18px rgba(0,0,0,.4);word-break:auto-phrase;text-wrap:balance}'+
'.hxsv .h-nm{font-size:13.5px;opacity:.9;margin-top:10px;line-height:1.6}'+
'.hxsv .h-nm span{display:inline-flex;align-items:center;gap:4px;opacity:.85}.hxsv .h-nm .hxi{width:14px;height:14px}'+
'.hxsv .h-go{display:flex;align-items:center;justify-content:center;gap:8px;margin-top:20px;height:52px;border-radius:999px;background:#fff;color:#2B2622;font:700 15px "Zen Kaku Gothic New",sans-serif;letter-spacing:.06em;border:0;width:100%;cursor:pointer;animation:hxup 2.4s ease-in-out infinite}'+
'.hxsv .h-go .hxi{width:18px;height:18px}@keyframes hxup{0%,100%{transform:none}50%{transform:translateY(-3px)}}'+
'.hxsv .h-cr{position:absolute;right:12px;top:calc(64px + env(safe-area-inset-top));z-index:2;font-size:9.5px;opacity:.7;max-width:55%;text-align:right}'+
'.hxsv.h-pz .h-bars i.h-cu b{animation-play-state:paused!important}'+
/* ③ダイナミックアイランド */
'.hxis{position:fixed;left:50%;bottom:calc(96px + env(safe-area-inset-bottom));z-index:2147482000;transform:translate(-50%,160px);background:#0E0C0B;color:#fff;border-radius:22px;box-shadow:0 12px 34px -12px rgba(0,0,0,.55);transition:transform .6s '+SP+',width .55s '+SP+',height .55s '+SP+',border-radius .5s '+SP+';width:206px;height:40px;overflow:hidden;cursor:pointer;-webkit-tap-highlight-color:transparent}'+
'.hxis.h-sh{transform:translate(-50%,0)}'+
'.hxis .h-c{display:flex;align-items:center;gap:8px;height:40px;padding:0 14px;font:700 12.5px "Zen Kaku Gothic New",sans-serif;white-space:nowrap}'+
'.hxis .h-c i{width:8px;height:8px;border-radius:50%;background:#34C76F;box-shadow:0 0 0 0 rgba(52,199,111,.6);animation:hxpl 1.8s infinite}.hxis .h-c i.h-s{background:#F0A23B;animation:none}'+
'@keyframes hxpl{0%{box-shadow:0 0 0 0 rgba(52,199,111,.6)}80%,100%{box-shadow:0 0 0 8px rgba(52,199,111,0)}}'+
'.hxis .h-c b{font:600 15px Jost,sans-serif;margin-left:-2px}.hxis .h-c time{margin-left:auto;font:500 12.5px Jost,sans-serif;opacity:.7;letter-spacing:.04em}'+
'.hxis .h-x{opacity:0;transition:opacity .25s;padding:2px 12px 12px}.hxis.h-op{width:min(360px,calc(100vw - 24px));height:var(--h,260px);border-radius:30px}.hxis.h-op .h-x{opacity:1;transition-delay:.15s}'+
'.hxis .h-x a{display:flex;align-items:center;gap:12px;padding:8px 4px;color:#fff;text-decoration:none;border-top:1px solid rgba(255,255,255,.08)}'+
'.hxis .h-x a img{width:44px;height:44px;border-radius:12px;object-fit:cover;flex:none;background:#222}.hxis .h-x a span{min-width:0}'+
'.hxis .h-x a b{display:block;font:700 13.5px/1.4 "Zen Kaku Gothic New",sans-serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.hxis .h-x a small{display:block;font-size:11.5px;color:#7FE0A6;margin-top:2px}'+
'.hxis .h-x button{display:block;width:100%;margin-top:8px;height:42px;border-radius:999px;border:0;background:#fff;color:#0E0C0B;font:700 13px "Zen Kaku Gothic New",sans-serif;cursor:pointer}'+
'html.night .hxis{filter:invert(1) hue-rotate(180deg)}html.night .hxis img{filter:none!important}'+
/* ④さがす（全画面） */
'.hxsr{position:fixed;inset:0;z-index:2147482500;background:rgba(250,248,245,.86);-webkit-backdrop-filter:blur(22px) saturate(1.6);backdrop-filter:blur(22px) saturate(1.6);display:flex;flex-direction:column;opacity:0;transition:opacity .22s}'+
'.hxsr.on{opacity:1}.hxsr .h-bx{display:flex;align-items:center;gap:10px;padding:calc(12px + env(safe-area-inset-top)) 16px 10px}'+
'.hxsr label{flex:1;display:flex;align-items:center;gap:10px;height:48px;padding:0 14px;border-radius:16px;background:#fff;box-shadow:0 1px 0 rgba(0,0,0,.04),0 10px 30px -18px rgba(40,30,20,.5);transform:translateY(-8px);transition:transform .5s '+SP+'}.hxsr.on label{transform:none}'+
'.hxsr label .hxi{color:#8C7B6E}.hxsr input{flex:1;min-width:0;border:0;background:none;outline:none;font:500 16px "Zen Kaku Gothic New",sans-serif;color:#2B2622}.hxsr input::placeholder{color:#9A8F86}'+
'.hxsr .h-cn{border:0;background:none;font:700 14px "Zen Kaku Gothic New",sans-serif;color:#2B2622;padding:10px 2px;cursor:pointer}'+
'.hxsr .h-ch{display:flex;gap:7px;overflow-x:auto;scrollbar-width:none;padding:2px 16px 10px}.hxsr .h-ch::-webkit-scrollbar{display:none}'+
'.hxsr .h-ch button{flex:none;border:1px solid #E3DBD2;background:#fff;color:#4A403A;border-radius:999px;padding:8px 13px;font:700 12.5px "Zen Kaku Gothic New",sans-serif;cursor:pointer;transition:background .2s,color .2s}'+
'.hxsr .h-ch button[aria-pressed=true]{background:#2B2622;border-color:#2B2622;color:#fff}'+
'.hxsr .h-rs{flex:1;overflow-y:auto;-webkit-overflow-scrolling:touch;padding:0 16px calc(30px + env(safe-area-inset-bottom));overscroll-behavior:contain}'+
'.hxsr h3{font:600 11px Jost,"Zen Kaku Gothic New",sans-serif;letter-spacing:.2em;color:#8C7B6E;margin:14px 2px 6px}'+
'.hxsr .h-it{display:flex;align-items:center;gap:12px;padding:9px 4px;border-radius:14px;text-decoration:none;color:#2B2622;opacity:0;transform:translateY(8px);animation:hxin .45s '+EO+' forwards}'+
'.hxsr .h-it:active{background:rgba(0,0,0,.05)}@keyframes hxin{to{opacity:1;transform:none}}'+
'.hxsr .h-it .h-th{width:56px;height:56px;border-radius:14px;flex:none;background:#E9E4DE center/cover;overflow:hidden}.hxsr .h-it .h-th img{width:100%;height:100%;object-fit:cover;display:block}'+
'.hxsr .h-it span{min-width:0;flex:1}.hxsr .h-it b{display:block;font:700 14.5px/1.45 "Zen Kaku Gothic New",sans-serif;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}'+
'.hxsr .h-it small{display:flex;gap:6px;align-items:center;font-size:11.5px;color:#76685D;margin-top:3px}.hxsr .h-it small i{font-style:normal;font-weight:700;color:var(--pc)}.hxsr .h-it small em{font-style:normal;color:#1F7A47;font-weight:700}'+
'.hxsr mark{background:linear-gradient(transparent 55%,#FFE2A8 55%);color:inherit}'+
'.hxsr .h-no{text-align:center;color:#76685D;font-size:13.5px;padding:40px 0;line-height:2}'+
'.hxsr .h-rc{display:flex;flex-wrap:wrap;gap:6px}.hxsr .h-rc button{display:inline-flex;align-items:center;gap:5px;border:0;background:rgba(0,0,0,.05);border-radius:999px;padding:7px 12px;font:500 12.5px "Zen Kaku Gothic New",sans-serif;color:#4A403A;cursor:pointer}.hxsr .h-rc .hxi{width:14px;height:14px}'+
'html.night .hxsr{background:rgba(250,248,245,.92)}html.night .hxsr .h-th{filter:invert(1) hue-rotate(180deg)}html.night .hxsr .h-th img{filter:none!important}'+
/* 入口の「さがす」 */
'.hxq{display:flex;align-items:center;gap:10px;width:100%;max-width:none;box-sizing:border-box;height:50px;margin:14px 0 2px;padding:0 16px;border:1px solid #E6DED6;border-radius:16px;background:rgba(255,255,255,.8);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);font:500 14.5px "Zen Kaku Gothic New",sans-serif;color:#8C7B6E;cursor:pointer;text-align:left;box-shadow:0 10px 26px -20px rgba(40,30,20,.6)}'+
'.hxq .hxi{color:#2B2622}.hxq span{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.hxq kbd{white-space:nowrap;margin-left:auto;font:600 11px Jost,sans-serif;color:#9A8F86;border:1px solid #E6DED6;border-radius:6px;padding:2px 6px}'+
/* ⑤下から出る板 */
'.hxbd{position:fixed;inset:0;z-index:2147482400;background:rgba(20,15,12,.38);-webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px);opacity:0;transition:opacity .3s}.hxbd.on{opacity:1}'+
'.hxsh{position:fixed;left:0;right:0;bottom:0;z-index:2147482401;max-width:560px;margin:0 auto;max-height:92svh;background:#fff;border-radius:26px 26px 0 0;box-shadow:0 -20px 50px -20px rgba(0,0,0,.35);transform:translateY(105%);transition:transform .55s '+SP+';display:flex;flex-direction:column;overflow:hidden}'+
'.hxsh.on{transform:translateY(0)}.hxsh.h-drag{transition:none}'+
'.hxsh .h-hd{position:absolute;left:50%;top:8px;width:40px;height:5px;margin-left:-20px;border-radius:3px;background:rgba(255,255,255,.85);z-index:3;box-shadow:0 1px 4px rgba(0,0,0,.25)}'+
'.hxsh .h-sc{overflow-y:auto;-webkit-overflow-scrolling:touch;overscroll-behavior:contain;padding-bottom:calc(16px + env(safe-area-inset-bottom))}'+
'.hxsh .h-pv{position:relative;aspect-ratio:16/10;background:#E9E4DE center/cover;overflow:hidden}.hxsh .h-pv img{width:100%;height:100%;object-fit:cover;display:block;cursor:zoom-in;opacity:0;transition:opacity .4s}.hxsh .h-pv img.h-in{opacity:1}'+
'.hxsh .h-pv::after{content:"";position:absolute;inset:auto 0 0;height:40%;background:linear-gradient(transparent,rgba(0,0,0,.35));pointer-events:none}'+
'.hxsh .h-pv small{position:absolute;right:10px;bottom:8px;z-index:1;color:#fff;font-size:9.5px;opacity:.85}'+
'.hxsh .h-pv .h-cl{position:absolute;right:12px;top:12px;z-index:2;width:36px;height:36px;border-radius:50%;border:0;background:rgba(20,16,12,.5);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);color:#fff;display:grid;place-items:center;cursor:pointer}.hxsh .h-pv .h-cl .hxi{width:18px;height:18px}'+
'.hxsh .h-bd{padding:16px 20px 4px}'+
'.hxsh .h-tg{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px}.hxsh .h-tg span{font:700 11.5px "Zen Kaku Gothic New",sans-serif;border-radius:999px;padding:5px 10px;background:#F4F1ED;color:#4A403A}'+
'.hxsh .h-tg .h-pf{background:var(--pc);color:#fff}.hxsh .h-tg .h-lv{background:#E4F4EA;color:#17683D}.hxsh .h-tg .h-lv::before{content:"● ";color:#22A35A}'+
'.hxsh .h-hk{font:700 13px "Zen Kaku Gothic New",sans-serif;color:var(--pc);margin:0 0 4px}'+
'.hxsh h2{font:700 22px/1.45 "Shippori Mincho","Noto Serif JP",serif;letter-spacing:.02em;margin:0;color:#231E1B;word-break:auto-phrase;text-wrap:balance}'+
'.hxsh .h-vn{display:flex;align-items:center;gap:5px;font-size:13px;color:#6B6058;margin-top:8px}.hxsh .h-vn .hxi{width:15px;height:15px}'+
'.hxsh .h-pr{margin:16px 0 4px}.hxsh .h-pr .h-l{display:flex;justify-content:space-between;font:500 12px Jost,"Zen Kaku Gothic New",sans-serif;color:#6B6058;margin-bottom:6px}.hxsh .h-pr .h-l b{color:#231E1B;font-weight:700}'+
'.hxsh .h-pr .h-t{position:relative;height:6px;border-radius:3px;background:#EFEAE4;overflow:hidden}.hxsh .h-pr .h-t i{position:absolute;inset:0 auto 0 0;width:0;border-radius:3px;background:linear-gradient(90deg,var(--pc),#E7B36A);transition:width 1.1s '+EO+' .25s}'+
'.hxsh .h-pr .h-t u{position:absolute;top:-3px;width:2px;height:12px;background:#231E1B;border-radius:1px;transition:left 1.1s '+EO+' .25s;left:0}'+
'.hxsh .h-ds{font-size:14.5px;line-height:1.95;color:#3A322D;margin:14px 0 0}'+
'.hxsh .h-ac{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:18px 0 0}'+
'.hxsh .h-ac button,.hxsh .h-ac a{display:flex;flex-direction:column;align-items:center;gap:5px;padding:12px 0 10px;border-radius:16px;border:1px solid #EAE3DC;background:#fff;color:#2B2622;text-decoration:none;font:700 11.5px "Zen Kaku Gothic New",sans-serif;cursor:pointer;transition:transform .35s '+SP+'}'+
'.hxsh .h-ac :active{transform:scale(.94)}.hxsh .h-ac [aria-pressed=true]{background:#FFF6DD;border-color:#E9C25B;color:#7A5A00}.hxsh .h-ac [aria-pressed=true] .hxi{fill:#E2B53B;stroke:#C99A1E}'+
'.hxsh .h-mo{display:flex;align-items:center;justify-content:center;gap:8px;margin:12px 0 0;height:54px;border-radius:16px;background:#2B2622;color:#fff;font:700 15px "Zen Kaku Gothic New",sans-serif;letter-spacing:.06em;text-decoration:none}.hxsh .h-mo .hxi{width:18px;height:18px;transition:transform .3s}.hxsh .h-mo:active .hxi{transform:translateX(4px)}'+
'html.night .hxsh .h-pv,html.night .hxsh .h-tg .h-pf{filter:invert(1) hue-rotate(180deg)}html.night .hxsh .h-pv img{filter:none!important}'+
/* ⑥今週ほかにも＝Embla */
'.mnews .mntr.hxem{display:block!important;padding:0!important;overflow:hidden!important;scroll-snap-type:none!important;touch-action:pan-y pinch-zoom}.mnews .hxemc{display:flex;gap:10px;width:100%;backface-visibility:hidden}.mnews .hxemc>.mnsl{flex:0 0 100%;min-width:0}'+
'.mnews .hxemc>.mnsl img{inset:0 -12%!important;width:124%!important;will-change:transform}'+
'.mnews .hxpg{display:flex;gap:4px;margin:10px 2px 0}.mnews .hxpg i{flex:1;height:3px;border-radius:2px;background:#E2DCD6;overflow:hidden}.mnews .hxpg i b{display:block;height:100%;width:0;background:#2B2622}.mnews .hxpg i.h-dn b{width:100%}'+
'.mnews.hxe .mndt{display:none!important}'+
/* ⑦写真の前のぼかし色・⑨BudouX */
'.hxth{background-size:cover!important;background-position:center!important;animation:none!important}'+
'budoux-ja,.hxbx{word-break:keep-all;overflow-wrap:anywhere}'+
/* 1件ページ：写真を押すと大きく */
'.mph-o img,.sp-ph img{cursor:zoom-in}'+
'.pswp{--pswp-bg:#0b0a09}html.night .pswp{filter:invert(1) hue-rotate(180deg)}'+
'@media (prefers-reduced-motion:reduce){.hxsv,.hxsh,.hxis{transition:none!important}.hxsv .h-im img.h-in,.hxsv .h-go,.hxsr .h-it{animation:none!important;opacity:1!important;transform:none!important}}';
var stl=DOC.createElement('style');stl.textContent=css;DOC.head.appendChild(stl);
var pl=DOC.createElement('link');pl.rel='stylesheet';pl.href='/assets/pswp/photoswipe.css';DOC.head.appendChild(pl);

/* ---------- まとめ（ストーリーの組） ---------- */
function live(){var t=ymd(jst());return D.filter(function(o){return o.im&&o.id&&o.s&&o.s<=t&&(!o.e||o.e>=t)})}
function sets(){var t=ymd(jst()),t3=ymd(new Date(jst().getTime()+3*864e5)),t7=ymd(new Date(jst().getTime()+7*864e5));
  var ok=D.filter(function(o){return o.im&&o.id&&(!o.e||o.e>=t)&&(!o.vn||o.n.indexOf(o.vn)>=0||1)});
  var vp=function(o){return o.vn&&o.n.indexOf(o.vn)<0?1:0},by=function(a,b){return vp(a)-vp(b)||((a.e||'9')<(b.e||'9')?-1:1)};
  var L=[],on=ok.filter(function(o){var n=now(o);return n&&n.on});
  if(on.length>=2)L.push({k:'on',t:'いま開いてる',a:on.sort(by),lv:1});
  var nt=ok.filter(function(o){return /イルミ|ライト|灯|光|ルミナ|クリスマス|ツリー|夜/.test(o.n+(o.hk||''))&&o.s<=t7}).sort(by);if(nt.length>=2)L.push({k:'il',t:'夜の光',a:nt});
  var ky=ok.filter(function(o){return /紅葉|もみじ|楓|錦秋/.test(o.n+(o.hk||''))&&(!o.s||o.s<=t7)}).sort(by);if(ky.length>=2)L.push({k:'ky',t:'紅葉',a:ky});
  var en=ok.filter(function(o){return o.s&&o.s<=t&&o.e&&o.e<=t3}).sort(by);if(en.length>=2)L.push({k:'en',t:'終わる間近',a:en});
  var nw=ok.filter(function(o){return o.s&&o.s>t&&o.s<=t7}).sort(function(a,b){return a.s<b.s?-1:1});if(nw.length>=2)L.push({k:'nw',t:'これから',a:nw});
  PFO.forEach(function(p){var a=ok.filter(function(o){return o.p===p&&(!o.s||o.s<=t7)}).sort(by);if(a.length>=2)L.push({k:'p'+p,t:p,a:a,pc:PC[p]})});
  L.forEach(function(s){s.a=s.a.slice(0,10)});return L}
function seen(){try{return JSON.parse(localStorage.getItem('hx_seen')||'{}')}catch(e){return{}}}
function rail(){var hostQ=DOC.querySelector('.wrap>.qk'),cover=/^\/(town-notes(\.html)?)?$/.test(location.pathname),ms=cover&&DOC.querySelector('section.mapsec');
  if(DOC.querySelector('.hxst'))return;var hd=!hostQ&&!ms&&/^\/(odekake|illumination|koyo|ima)/.test(location.pathname)&&DOC.querySelector('.wrap>header.head,.wrap>.head'),at=hostQ||ms||(hd&&hd.nextElementSibling);if(!at)return;
  var S=sets();if(!S.length)return;window.__hxS=S;var sn=seen(),t=ymd(jst());
  var h='';S.forEach(function(s,i){var o=s.a[0],nOn=s.lv?s.a.length:0;h+='<button type="button" data-i="'+i+'" class="'+(sn[s.k]===t?'h-seen':'')+'" style="--pc:'+(s.pc||(PC[o.p]||'#B97A62'))+'" aria-label="'+esc(s.t)+'のストーリー（'+s.a.length+'件）"><span class="h-rg"><i><img src="'+ph(o,'t')+'" alt="" decoding="async"'+(i>5?' loading="lazy"':'')+'></i>'+(s.lv?'<b class="h-lv">'+nOn+'</b>':'')+'</span>'+esc(s.t)+'</button>'});
  var w=DOC.createElement('div');w.className='hxst';w.setAttribute('role','list');w.innerHTML=h;
  at.parentNode.insertBefore(w,at);
  w.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;story(+b.dataset.i,0)});
  if(!DOC.querySelector('.hxq')&&(cover||!DOC.querySelector('#v2bar [data-a=find]'))){var q=DOC.createElement('button');q.type='button';q.className='hxq';q.innerHTML=ic('search')+'<span>行きたい所・駅で探す</span><kbd>'+D.length+'件</kbd>';w.parentNode.insertBefore(q,w.nextSibling);q.onclick=function(){search('')};
    /* 入口の頭は左右の余白が広いので、輪は画面いっぱい・さがすは地図と同じ幅に合わせる */
    if(!cover){q.style.margin='4px 0 6px';return}var fit=function(){w.style.margin='12px 0 4px';q.style.margin='12px 0 2px';q.style.width='';var r=w.getBoundingClientRect(),m=ms.getBoundingClientRect(),r2=q.getBoundingClientRect();w.style.marginLeft=(-r.left)+'px';w.style.marginRight=(r.right-DOC.documentElement.clientWidth)+'px';var pd=Math.max(16,m.left)+'px';w.style.setProperty('padding',('10px '+pd+' 6px'),'important');q.style.marginLeft=(m.left-r2.left)+'px';q.style.width=m.width+'px'};fit();addEventListener('resize',fit)}}

/* ---------- ストーリーの全画面 ---------- */
var SV=null;
function story(si,ii){var S=window.__hxS;if(!S||!S[si])return;vib();
  if(!SV){SV=DOC.createElement('div');SV.className='hxsv';SV.setAttribute('role','dialog');SV.setAttribute('aria-modal','true');DOC.body.appendChild(SV);bindSV()}
  SV.dataset.si=si;SV.dataset.ii=ii;paint();DOC.body.style.overflow='hidden';
  requestAnimationFrame(function(){SV.classList.remove('out');SV.classList.add('on')});
  try{history.pushState({hxs:1},'')}catch(e){}}
var TM=null,T0=0,LEFT=0,PAUSE=0,DUR=5600;
function paint(){var S=window.__hxS,si=+SV.dataset.si,ii=+SV.dataset.ii,s=S[si],o=s.a[ii],t=ymd(jst()),n=now(o),pc=PC[o.p]||'#B97A62';
  var sn=seen();if(ii===s.a.length-1){sn[s.k]=t;try{localStorage.setItem('hx_seen',JSON.stringify(sn))}catch(e){}var rb=DOC.querySelector('.hxst [data-i="'+si+'"]');if(rb)rb.classList.add('h-seen')}
  var tb=thb(o);
  SV.style.setProperty('--pc',pc);
  SV.innerHTML='<div class="h-im" style="'+(tb?'background-image:url('+tb+')':'')+'"><img src="'+ph(o)+'" alt="'+esc(o.n)+'" decoding="async"></div>'+
    '<div class="h-bars">'+s.a.map(function(x,k){return '<i class="'+(k<ii?'h-dn':k===ii?'h-cu':'')+'"><b></b></i>'}).join('')+'</div>'+
    '<div class="h-tp"><span class="h-av" style="background-image:url('+ph(s.a[0],'t')+')"></span><b>'+esc(s.t)+'</b><small>'+(ii+1)+'/'+s.a.length+'</small><button type="button" class="xx" aria-label="閉じる">'+ic('x')+'</button></div>'+
    (o.cr?'<small class="h-cr">写真：'+esc(o.cr.replace(/（.*$/,''))+'</small>':'')+
    '<div class="h-tx"><span class="h-tg'+(n&&n.on?' h-lv':'')+'"><i>'+esc(o.p)+'</i>'+esc(n?n.t:stat(o))+(o.e&&!n?'・'+md(o.e)+'まで':'')+'</span>'+
    '<h2>'+esc(o.hk||o.n)+'</h2><div class="h-nm">'+(o.hk?esc(o.n)+'<br>':'')+(o.vn?'<span>'+ic('pin')+esc(o.vn)+'</span>':'')+'</div>'+
    '<button type="button" class="h-go">'+ic('up')+'くわしく見る</button></div>';
  var im=SV.querySelector('.h-im img');var fin=function(){im.classList.add('h-in')};if(im.complete&&im.naturalWidth)fin();else{im.onload=fin;im.onerror=fin}
  var nx=s.a[ii+1]||(S[si+1]&&S[si+1].a[0]);if(nx){var p=new Image();p.src=ph(nx)}
  start(DUR)}
function start(ms){clearTimeout(TM);LEFT=ms;T0=Date.now();var b=SV.querySelector('.h-bars .h-cu b');
  if(b){b.style.transition='none';b.style.width=(100*(1-ms/DUR))+'%';b.offsetWidth;b.style.transition='width '+ms+'ms linear';b.style.width='100%'}
  TM=setTimeout(next,ms)}
function pause(){if(PAUSE)return;PAUSE=1;clearTimeout(TM);LEFT=Math.max(300,LEFT-(Date.now()-T0));var b=SV.querySelector('.h-bars .h-cu b');if(b){var w=getComputedStyle(b).width;b.style.transition='none';b.style.width=w}}
function resume(){if(!PAUSE)return;PAUSE=0;start(LEFT)}
function next(){var S=window.__hxS,si=+SV.dataset.si,ii=+SV.dataset.ii;if(ii<S[si].a.length-1){SV.dataset.ii=ii+1;paint()}else if(si<S.length-1){SV.dataset.si=si+1;SV.dataset.ii=0;paint()}else close1()}
function prev(){var S=window.__hxS,si=+SV.dataset.si,ii=+SV.dataset.ii;if(ii>0){SV.dataset.ii=ii-1;paint()}else if(si>0){SV.dataset.si=si-1;SV.dataset.ii=S[si-1].a.length-1;paint()}else start(DUR)}
function close1(fromPop){if(!SV||!SV.classList.contains('on'))return;clearTimeout(TM);SV.classList.remove('on');SV.classList.add('out');DOC.body.style.overflow='';
  setTimeout(function(){if(SV&&!SV.classList.contains('on'))SV.innerHTML=''},320);if(!fromPop)try{history.back()}catch(e){}}
function cur(){var S=window.__hxS;return S[+SV.dataset.si].a[+SV.dataset.ii]}
function bindSV(){var x0=0,y0=0,t0=0,lp=null,moved=0;
  SV.addEventListener('pointerdown',function(e){if(e.target.closest('button'))return;x0=e.clientX;y0=e.clientY;t0=Date.now();moved=0;lp=setTimeout(function(){pause();SV.classList.add('h-pz')},180)});
  SV.addEventListener('pointermove',function(e){if(!t0)return;var dy=e.clientY-y0;if(Math.abs(dy)>8||Math.abs(e.clientX-x0)>8){moved=1;clearTimeout(lp)}if(dy>0){SV.style.transition='none';SV.style.transform='translateY('+dy*.6+'px) scale('+(1-Math.min(dy,300)/3000)+')'}});
  SV.addEventListener('pointerup',function(e){if(!t0)return;clearTimeout(lp);var dx=e.clientX-x0,dy=e.clientY-y0,dt=Date.now()-t0;t0=0;SV.style.transition='';SV.style.transform='';SV.classList.remove('h-pz');
    if(dy>110||(dy>40&&dy/dt>.5)){close1();return}if(dy<-70){go(cur());return}
    if(Math.abs(dx)>60){dx<0?next():prev();return}
    if(PAUSE&&dt>180){resume();return}if(moved)return;resume();if(e.clientX<innerWidth*.3)prev();else next()});
  SV.addEventListener('pointercancel',function(){t0=0;clearTimeout(lp);SV.style.transform='';resume()});
  SV.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;e.stopPropagation();if(b.classList.contains('xx'))close1();else if(b.classList.contains('h-go'))go(cur())});
  addEventListener('keydown',function(e){if(!SV.classList.contains('on'))return;if(e.key==='Escape')close1();else if(e.key==='ArrowRight')next();else if(e.key==='ArrowLeft')prev()});
  DOC.addEventListener('visibilitychange',function(){if(!SV.classList.contains('on'))return;DOC.hidden?pause():resume()})}
addEventListener('popstate',function(){if(SV&&SV.classList.contains('on'))close1(1);if(SR&&SR.classList.contains('on'))closeSR(1);if(SH&&SH.classList.contains('on'))closeSH(1)});

/* ---------- ダイナミックアイランド ---------- */
var IS=null;
function island(){if(IS||!D.length)return;IS=DOC.createElement('div');IS.className='hxis';IS.setAttribute('role','button');IS.setAttribute('aria-label','いま開いているおでかけ');DOC.body.appendChild(IS);
  function fill(){var d=jst(),on=[],so=[];D.forEach(function(o){var n=now(o);if(n&&o.id&&o.im)(n.on?on:so).push(o)});var L=on.length?on:so;
    var tm=('0'+d.getUTCHours()).slice(-2)+':'+('0'+d.getUTCMinutes()).slice(-2);
    var lab=on.length?'いま開いてる <b>'+on.length+'</b>':so.length?'まもなく <b>'+so.length+'</b>':'きょう開催 <b>'+live().length+'</b>';
    var top=(L.length?L:live()).slice(0,3);
    IS.innerHTML='<div class="h-c"><i'+(on.length?'':' class="h-s"')+'></i>'+lab+'<time>'+tm+'</time></div><div class="h-x">'+top.map(function(o){var n=now(o);return '<a href="/o/'+o.id+'" data-hx="'+o.id+'"><img src="'+ph(o,'t')+'" alt=""><span><b>'+esc(o.n)+'</b><small>'+esc(n?n.t:stat(o))+'</small></span></a>'}).join('')+'<button type="button">ストーリーで全部見る</button></div>';
    IS.style.setProperty('--h',(52+top.length*61+56)+'px')}
  fill();setInterval(fill,30000);
  var shown=0;function chk(){var y=scrollY>(innerHeight*.55);if(y!==!!shown){shown=y;IS.classList.toggle('h-sh',y);if(!y)IS.classList.remove('h-op')}}
  addEventListener('scroll',chk,{passive:true});chk();
  IS.addEventListener('click',function(e){var a=e.target.closest('a[data-hx]');if(a){e.preventDefault();go(ID[a.dataset.hx]);return}
    if(e.target.closest('button')){IS.classList.remove('h-op');var S=window.__hxS||(window.__hxS=sets());story(0,0);return}vib();IS.classList.toggle('h-op')});
  DOC.addEventListener('click',function(e){if(IS.classList.contains('h-op')&&!IS.contains(e.target))IS.classList.remove('h-op')},true)}

/* ---------- さがす ---------- */
var SR=null,FL='';
function fold(s){return String(s||'').normalize('NFKC').toLowerCase().replace(/[ァ-ヶ]/g,function(c){return String.fromCharCode(c.charCodeAt(0)-96)}).replace(/\s+/g,'')}
function hi(s,q){if(!q)return esc(s);var f=fold(s),i=f.indexOf(q);if(i<0||f.length!==String(s).replace(/\s+/g,'').length||/\s/.test(s))return esc(s);return esc(s.slice(0,i))+'<mark>'+esc(s.slice(i,i+q.length))+'</mark>'+esc(s.slice(i+q.length))}
function row(o,q,k){var n=now(o),pc=PC[o.p]||'#B97A62',tb=thb(o);return '<a class="h-it" href="/o/'+o.id+'" data-hx="'+o.id+'" style="--pc:'+pc+';animation-delay:'+Math.min(k*28,300)+'ms"><span class="h-th" style="'+(tb?'background-image:url('+tb+')':'')+'"><img src="'+ph(o,'t')+'" alt="" loading="lazy" decoding="async"></span><span><b>'+hi(o.n,q)+'</b><small><i>'+esc(o.p)+'</i>'+(n&&n.on?'<em>● '+esc(n.t)+'</em>':esc(stat(o)))+(o.vn?'・'+esc(o.vn):'')+'</small></span></a>'}
function search(q0){if(!D.length)return;vib();
  if(!SR){SR=DOC.createElement('div');SR.className='hxsr';SR.setAttribute('role','dialog');SR.setAttribute('aria-modal','true');SR.setAttribute('aria-label','さがす');
    var ch=['いま開いてる','今週末','もうすぐ終わる','これから'].concat(PFO.filter(function(p){return D.some(function(o){return o.p===p})}));
    SR.innerHTML='<div class="h-bx"><label>'+ic('search')+'<input type="search" enterkeyhint="search" placeholder="行きたい所・駅・したいこと" aria-label="さがす言葉"></label><button type="button" class="h-cn">閉じる</button></div>'+
      '<div class="h-ch">'+ch.map(function(c){return '<button type="button" aria-pressed="false">'+c+'</button>'}).join('')+'</div><div class="h-rs" aria-live="polite"></div>';
    DOC.body.appendChild(SR);var inp=SR.querySelector('input'),tq=null;
    inp.addEventListener('input',function(){clearTimeout(tq);tq=setTimeout(function(){res(inp.value)},60)});
    inp.addEventListener('keydown',function(e){if(e.key==='Enter'){var a=SR.querySelector('.h-rs a.h-it');if(a){rec(inp.value);go(ID[a.dataset.hx])}}else if(e.key==='Escape')closeSR()});
    SR.querySelector('.h-cn').onclick=function(){closeSR()};
    SR.querySelector('.h-ch').addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;var on=b.getAttribute('aria-pressed')!=='true';SR.querySelectorAll('.h-ch button').forEach(function(x){x.setAttribute('aria-pressed','false')});b.setAttribute('aria-pressed',String(on));FL=on?b.textContent:'';vib();res(inp.value)});
    SR.querySelector('.h-rs').addEventListener('click',function(e){var a=e.target.closest('a[data-hx]');if(a){e.preventDefault();rec(inp.value);go(ID[a.dataset.hx]);return}var r=e.target.closest('[data-rq]');if(r){inp.value=r.dataset.rq;res(inp.value)}});
    SR.querySelector('.h-rs').addEventListener('touchstart',function(){inp.blur()},{passive:true})}
  var inp=SR.querySelector('input');inp.value=q0||'';res(inp.value);DOC.body.style.overflow='hidden';
  requestAnimationFrame(function(){SR.classList.add('on')});setTimeout(function(){inp.focus()},40);try{history.pushState({hxr:1},'')}catch(e){}}
function rec(q){q=(q||'').trim();if(!q)return;try{var r=JSON.parse(localStorage.getItem('hx_rq')||'[]').filter(function(x){return x!==q});r.unshift(q);localStorage.setItem('hx_rq',JSON.stringify(r.slice(0,6)))}catch(e){}}
function flt(o){var t=ymd(jst());if(o.e&&o.e<t)return false;if(!FL)return true;var n;
  if(FL==='いま開いてる'){n=now(o);return n&&n.on}
  if(FL==='今週末'){var d=jst(),w=d.getUTCDay(),sa=new Date(d.getTime()+((6-w+7)%7)*864e5),su=new Date(sa.getTime()+864e5);if(w===0)sa=new Date(d.getTime()-864e5),su=d;return (!o.s||o.s<=ymd(su))&&(!o.e||o.e>=ymd(sa))}
  if(FL==='もうすぐ終わる')return o.s&&o.s<=t&&o.e&&dd(t,o.e)<=7;
  if(FL==='これから')return o.s&&o.s>t;return o.p===FL}
var SYN={'こうよう':'紅葉','もみじ':'紅葉','はなび':'花火','まつり':'祭','おんせん':'温泉','びじゅつかん':'美術館','はくぶつかん':'博物館','どうぶつえん':'動物園','すいぞくかん':'水族館','よる':'夜','むりょう':'無料','こども':'子ども','ひかり':'光','あかり':'灯','てんらんかい':'展','おおさか':'大阪','きょうと':'京都','ひょうご':'兵庫','こうべ':'神戸','なら':'奈良','しが':'滋賀','わかやま':'和歌山','ひめじ':'姫路','うめだ':'梅田','なんば':'難波','てんのうじ':'天王寺','あらしやま':'嵐山','とうきょう':'東京','よこはま':'横浜','しぶや':'渋谷','しんじゅく':'新宿','ぎんざ':'銀座','あさくさ':'浅草','いけぶくろ':'池袋','かながわ':'神奈川','ちば':'千葉','さいたま':'埼玉','いばらき':'茨城','とちぎ':'栃木','ぐんま':'群馬','かまくら':'鎌倉','はこね':'箱根','まいはま':'舞浜','おだいば':'お台場','まるのうち':'丸の内','ろっぽんぎ':'六本木'};
function qs2(f){var a=[f];if(f.length>=2)for(var k in SYN)if(k.indexOf(f)===0&&a.indexOf(SYN[k])<0)a.push(fold(SYN[k]));return a}
function has(x,Q){x=fold(x);for(var i=0;i<Q.length;i++){var j=x.indexOf(Q[i]);if(j>=0)return j}return -1}
function res(q){var rs=SR.querySelector('.h-rs'),f=fold(q),t=ymd(jst()),Q=qs2(f);
  var L=D.filter(function(o){return o.id&&o.im&&flt(o)});
  if(f){L=L.map(function(o){var s=0,j=has(o.n,Q);if(j===0)s=100;else if(j>0)s=80;else if(has(o.hk,Q)>=0)s=60;else if(has(o.vn,Q)>=0||has(o.ar,Q)>=0||has(o.p,Q)>=0)s=50;else if(has(o.ds,Q)>=0)s=30;var nn=now(o);if(s&&nn&&nn.on)s+=5;return[s,o]}).filter(function(x){return x[0]}).sort(function(a,b){return b[0]-a[0]||((a[1].e||'9')<(b[1].e||'9')?-1:1)}).map(function(x){return x[1]})}
  else L.sort(function(a,b){var x=now(a),y=now(b);return ((y&&y.on)?1:0)-((x&&x.on)?1:0)||((a.e||'9')<(b.e||'9')?-1:1)});
  var h='';
  if(!f&&!FL){var r=[];try{r=JSON.parse(localStorage.getItem('hx_rq')||'[]')}catch(e){}if(r.length)h+='<h3>さいきん探した言葉</h3><div class="h-rc">'+r.map(function(x){return '<button type="button" data-rq="'+esc(x)+'">'+ic('hist')+esc(x)+'</button>'}).join('')+'</div>';h+='<h3>いま・もうすぐ</h3>'}
  else h+='<h3>'+L.length+'件'+(FL?'・'+esc(FL):'')+'</h3>';
  h+=L.slice(0,40).map(function(o,k){return row(o,f,k)}).join('');
  if(!L.length)h+='<p class="h-no">見つかりませんでした。<br>ひらがな・駅の名前・「紅葉」「イルミ」などでも探せます。</p>';
  rs.innerHTML=h;rs.scrollTop=0}
function closeSR(fromPop){if(!SR||!SR.classList.contains('on'))return;SR.classList.remove('on');DOC.body.style.overflow='';SR.querySelector('input').blur();if(!fromPop)try{history.back()}catch(e){}}
/* 下のバーの「さがす」・パソコンの / キー */
DOC.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('#v2bar [data-a=find]');if(!b||!D.length)return;e.preventDefault();e.stopImmediatePropagation();search('')},true);
addEventListener('keydown',function(e){if((e.key==='/'||(e.key==='k'&&(e.metaKey||e.ctrlKey)))&&!/INPUT|TEXTAREA/.test((e.target.tagName||''))&&D.length){e.preventDefault();search('')}});

/* ---------- 下から出る板 ---------- */
var SH=null,BD=null,SO=null;
function sheet(o){if(!o)return;vib();SO=o;
  if(!SH){BD=DOC.createElement('div');BD.className='hxbd';SH=DOC.createElement('div');SH.className='hxsh';SH.setAttribute('role','dialog');SH.setAttribute('aria-modal','true');DOC.body.appendChild(BD);DOC.body.appendChild(SH);bindSH()}
  var t=ymd(jst()),n=now(o),pc=PC[o.p]||'#B97A62',on=favs().indexOf(o.u)>=0,tb=thb(o);
  var pr='';if(o.s&&o.e&&o.e>o.s){var all=dd(o.s,o.e),el=Math.max(0,Math.min(all,dd(o.s,t))),pct=o.s>t?0:Math.round(100*el/all),l=dd(t,o.e);
    pr='<div class="h-pr"><div class="h-l"><span>'+md(o.s)+'（'+W[new Date(o.s+'T00:00:00Z').getUTCDay()]+'）</span><b>'+(o.s>t?'あと'+dd(t,o.s)+'日で始まる':l===0?'きょうまで':'あと'+l+'日')+'</b><span>'+md(o.e)+'（'+W[new Date(o.e+'T00:00:00Z').getUTCDay()]+'）</span></div><div class="h-t"><i data-w="'+pct+'"></i><u data-l="'+pct+'"></u></div></div>'}
  var q=encodeURIComponent((o.vn||o.n)+' '+o.p);
  SH.style.setProperty('--pc',pc);SH.setAttribute('aria-label',o.n);
  SH.innerHTML='<span class="h-hd"></span><div class="h-sc"><div class="h-pv" style="'+(tb?'background-image:url('+tb+')':'')+'"><img src="'+ph(o)+'" alt="'+esc(o.n)+'" decoding="async"><button type="button" class="h-cl" aria-label="閉じる">'+ic('x')+'</button>'+(o.cr?'<small>写真：'+esc(o.cr.replace(/（.*$/,''))+'</small>':'')+'</div>'+
    '<div class="h-bd"><div class="h-tg"><span class="h-pf">'+esc(o.p)+'</span>'+(n?'<span class="'+(n.on?'h-lv':'')+'">'+esc(n.t)+'</span>':'<span>'+esc(stat(o))+'</span>')+(o.h?'<span>'+esc(o.h.replace('-','〜'))+'</span>':'')+'</div>'+
    (o.hk?'<p class="h-hk">'+esc((o.ar?'【'+o.ar+'】':'')+o.hk)+'</p>':'')+'<h2>'+esc(o.n)+'</h2>'+(o.vn?'<div class="h-vn">'+ic('pin')+esc(o.vn)+'</div>':'')+pr+
    (o.ds?'<p class="h-ds">'+esc(o.ds)+'</p>':'')+
    '<div class="h-ac"><button type="button" class="h-fv" aria-pressed="'+on+'">'+ic('star')+(on?'行きたい済み':'行きたい')+'</button><button type="button" class="h-sh2">'+ic('share')+'送る</button><a href="https://www.google.com/maps/search/?api=1&query='+q+'" target="_blank" rel="noopener">'+ic('pin')+'地図</a></div>'+
    '<a class="h-mo" href="/o/'+o.id+'">くわしく見る'+ic('arr')+'</a></div></div>';
  var im=SH.querySelector('.h-pv img');var fin=function(){im.classList.add('h-in')};if(im.complete&&im.naturalWidth)fin();else{im.onload=fin;im.onerror=fin}
  DOC.body.style.overflow='hidden';SH.classList.remove('h-drag');SH.style.transform='';
  requestAnimationFrame(function(){requestAnimationFrame(function(){BD.classList.add('on');SH.classList.add('on');var i=SH.querySelector('.h-pr i'),u=SH.querySelector('.h-pr u');if(i){i.style.width=i.dataset.w+'%';u.style.left='calc('+u.dataset.l+'% - 1px)'}})});
  try{history.pushState({hxh:1},'')}catch(e){}}
function closeSH(fromPop){if(!SH||!SH.classList.contains('on'))return;SH.classList.remove('on');BD.classList.remove('on');SH.style.transform='';DOC.body.style.overflow='';if(!fromPop)try{history.back()}catch(e){}}
function bindSH(){BD.onclick=function(){closeSH()};
  SH.addEventListener('click',function(e){var b=e.target.closest('button,a.h-mo,.h-pv img');if(!b)return;
    if(b.classList.contains('h-cl')){closeSH();return}
    if(b.classList.contains('h-mo')){e.preventDefault();go(SO);return}
    if(b.tagName==='IMG'){zoom(b);return}
    if(b.classList.contains('h-fv')){var f=favs(),i=f.indexOf(SO.u);if(i>=0)f.splice(i,1);else f.push(SO.u);try{localStorage.setItem('tn_fav',JSON.stringify(f))}catch(x){}var y=i<0;b.setAttribute('aria-pressed',y);b.innerHTML=ic('star')+(y?'行きたい済み':'行きたい');vib();
      var n=DOC.querySelector('#v2bar .fvn');if(n){n.textContent=f.length;n.hidden=!f.length}return}
    if(b.classList.contains('h-sh2')){var u=location.origin+'/o/'+SO.id;if(navigator.share)navigator.share({title:SO.n,url:u}).catch(function(){});else{try{navigator.clipboard.writeText(u);b.innerHTML=ic('share')+'コピーしました'}catch(x){}}}});
  /* 下に引くと閉じる（中の文が一番上の時だけ） */
  var y0=0,t0=0,dy=0,sc=null,act=0;
  SH.addEventListener('touchstart',function(e){sc=SH.querySelector('.h-sc');if(sc.scrollTop>0&&!e.target.closest('.h-pv'))return;y0=e.touches[0].clientY;t0=Date.now();dy=0;act=1},{passive:true});
  SH.addEventListener('touchmove',function(e){if(!act)return;dy=e.touches[0].clientY-y0;if(dy<=0){SH.classList.remove('h-drag');SH.style.transform='';return}if(e.cancelable)e.preventDefault();SH.classList.add('h-drag');SH.style.transform='translateY('+dy+'px)'},{passive:false});
  SH.addEventListener('touchend',function(){if(!act)return;act=0;SH.classList.remove('h-drag');var v=dy/Math.max(1,Date.now()-t0);if(dy>130||(dy>40&&v>.6))closeSH();else SH.style.transform=''})}
/* カード・ニュース・おすすめ5 を押すと板（☆・地図・近くの宿・ボタンはそのまま） */
addEventListener('click',function(e){if(e.defaultPrevented||e.metaKey||e.ctrlKey||e.shiftKey||!D.length)return;var t=e.target.closest&&e.target.closest('.card[data-mo],.pr5 a[data-mo],a.mnsl');if(!t)return;
  if(e.target.closest('.wfav,button,.wfv,.ilk,.mpr,a.mp,.inn'))return;var id=t.dataset.mo||(t.getAttribute('href')||'').replace(/^\/o\//,'');var o=ID[id];if(!o)return;
  if(t.closest('.hxemc')&&Date.now()-DRG<250){e.preventDefault();e.stopImmediatePropagation();return}
  e.preventDefault();e.stopImmediatePropagation();sheet(o)},true);

/* ---------- 写真を大きく（PhotoSwipe） ---------- */
function zoom(img){var go2=function(){var w=img.naturalWidth||1200,h=img.naturalHeight||800;var p=new PhotoSwipe({dataSource:[{src:img.currentSrc||img.src,width:w,height:h,alt:img.alt}],index:0,bgOpacity:.96,showHideAnimationType:'zoom',closeTitle:'閉じる',zoomTitle:'拡大'});p.init()};
  if(window.PhotoSwipe)go2();else load('/assets/pswp/photoswipe.umd.min.js',go2)}
DOC.addEventListener('click',function(e){var i=e.target.closest&&e.target.closest('.mph-o img,.sp-ph img');if(!i)return;e.preventDefault();zoom(i)});

/* ---------- 今週ほかにも・ニュース＝Embla ---------- */
var EMB=null,DRG=0;
function embla(){if(!window.HX||EMB)return;var w=DOC.querySelector('.mnews'),tr=w&&w.querySelector('.mntr');if(!tr||tr.classList.contains('hxem'))return;var sl=[].slice.call(tr.querySelectorAll(':scope>.mnsl'));if(sl.length<2)return;
  tr.scrollTo=function(){};tr.scrollLeft=0;tr.classList.add('hxem');w.classList.add('hxe');var c=DOC.createElement('div');c.className='hxemc';sl.forEach(function(s){c.appendChild(s)});tr.appendChild(c);
  var pg=DOC.createElement('div');pg.className='hxpg';pg.innerHTML=sl.map(function(){return '<i><b></b></i>'}).join('');(w.querySelector('.mndt')||tr).insertAdjacentElement('afterend',pg);
  EMB=HX.Embla(tr,{loop:true,align:'start',skipSnaps:false,duration:28});
  var bars=pg.querySelectorAll('i'),AT=null,PD=6000;
  function prog(){var i=EMB.selectedScrollSnap();bars.forEach(function(b,k){b.classList.toggle('h-dn',k<i);var x=b.firstChild;x.style.transition='none';x.style.width=k<i?'100%':'0';if(k===i&&!RM){x.offsetWidth;x.style.transition='width '+PD+'ms linear';x.style.width='100%'}});sl.forEach(function(s,k){s.classList.toggle('cur',k===i)})}
  function auto(){clearTimeout(AT);if(RM)return;AT=setTimeout(function(){var r=tr.getBoundingClientRect();if(!DOC.hidden&&r.bottom>0&&r.top<innerHeight)EMB.scrollNext();else auto()},PD)}
  function par(){var p=EMB.scrollProgress(),sn=EMB.scrollSnapList(),eng=EMB.internalEngine();sn.forEach(function(s,i){var d=s-p;if(eng.options.loop)eng.slideLooper.loopPoints.forEach(function(lp){var tg=lp.target();if(i===lp.index&&tg!==0){var sg=Math.sign(tg);if(sg===-1)d=s-(1+p);if(sg===1)d=s+(1-p)}});var im=sl[i].querySelector('img');if(im)im.style.transform='translate3d('+(d*-26)+'%,0,0)'})}
  EMB.on('select',function(){prog();auto()});EMB.on('pointerDown',function(){clearTimeout(AT);bars.forEach(function(b){var x=b.firstChild;var cw=getComputedStyle(x).width;x.style.transition='none';x.style.width=cw})});var PDN=0,MOV=0;EMB.on('pointerDown',function(){PDN=1;MOV=0});EMB.on('scroll',function(){if(PDN)MOV=1});EMB.on('pointerUp',function(){if(MOV)DRG=Date.now();PDN=0;auto()});
  EMB.on('scroll',par);EMB.on('reInit',par);par();prog();auto()}

/* ---------- 写真の前のぼかし色・並び替えの動き・iPhone の改行 ---------- */
function th(){if(!window.HX)return;DOC.querySelectorAll('img[src*="/assets/ph/"]:not([data-hxt])').forEach(function(i){i.dataset.hxt=1;if(i.complete&&i.naturalWidth)return;var f=(i.getAttribute('src').split('/').pop()||'').split('?')[0];var h=PHH[f];if(!h)return;var p=i.parentElement;if(!p)return;try{var b=atob(h),a=new Uint8Array(b.length);for(var k=0;k<b.length;k++)a[k]=b.charCodeAt(k);p.style.setProperty('background-image','url('+HX.th(a)+')','important');p.classList.add('hxth')}catch(e){}})}
var AA=[];function anim(){if(!window.HX||RM)return;var ps=[];DOC.querySelectorAll('.card[data-mo]').forEach(function(a){var p=a.parentElement;if(p&&ps.indexOf(p)<0)ps.push(p)});ps.forEach(function(p){if(AA.indexOf(p)>=0)return;AA.push(p);try{HX.autoAnimate(p,{duration:280,easing:'cubic-bezier(.2,.8,.2,1)'})}catch(e){}})}
var BX=0,BXT='h1,h2,h3,.mhh,.mntx b,.t,.mhk,.mhk-o,.nm,.pt,.sp-pt';function bx(){if(BX===1||(window.CSS&&CSS.supports&&CSS.supports('word-break','auto-phrase')))return;
  if(!window.HXB){if(!BX){BX=2;load('/assets/hx-bx.js',bx)}return}DOC.querySelectorAll(BXT).forEach(function(e){if(e.dataset.hxb||e.children.length>2)return;e.dataset.hxb=1;try{HXB.applyToElement(e);e.classList.add('hxbx')}catch(x){}})}

/* ---------- 動かす ---------- */
var RQ=null;function run(){clearTimeout(RQ);RQ=setTimeout(function(){try{rail()}catch(e){}try{island()}catch(e){}try{embla()}catch(e){}try{th()}catch(e){}try{anim()}catch(e){}try{bx()}catch(e){}},120)}
load('/assets/hx-lib.js?v=1',run);
fetch('/assets/phh.json?v=1').then(function(r){return r.json()}).then(function(j){PHH=j;run()}).catch(function(){});
fetch('/assets/mihon.json?v='+(window.__mhv||3)).then(function(r){return r.json()}).then(function(j){for(var x in j){var o=j[x];if(o.id&&!ID[o.id]){ID[o.id]=o;D.push(o)}}run();
  try{new MutationObserver(function(m){for(var i=0;i<m.length;i++){var n=m[i].target;if(n.closest&&n.closest('.hxsv,.hxsr,.hxsh,.hxis'))continue;run();return}}).observe(DOC.body,{childList:true,subtree:true})}catch(e){}}).catch(function(){});
})();
