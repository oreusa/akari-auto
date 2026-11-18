/* 11/18 関東（LIFE NOTE）の見本。月の links/assets/mihon.js を関東のカード（.card.it・a.cd）と都県に合わせた写し。
   1件ページ（/o/）の写真は spot_pages.py が書く（ここでは足さない）。直す時は月の方と両方 */
/* 11/18 今のHPのクオリティアップ（見本）。今のページ・部品はそのまま、足すだけ。
   ?mihon=1 を付けた人だけに出る（night.js が読み込む・?mihon=0 で消える）。
   足す物：カードの絵の所に本物の写真／【地名】の一言／いまライトアップ中・あと◯分／カードを押すと1件ページ／
   1件ページに 写真・どんな催し？・行きたい・カレンダー・送る。表は /assets/mihon.json（tools/mihon/build.py）。 */
(function(){
if(window.__mihon)return;window.__mihon=1;
var D={},ID={},READY=0;
var css=
/* カードの絵の所（66px の角丸）に写真。英字の札（LIGHT など）と日付の札は今のまま */
'.cmb .ib.mph{background:#ddd}'+
'.cmb .ib.mph img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;border-radius:inherit}'+
'.cmb .ib.mph svg,.cmb .ib.mph::before{display:none!important}'+
'.cmb .ib.mph::after{z-index:2}'+
'.cmb .ib.mph .lb{z-index:1;color:#fff;opacity:1;bottom:0;padding:9px 0 5px .22em;background:linear-gradient(transparent,rgba(20,16,12,.55));text-shadow:0 1px 2px rgba(0,0,0,.3)}'+
/* 【地名】の一言（題の上の小さな1行） */
'.mhk{display:block;font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:12.5px;line-height:1.5;color:var(--pc,#6b625b);margin:2px 0 3px;letter-spacing:.02em}'+
'a.fc .mhk{font-size:11.5px;margin:1px 0 2px}'+
/* いまライトアップ中（今の「開催中」の札の横） */
'.mnow{display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:700;line-height:1;padding:5px 9px 5px 8px;border-radius:999px;background:#E7F4EC;color:#1E7A4A;white-space:nowrap}'+
'.mnow::before{content:"";width:6px;height:6px;border-radius:50%;background:#22A35A;box-shadow:0 0 0 0 rgba(34,163,90,.5);animation:mnp 1.8s ease-out infinite}'+
'.mnow.soon{background:#FBF0E2;color:#A55A12}.mnow.soon::before{background:#E08A2E;animation:none}'+
'@keyframes mnp{0%{box-shadow:0 0 0 0 rgba(34,163,90,.5)}80%,100%{box-shadow:0 0 0 7px rgba(34,163,90,0)}}'+
'@media (prefers-reduced-motion:reduce){.mnow::before{animation:none}}'+
'.mnowl{margin-top:8px}'+
/* おすすめ5 の小さな絵 → 写真 */
'.pr5 .ti.mph{overflow:hidden;padding:0!important}.pr5 .ti.mph img{width:100%;height:100%;object-fit:cover;display:block}.pr5 .ti.mph svg{display:none}'+
/* 1件ページ：写真・一言・どんな催し？・ボタン */
'img.mfade{opacity:0;transform:scale(1.035);transition:opacity .55s cubic-bezier(.2,.7,.2,1),transform .9s cubic-bezier(.2,.7,.2,1)}img.mfade.in{opacity:1;transform:none}'+
'.mbp,.mnsl,.m1,.cmb .ib.mph,.pr5 .ti.mph{background:linear-gradient(100deg,#ece8e3 30%,#f6f3ef 50%,#ece8e3 70%) 0 0/300% 100%!important;animation:mshm 1.3s linear infinite}'+
'.mbp.ld,.mnsl.ld,.m1.ld,.cmb .ib.mph.ld,.pr5 .ti.mph.ld{animation:none}'+
'@keyframes mshm{to{background-position:-300% 0}}'+
'.mnews .mnsl img.in{transform:scale(1.0);transition:opacity .55s,transform 7s linear}.mnews .mnsl.cur img.in{transform:scale(1.07)}'+
':is(.card,a.cd).mbig,.mnews .mnsl,.pr5 .m1{-webkit-tap-highlight-color:transparent}.mnews .mnsl:active,.pr5 .m1:active{scale:.985;transition:scale .15s}'+
'@media (prefers-reduced-motion:reduce){img.mfade{transition:none;transform:none}.mnews .mnsl.cur img.in{transform:none}.mbp,.mnsl,.m1{animation:none!important}}'+
'.mph-o{margin:0 0 14px}.mph-o img{display:block;width:100%;aspect-ratio:3/2;object-fit:cover;border-radius:18px;background:#eee;box-shadow:0 14px 30px -18px rgba(40,30,20,.45)}'+
'.mph-o figcaption{font-size:10.5px;color:#9a928b;margin:7px 2px 0;line-height:1.5}.mph-o figcaption a{color:inherit}'+
'.head .mhk-o{font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:14px;color:var(--pc,#6b625b);margin:10px 0 0;letter-spacing:.03em;line-height:1.6;position:relative}'+
'.mig{margin:18px 0 0}.mig>span{display:block;font-size:12px;font-weight:700;color:#71717A;letter-spacing:.06em;margin:0 0 8px}.mig .instagram-media{margin:0!important;min-width:0!important;width:100%!important;border-radius:8px!important}.mig iframe{border-radius:8px!important}.migl{display:inline-flex;align-items:center;gap:8px;padding:11px 16px;border:1px solid #E4E4E7;border-radius:999px;font-weight:700;font-size:14px;color:#18181B;text-decoration:none;background:#fff}.migl i{width:18px;height:18px;border-radius:5px;background:linear-gradient(45deg,#F58529,#DD2A7B,#8134AF);display:inline-block}html.night .mig .instagram-media,html.night .mig iframe{filter:invert(1) hue-rotate(180deg)}'+
'section.mnews .mnh b{white-space:nowrap;font-size:16px;letter-spacing:.02em}section.mnews .mnlive{margin-right:0;padding:5px 9px}section.mnews .mnh time{display:none}.mnews .mnh time{display:none}.mnews.mnc{margin:14px 0 2px}.mnews.mnc .mnh time{display:none}.mnews.mnc .mnh b{white-space:nowrap}.mnews.mnc .mnh{padding-bottom:8px}.mnews.mnc .mnh small{display:none}.mnews.mnc .mnh b{font-size:16px}.mnews.mnc .mnsl{flex-basis:84%;aspect-ratio:16/10;border-radius:14px}.mnews.mnc .mntx b{font-size:16px}.mnews.mnc .mndt{display:none}'+
':is(.card,a.cd) .kv.mkh{display:none!important}'+
'.mds{background:#F4F4F5;border-radius:4px;padding:16px 16px 15px;margin:14px 0 0}.mds span{display:block;font-size:10.5px;color:#8a837d;letter-spacing:.08em;margin-bottom:6px}.mds p{margin:0;font-size:14.5px;line-height:1.9;color:#2B2622}'+
'.act a.mfav[aria-pressed=true]{background:#FFF7E0;border-color:#E2B53B;color:#7A5A00}'+
'.mshr{display:none;gap:8px;margin-top:8px}.mshr.open{display:flex}.mshr a{flex:1;text-align:center;font-size:13px;padding:11px 0;border-radius:10px;border:1px solid #ddd;color:#2B2622;text-decoration:none;font-weight:700}'+
/* 夜：ページ全体が反転するので、写真だけ元に戻す（night.js の決まり） */

'html.night .mnow{background:#E7F4EC}'+
/* 写真のあるカード：上に大きな写真。カードの絵のタイルと日付の札は今のまま、写真の下の端に少し重ねる */
'html body :is(.card,a.cd).mbig.mbig.mbig.mbig.mbig.mbig{padding-top:166px!important;min-height:0;position:relative;overflow:hidden}'+
':is(.card,a.cd).mbig .mbp{position:absolute;left:0;right:0;top:0;height:150px;border-radius:8px 8px 0 0;overflow:hidden;background:#e9e6e2}'+
':is(.card,a.cd).mbig .mbp .mvn{position:absolute;left:8px;top:8px;font-style:normal;font-size:10.5px;font-weight:700;color:#fff;background:rgba(30,24,20,.62);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);border-radius:999px;padding:4px 9px;max-width:70%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'+
':is(.card,a.cd).mbig .mbp img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .5s ease}'+
':is(.card,a.cd).mbig:hover .mbp img{transform:scale(1.03)}'+
':is(.card,a.cd).mbig .mbp small{position:absolute;right:8px;bottom:6px;font-size:9px;color:#fff;opacity:.85;text-shadow:0 1px 2px rgba(0,0,0,.6);max-width:60%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'+
':is(.card,a.cd).mbig .cmb{top:120px!important;z-index:2}'+
':is(.card,a.cd).mbig .cmb .ib{box-shadow:0 0 0 3px #fff,0 10px 18px -10px rgba(0,0,0,.45)}'+
':is(.card,a.cd).mbig .wfav{z-index:3}'+
/* きょうのおでかけニュース（3つの入口のすぐ下） */
'.mnews{margin:22px 0 6px}'+
'.mnews .mnh{display:flex;align-items:flex-end;justify-content:space-between;padding:0 2px 10px}'+
'.mnews .mnh small{display:block;font-family:Jost,sans-serif;font-size:10px;letter-spacing:.28em;color:#B97A62;margin-bottom:5px}'+
'.mnews .mnh b{font-family:"Shippori Mincho","Noto Serif JP",serif;font-weight:600;font-size:19px;letter-spacing:.12em;color:#2B2622}'+
'.mnews .mnh time{font-size:11.5px;color:#8a837d;letter-spacing:.04em}'+
'.mnews .mnh{gap:8px}.mnews .mnlive{margin-left:auto;margin-right:8px;display:inline-flex;align-items:center;gap:6px;font-size:11px;font-weight:700;color:#1E7A4A;background:#E7F4EC;border-radius:999px;padding:5px 10px;white-space:nowrap}.mnews .mnlive b{font-family:Jost,sans-serif;font-size:13px}.mnews .mnlive i{width:7px;height:7px;border-radius:50%;background:#22A35A;animation:mnp 1.8s ease-out infinite}.mnews .mnlive i.s{background:#E08A2E;animation:none}.mnews .mnlive:has(i.s){color:#A55A12;background:#FBF0E2}'+'.mnews .mntr{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;gap:10px;scrollbar-width:none;-webkit-overflow-scrolling:touch;margin:0 -2px;padding:0 2px 4px}.mnews .mntr::-webkit-scrollbar{display:none}'+
'.mnews .mnsl{position:relative;flex:0 0 100%;scroll-snap-align:start;border-radius:16px;overflow:hidden;aspect-ratio:4/3;display:block;color:#fff;text-decoration:none;background:#2b2622;box-shadow:0 16px 30px -20px rgba(40,30,20,.6)}'+
'.mnews .mnsl img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}'+
'.mnews .mnsl::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) 38%,rgba(10,8,6,.78) 100%)}'+
'.mnews .mntx{position:absolute;left:16px;right:16px;bottom:15px;z-index:1}'+
'.mnews .mntg{display:inline-flex;gap:6px;align-items:center;font-size:11px;font-weight:700;background:rgba(255,255,255,.94);color:#2B2622;border-radius:999px;padding:5px 10px;margin-bottom:9px}'+
'.mnews .mntg i{font-style:normal;color:var(--pc,#B97A62)}'+
'.mnews .mntx b{display:block;font-family:"Zen Kaku Gothic New",sans-serif;font-weight:900;font-size:21px;line-height:1.38;letter-spacing:.01em;text-shadow:0 1px 10px rgba(0,0,0,.35)}'+
'.mnews .mntx .mnn{display:block;font-size:12px;opacity:.9;margin-top:5px}'+
'.mnews .mncr{position:absolute;top:8px;right:10px;z-index:1;font-size:9px;opacity:.8;text-shadow:0 1px 2px rgba(0,0,0,.6)}'+
'.mnews .mndt{display:flex!important;flex-direction:row;justify-content:center;gap:6px;margin-top:10px}.mnews .mndt i{display:block;flex:none;width:6px;height:6px;border-radius:3px;background:#d6d1cb;transition:width .3s}.mnews .mndt i.on{width:18px;background:#2B2622}'+
/* おすすめ5 の1位：大きな写真 */
'.pr5 .m1{display:block;position:relative;margin:4px 0 2px;border-radius:12px;overflow:hidden;aspect-ratio:16/9;background:#e9e6e2}.pr5 .m1 img{width:100%;height:100%;object-fit:cover;display:block}'+
'.pr5 .m1 em{position:absolute;left:10px;top:10px;font-style:normal;font-family:Jost,sans-serif;font-weight:600;font-size:11px;letter-spacing:.14em;background:#fff;color:#C0563C;border-radius:999px;padding:4px 10px}'+
'html.night .mnews .mnsl{filter:invert(1) hue-rotate(180deg)}html.night .mnews .mnsl img{filter:none!important}'+
'html.night :is(.card,a.cd).mbig .cmb .ib{box-shadow:0 0 0 3px #fff}'+
'html.night .mnews .mndt i.on{background:#2B2622}'+
/* 11/18 下の FOLLOW：ページごとに 四角い3つの枠・下線の文字・マーク とばらばらだった → 表紙と同じ細い線のマークにそろえる */
'html body .sns{text-align:center}html body div.sns h2{font:400 10.5px Jost,sans-serif;letter-spacing:.42em;color:#8C7B6E;margin:0 0 10px}'+
'html body div.sns a:is([href*="instagram"],[href*="threads"],[href*="x.com"]):not(.co){font-size:0!important;border:0!important;background:none!important;width:44px!important;height:44px!important;padding:0!important;margin:0 6px!important;border-radius:50%!important;display:inline-grid!important;place-items:center;color:#2B2622!important;box-shadow:none!important;letter-spacing:0!important}'+
'html body div.sns a:is([href*="instagram"],[href*="threads"],[href*="x.com"]):not(.co) span{display:none!important}html body div.sns a:is([href*="instagram"],[href*="threads"],[href*="x.com"]):not(.co):before{content:"";width:20px;height:20px;background:currentColor;-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat}'+
'html body .sns a[href*="instagram"]{--ic:url("data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%20viewBox%3D%270%200%2024%2024%27%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.5%27%3E%3Crect%20x%3D%273.5%27%20y%3D%273.5%27%20width%3D%2717%27%20height%3D%2717%27%20rx%3D%275%27/%3E%3Ccircle%20cx%3D%2712%27%20cy%3D%2712%27%20r%3D%274%27/%3E%3C/svg%3E")}html body .sns a[href*="threads"]{--ic:url("data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%20viewBox%3D%270%200%2024%2024%27%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.5%27%20stroke-linecap%3D%27round%27%3E%3Cpath%20d%3D%27M16.6%2011.3c-.4-2.6-2.1-3.9-4.5-3.9-2.6%200-4.4%201.9-4.4%204.6%200%202.9%201.9%204.9%204.6%204.9%202.3%200%203.6-1.3%203.6-2.9%200-1.7-1.4-2.6-3.3-2.6-1.7%200-2.6.8-2.6%201.8%200%20.9.8%201.5%201.8%201.5%202.2%200%203.3-1.9%203-5.6%27/%3E%3Cpath%20d%3D%27M19.5%208.2C18.4%205.1%2015.7%203.5%2012.2%203.5%207%203.5%203.8%207%203.8%2012s3.2%208.5%208.4%208.5c3.4%200%205.9-1.5%207-4.1%27/%3E%3C/svg%3E")}html body .sns a[href*="x.com"]{--ic:url("data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A//www.w3.org/2000/svg%27%20viewBox%3D%270%200%2024%2024%27%20fill%3D%27none%27%20stroke%3D%27black%27%20stroke-width%3D%271.4%27%3E%3Cpath%20d%3D%27M4%204l16%2016M20%204L4%2020%27/%3E%3C/svg%3E")}'+
/* 不動産のご相談：申し込みボタン */
'html body .sns a.co.mcta1{background:#2B2622;color:#fff;border-color:#2B2622;padding:22px 20px 18px;box-shadow:0 22px 34px -22px rgba(30,20,10,.75)}'+
'html body .sns a.co.mcta1::before{color:#E2C2AB}html body .sns a.co.mcta1::after{display:none}html body .sns a.co.mcta1>span{color:rgba(255,255,255,.72)}'+
'.mctab{display:flex;align-items:center;gap:8px;margin-top:16px;background:#fff;color:#2B2622;border-radius:999px;padding:14px 18px;font:700 15px "Zen Kaku Gothic New",sans-serif;font-style:normal;letter-spacing:.04em}'+
'.mctab b{color:#C0563C}.mctab small{font:500 11px Jost,"Zen Kaku Gothic New",sans-serif;color:#8C7B6E;border:1px solid #E3DCD5;border-radius:999px;padding:2px 8px}.mctab i{margin-left:auto;font-style:normal;font-family:Jost;font-size:18px;transition:transform .25s}'+
'.mcta1:hover .mctab i,.mcta1:active .mctab i{transform:translateX(5px)}'+
'html body div.sns h2{text-align:center!important}'+
/* 11/18 見やすさの点検（axe-core）で薄すぎた小さな灰色の字：同じ色みのまま少しだけ濃く（白地で 4.5:1 以上） */
'html body .oh{color:#767B82!important}html body button[data-t][role=tab]:not([aria-selected=true]){color:#6E655E!important}html body button[data-t][role=tab] i{color:#467A54!important}html body .nft small{color:#6E655E!important}html body .mctab>span{color:#2B2622!important}'+
'html body .kicker,html body .lists a.ls .en{color:#7C6A5A!important}html body .prom h2,html body div.sns h2,html body .ft,html body .uhl b,html body .wrap>p,html body a[href$="privacy"]{color:#76685D!important}'+
'html body .sns a.co:not(.mcta1) span{color:#76685D}.mctab small{color:#6E655E}'+
/* 11/18 日本語の改行：言葉の途中で切らない（「山陽高／砂駅」→「山陽／高砂駅」）・見出しの最後の1文字だけの行をなくす */
'html[lang=ja] body :is(h1,h2,h3,.t,.m,.nm,.pl,.hk,.ds,.mhh,.mhn,.big b,figcaption,.card p,li a){word-break:auto-phrase;text-wrap:pretty}html[lang=ja] body :is(h1,h2,h3,.t,.nm,.mhh){text-wrap:balance}'+
/* 11/18 入口：今週の1件（画面いっぱいの写真・ゆっくりズーム） */
'.mhero{margin:6px -16px 0;position:relative}'+
'.mhero .mhl{position:relative;display:block;height:min(78svh,620px);min-height:440px;overflow:hidden;color:#fff;text-decoration:none;background:#2b2622;-webkit-tap-highlight-color:transparent}'+
'.mhero .mhl img{position:absolute;inset:0;width:100%;height:100%;max-width:none;object-fit:cover;border-radius:0}'+
''+
'@keyframes mkb{from{transform:scale(1.02) translate3d(0,0,0)}to{transform:scale(1.14) translate3d(-2%,-1.5%,0)}}'+
'.mhero .mhl::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(12,9,7,.42) 0%,rgba(12,9,7,0) 26%,rgba(12,9,7,0) 42%,rgba(12,9,7,.86) 100%);pointer-events:none}'+
'.mhero .mhtop{position:absolute;left:22px;top:20px;z-index:1;display:flex;align-items:center;gap:10px;font-size:12px;font-weight:700;letter-spacing:.14em}'+
'.mhero .mhtop b{font-family:Jost,sans-serif;font-weight:500;font-size:11px;letter-spacing:.32em}.mhero .mhtop i{width:22px;height:1px;background:rgba(255,255,255,.7)}'+
'.mhero .mhtx{position:absolute;left:22px;right:22px;bottom:26px;z-index:1;display:block}'+
'.mhero .mhtg{display:inline-flex;gap:7px;align-items:center;font-size:11.5px;font-weight:700;background:rgba(255,255,255,.95);color:#2B2622;border-radius:999px;padding:6px 12px;margin-bottom:14px}.mhero .mhtg i{font-style:normal;color:var(--pc)}'+
'.mhero .mhh{display:block;font-family:"Shippori Mincho","Noto Serif JP",serif;font-weight:700;font-size:clamp(25px,7.4vw,31px);line-height:1.42;letter-spacing:.04em;text-shadow:0 2px 18px rgba(0,0,0,.35);text-wrap:balance}'+
'.mhero .mhn{display:block;font-size:13px;opacity:.88;margin-top:9px;letter-spacing:.03em}'+
'.mhero em{display:inline-flex;align-items:center;gap:10px;font-style:normal;font-weight:700;font-size:13.5px;letter-spacing:.06em;margin-top:18px;padding:12px 20px;border-radius:999px;background:#fff;color:#2B2622;box-shadow:0 10px 24px -12px rgba(0,0,0,.6)}'+
'.mhero em span{transition:transform .25s}.mhero .mhl:hover em span,.mhero .mhl:active em span{transform:translateX(4px)}'+
'.mhero .mhcr{position:absolute;right:12px;top:22px;z-index:1;font-size:9px;opacity:.75;max-width:40%;text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'+
'.mnews.mncv{margin:22px 0 4px}.mnews .mnlive[hidden]{display:none!important}'+
'html.night .mhero .mhl{filter:invert(1) hue-rotate(180deg)}html.night .mhero img{filter:none!important}'+
/* スクロールで出てくる */
'.mrv{opacity:0;transform:translate3d(0,22px,0);transition:opacity .8s cubic-bezier(.2,.7,.2,1),transform .9s cubic-bezier(.2,.7,.2,1)}.mrv.mrvin{opacity:1;transform:none}'+
'.mhero .mhtx.mrv{transition-delay:.15s}'+
'@media (prefers-reduced-motion:reduce){.mhero .mhl img.in{animation:none}.mrv{opacity:1;transform:none;transition:none}}';
var st=document.createElement('style');st.textContent=css;(document.head||document.documentElement).appendChild(st);
function k(s){return (s||'').replace(/\s+/g,'')}
function find(t){return D[k(t)]}
function esc(s){return String(s||'').replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function hook(o){return o.hk?(o.ar?'【'+o.ar+'】':'')+o.hk:''}
/* 日本の時刻 */
function jst(){return new Date(Date.now()+9*36e5)}
function ymd(d){return d.toISOString().slice(0,10)}
function closed(o,d){var t=ymd(d),w=d.getUTCDay();
  if(o.cl){if(o.cl.indexOf('-'+t)>=0)return true;if(o.cl.indexOf('+'+t)>=0)return false;}
  if(o.dy&&/^wd:/.test(o.dy)&&o.dy.slice(3).indexOf(String(w))<0)return true;return false}
function now(o){if(!o||!o.h)return null;var d=jst(),t=ymd(d);if(!(o.s<=t&&o.e>=t)||closed(o,d))return null;
  var m=d.getUTCHours()*60+d.getUTCMinutes(),x=o.h.split('-').map(function(v){var a=v.split(':');return a[0]*60+ +a[1]});if(x.length<2)return null;
  var night=x[0]>=15*60;
  if(m>=x[0]&&m<x[1]){var l=x[1]-m;if(l<=60)return{c:'',t:'あと'+l+'分で終わり'};return{c:'',t:night?'いまライトアップ中':'いま開いています'}}
  if(m<x[0]&&x[0]-m<=180)return{c:'soon',t:(night?'今夜':'きょう')+o.h.split('-')[0]+'から'};return null}
function nowPill(host,o,cls){var n=now(o),p=host.querySelector('.mnow');if(!n){if(p)p.remove();return}
  if(!p){p=document.createElement('span');host.appendChild(p)}p.className='mnow '+(n.c||'')+(cls?' '+cls:'');p.textContent=n.t}
function photo(box,o,big){if(box.classList.contains('mph'))return;box.classList.add('mph');var i=document.createElement('img');i.alt='';i.loading='lazy';i.decoding='async';i.className='mfade';i.src='/assets/ph/'+(big?'':'t/')+o.im;box.insertBefore(i,box.firstChild)}
/* カード（一覧・府県・イルミ・紅葉・泊まり・いまから・1件ページの「ほかのおでかけ」） */
function slim(){if(/^\/hatsumode/.test(location.pathname))return;/* 初詣は時間・交通規制がページの中身なので隠さない */document.querySelectorAll(':is(.card,a.cd) .kv:not(.mk)').forEach(function(v){v.classList.add('mk');var l=(v.querySelector('span')||{}).textContent||'';if(!/見頃|開く日/.test(l))v.classList.add('mkh')})}
function cards(){slim();
  document.querySelectorAll(':is(.card,a.cd),a.fc').forEach(function(a){
    var tt=a.querySelector(a.matches('a.fc')?':scope>b':'.t,.nm');if(!tt)return;var o=find(tt.textContent);if(!o)return;
    if(o.im){if(a.matches(':is(.card,a.cd)')&&!o.wk){if(!a.querySelector('.mbp')){var f=document.createElement('div');f.className='mbp';f.innerHTML='<img class="mfade" src="/assets/ph/s/'+o.im+'" alt="" loading="lazy" decoding="async"><small>'+esc(o.cr.replace(/（.*$/,''))+'</small>'+(o.vn&&o.n.indexOf(o.vn)<0?'<i class="mvn">'+(o.vk?'場所：':'会場：')+esc(o.vn)+'</i>':'');a.insertBefore(f,a.firstChild);a.classList.add('mbig');var go=a.querySelector(':scope>.go');if(go){var cs=getComputedStyle(go);if(cs.position==='absolute'&&parseFloat(cs.top)<60)go.style.top=(parseFloat(cs.top)+152)+'px'}}}
      else if(!a.querySelector('.mbp')){var ib=a.querySelector('.cmb .ib');if(ib)photo(ib,o)}}
    if(!a.dataset.mh){var h=hook(o);if(h){var s=document.createElement('span');s.className='mhk';s.textContent=h;tt.parentNode.insertBefore(s,tt)}a.dataset.mh=1}
    var row=a.querySelector('.v2c');if(row)nowPill(row,o);
    if(o.id&&a.matches(':is(.card,a.cd)'))a.dataset.mo=o.id;
  });
  document.querySelectorAll('.pr5 a').forEach(function(a){var b=a.querySelector('.tx b');if(!b)return;var o=find(b.textContent);if(!o)return;
    var ti=a.querySelector('.ti');if(ti&&o.im)photo(ti,o);if(o.id)a.dataset.mo=o.id});
  news();cover();reveal();cta();hitech();a11y();
}

/* きょうのおでかけニュース：3つの入口のすぐ下。写真のある・いま開催中か7日以内に始まる催しから、終わりが近い順に4つ */
function news(CV){var pa=location.pathname,KD=/^\/illumination/.test(pa)?'il':/^\/koyo/.test(pa)?'ky':'',q=CV?CV.q:document.querySelector('.qk')||(KD&&(document.querySelector('.tnb')||document.querySelector('nav.sw')));if(!q||document.querySelector('.mnews'))return;
  var PF={tokyo:'東京',kanagawa:'神奈川',saitama:'埼玉',chiba:'千葉',ibaraki:'茨城',tochigi:'栃木',gunma:'群馬'},pm=pa.match(/-(tokyo|kanagawa|saitama|chiba|ibaraki|tochigi|gunma)/),pf=pm?PF[pm[1]]:'';
  var RX=KD==='il'?/イルミ|ライト|灯|光|ルミナ|クリスマス|ツリー|夜/:KD==='ky'?/紅葉|もみじ|楓|錦秋|ライトアップ/:null;
  var t=ymd(jst()),t7=ymd(new Date(jst().getTime()+7*864e5)),L=[];
  var ON={};if(KD)document.querySelectorAll(':is(.card,a.cd) :is(.t,.nm)').forEach(function(e){var o=find(e.textContent);if(o)ON[o.n]=1});
  for(var x in D){var o=D[x];if(!o.im||o.wk||(o.vn&&o.n.indexOf(o.vn)<0)||(pf&&o.p!==pf))continue;if(KD){if(ON[o.n]&&(o.id||o.u)&&(!o.e||o.e>=t)&&(!o.s||o.s<=t7))L.push(o)}else if(RX){if(RX.test(o.n+(o.hk||''))&&(o.id||o.u)&&(!o.e||o.e>=t)&&(!o.s||o.s<=t7))L.push(o)}else if(o.id&&(o.hk||CV)&&(CV?(!o.e||o.e>=t)&&(!o.s||o.s<=t7):o.e>=t&&o.s<=t7))L.push(o)}
  var sc=function(o){return (/イルミ|ライト|灯|光|夜|ルミナ|紅葉|もみじ/.test(o.n+o.hk)?0:2)+(o.s<=t?0:1)};
  L.sort(function(a,b){return sc(a)-sc(b)||(a.e<b.e?-1:1)});
  var P={};L=L.filter(function(o){if(!pf&&P[o.p]>=1&&L.length>6)return false;P[o.p]=(P[o.p]||0)+1;return true}).slice(0,CV?6:5);if(CV){if(!L.length)return;q=CV.hero(L.shift());KD='cv'}if(!L.length)return;
  var PC={"東京":"#4F86C6","神奈川":"#3FA3B5","埼玉":"#E09A3E","千葉":"#D9775A","茨城":"#5FA06A","栃木":"#D2697E","群馬":"#9C7BB8"},W='日月火水木金土',d=jst();
  var h='<div class="mnh"><div><small>TODAY’S NEWS</small><b>'+(KD==='il'?'今夜のイルミ':KD==='ky'?'いまの紅葉':KD==='cv'?'今週ほかにも':'きょうのおでかけニュース')+'</b></div><span class="mnlive"></span><time>'+(d.getUTCMonth()+1)+'/'+d.getUTCDate()+'（'+W[d.getUTCDay()]+'）</time></div><div class="mntr">';
  L.forEach(function(o){var st=!o.s?'見頃':o.s<=t?'開催中':(+o.s.slice(5,7))+'/'+(+o.s.slice(8))+'から';h+='<a class="mnsl" href="'+(o.id?'/o/'+o.id:esc(o.u)+'" target="_blank" rel="noopener')+'" style="--pc:'+(PC[o.p]||'#B97A62')+'"><img class="mfade" src="/assets/ph/'+o.im+'" alt="" decoding="async"'+(L.indexOf(o)===0?' fetchpriority="high"':' loading="lazy"')+'><span class="mncr">写真：'+esc(o.cr.replace(/（.*$/,''))+'</span><span class="mntx"><span class="mntg"><i>'+esc(o.p)+'</i>'+st+(o.e?'・'+(+o.e.slice(5,7))+'/'+(+o.e.slice(8))+'まで':'')+'</span>'+(hook(o)?'<b>'+esc(hook(o))+'</b><span class="mnn">'+esc(o.n)+'</span>':'<b>'+esc(o.n)+'</b>')+'</span></a>'});
  h+='</div><div class="mndt">'+L.map(function(o,i){return '<i'+(i?'':' class="on"')+'></i>'}).join('')+'</div>';
  var w=document.createElement('section');w.className='mnews'+(KD?' mnc':'')+(KD==='cv'?' mncv':'');w.setAttribute('aria-label','きょうのおでかけニュース');w.innerHTML=h;q.parentNode.insertBefore(w,q.nextSibling);
  var lv=w.querySelector('.mnlive');function live(){var on=0,soon=0;for(var x in D){var n=now(D[x]);if(n){if(n.c==='soon')soon++;else on++}}lv.innerHTML=on?'<i></i>いま開いてる <b>'+on+'</b>':soon?'<i class="s"></i>まもなく点灯 <b>'+soon+'</b>':'';lv.hidden=!(on||soon)}live();setInterval(live,60000);
  var tr=w.querySelector('.mntr'),dots=w.querySelectorAll('.mndt i'),sl=w.querySelectorAll('.mnsl'),cur=0,hold=0;if(sl[0])sl[0].classList.add('cur');
  tr.addEventListener('scroll',function(){var st=sl[0]?sl[0].offsetWidth+10:tr.clientWidth,i=Math.round(tr.scrollLeft/st);if(i!==cur){cur=i;dots.forEach(function(e,k){e.classList.toggle('on',k===i)});sl.forEach(function(e,k){e.classList.toggle('cur',k===i)})}},{passive:true});
  ['touchstart','pointerdown'].forEach(function(ev){tr.addEventListener(ev,function(){hold=Date.now()},{passive:true})});
  if(!matchMedia('(prefers-reduced-motion: reduce)').matches)setInterval(function(){if(Date.now()-hold<9000||document.hidden)return;var r=tr.getBoundingClientRect();if(r.bottom<0||r.top>innerHeight)return;tr.scrollTo({left:((cur+1)%dots.length)*(sl[0]?sl[0].offsetWidth+10:tr.clientWidth),behavior:'smooth'})},5200);
}
/* 11/18 入口（表紙）：地図の下に「今週の1件」を画面いっぱいの写真で（ゆっくりズーム）。その下に今週ほかにも（横にめくる） */
function cover(){if(!/^\/(town-notes(\.html)?)?$/.test(location.pathname)||document.querySelector('.mhero'))return;var ms=document.querySelector('section.mapsec');if(!ms)return;
  news({q:ms,hero:function(o){var t=ymd(jst()),st=!o.s||o.s<=t?'開催中':(+o.s.slice(5,7))+'/'+(+o.s.slice(8))+'から',PC={"東京":"#4F86C6","神奈川":"#3FA3B5","埼玉":"#E09A3E","千葉":"#D9775A","茨城":"#5FA06A","栃木":"#D2697E","群馬":"#9C7BB8"};
    var w=document.createElement('section');w.className='mhero';w.setAttribute('aria-label','今週の1件');
    w.innerHTML='<a class="mhl" href="/o/'+o.id+'" data-mo="'+o.id+'" style="--pc:'+(PC[o.p]||'#B97A62')+'"><img class="mfade" src="/assets/ph/'+o.im+'" alt="'+esc(o.n)+'" decoding="async" fetchpriority="high">'+
      '<span class="mhtop"><b>THIS WEEK</b><i></i>今週の1件</span>'+
      '<span class="mhtx mrv"><span class="mhtg"><i>'+esc(o.p)+'</i>'+st+(o.e?'・'+(+o.e.slice(5,7))+'/'+(+o.e.slice(8))+'まで':'')+'</span>'+
      '<b class="mhh">'+esc(o.hk||o.n)+'</b>'+(o.hk?'<span class="mhn">'+esc(o.n)+'</span>':'')+'<em>くわしく見る<span>→</span></em></span>'+
      '<small class="mhcr">写真：'+esc(o.cr.replace(/（.*$/,''))+'</small></a>';
    var an=ms.closest('header.head')||ms;an.parentNode.insertBefore(w,an.nextSibling);return w}})}
/* 今週の1件の文字が、見えた時にふわっと出る（ほかの段の浮かび上がり・数字の数え上がりは tech.js が全員にしている） */
var RM=matchMedia('(prefers-reduced-motion: reduce)').matches,RIO=null;
function reveal(){if(RM||!('IntersectionObserver' in window))return;if(!/^\/(town-notes(\.html)?)?$/.test(location.pathname))return;
  if(!RIO)RIO=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('mrvin');RIO.unobserve(e.target)}})},{rootMargin:'0px 0px -8% 0px'});
  document.querySelectorAll('.mrv:not(.mrvo)').forEach(function(e){e.classList.add('mrvo');RIO.observe(e)})}
/* 11/18 不動産のご相談：申し込みの段を「押すボタン」に見えるように（cta.gallery 風）。順番・文はそのまま */
function cta(){if(!/^\/fudosan(\.html)?$/.test(location.pathname))return;var a=document.querySelector('.sns a.co[href$="moushikomi"]:not(.mcta1)');if(!a)return;a.classList.add('mcta1');
  a.insertAdjacentHTML('beforeend','<em class="mctab"><span><b>無料</b>でお申し込み</span><small>約1分</small><i>→</i></em>')}
/* カードを押すと、そのおでかけの1件ページ（写真・説明・公式ボタン）へ。☆・地図・近くの宿は今のまま */
function go(id,img){try{var o=ID[id];if(o&&o.im)sessionStorage.setItem('tn_mph',JSON.stringify({id:id,im:o.im}));else sessionStorage.removeItem('tn_mph')}catch(x){}
  if(img&&document.startViewTransition!==undefined||img&&'onpagereveal' in window){document.querySelectorAll('[style*="view-transition-name"]').forEach(function(x){if(x!==img)x.style.viewTransitionName=''});img.style.viewTransitionName='mph'}
  location.href='/o/'+id}
document.addEventListener('click',function(e){if(e.defaultPrevented||e.metaKey||e.ctrlKey||e.shiftKey)return;var t=e.target.closest&&e.target.closest('a[data-mo],a.mnsl,a.m1');if(!t)return;
  if(e.target.closest('.wfav,button'))return;var id=t.dataset.mo||(t.getAttribute('href')||'').replace(/^\/o\//,'');if(!/^[0-9a-f]{8}$/.test(id))return;
  e.preventDefault();go(id,t.querySelector('.mbp img,.ib.mph img,.ti.mph img,img'))},true);
/* 押す前に次のページを用意しておく（指を置いた時・マウスを乗せた時）→ 押した瞬間に開く */
try{if(HTMLScriptElement.supports&&HTMLScriptElement.supports('speculationrules')){var sr=document.createElement('script');sr.type='speculationrules';sr.textContent=JSON.stringify({prerender:[{where:{href_matches:'/o/*'},eagerness:'moderate'}],prefetch:[{where:{and:[{href_matches:'/*'},{not:{href_matches:'/c'}}]},eagerness:'conservative'}]});document.head.appendChild(sr)}}catch(x){}
var warm={};document.addEventListener('pointerdown',function(e){var t=e.target.closest&&e.target.closest('a[data-mo]');if(!t||warm[t.dataset.mo])return;warm[t.dataset.mo]=1;var l=document.createElement('link');l.rel='prefetch';l.href='/o/'+t.dataset.mo;document.head.appendChild(l)},{passive:true});
/* 1件ページ */
function detail(){var m=location.pathname.match(/^\/o\/([0-9a-f]{8})/);if(!m||document.body.dataset.mhd)return;var o=ID[m[1]];if(!o)return;document.body.dataset.mhd=1;
  var hd=document.querySelector('.head');
  if(hd){var h=hook(o);if(h){var p=document.createElement('p');p.className='mhk-o';p.textContent=h;var sub=hd.querySelector('.sub');hd.insertBefore(p,sub||null)}}
  var cap='<figcaption>'+(o.vn&&o.n.indexOf(o.vn)<0?(o.vk?'場所（':'会場（')+esc(o.vn)+'）の':'')+'写真：'+(o.cu?'<a href="'+esc(o.cu)+'" target="_blank" rel="noopener">'+esc(o.cr)+'</a>':esc(o.cr))+'</figcaption>';
  var ex=document.querySelector('.mph-o');if(ex){ex.querySelector('img').alt=o.n;ex.insertAdjacentHTML('beforeend',cap)}
  else if(o.im&&hd){var f=document.createElement('figure');f.className='mph-o';f.innerHTML='<img src="/assets/ph/'+o.im+'" alt="'+esc(o.n)+'" decoding="async" fetchpriority="high" class="mfade">'+cap;hd.parentNode.insertBefore(f,hd.nextSibling)}
  document.querySelectorAll('.big>div').forEach(function(b){var sp=b.querySelector('span');if(sp&&sp.textContent.trim()==='いまは'){var w=document.createElement('div');w.className='mnowl';b.appendChild(w);nowPill(w,o);setInterval(function(){nowPill(w,o)},60000)}});
  var ld=document.querySelector('.lead');
  if(o.ds&&ld){var x=document.createElement('div');x.className='mds';x.innerHTML='<span>どんな催し？</span><p>'+esc(o.ds)+'</p>';ld.parentNode.insertBefore(x,ld.nextSibling);ld.style.display='none'}
  if((o.ig&&o.ig.length)||o.ia){var at=document.querySelector('.act')||ld;if(at){var g=document.createElement('div');g.className='mig';
    if(o.ig&&o.ig.length){var pl='https://www.instagram.com/'+o.ig[0]+'/';g.innerHTML='<span>主催者のインスタから</span><blockquote class="instagram-media" data-instgrm-permalink="'+pl+'?utm_source=ig_embed" data-instgrm-version="14"><a href="'+pl+'" target="_blank" rel="noopener">インスタで見る</a></blockquote>';
      var lj=function(){if(window.instgrm){window.instgrm.Embeds.process();return}if(document.getElementById('migjs'))return;var sc=document.createElement('script');sc.id='migjs';sc.async=1;sc.src='https://www.instagram.com/embed.js';document.body.appendChild(sc)};
      if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){if(es[0].isIntersecting){io.disconnect();lj()}},{rootMargin:'600px'});io.observe(g)}else lj()}
    else{g.innerHTML='<a class="migl" href="https://www.instagram.com/'+esc(o.ia)+'/" target="_blank" rel="noopener"><i></i>主催者のインスタで写真を見る</a>'}
    at.parentNode.insertBefore(g,at.nextSibling)}}
  var ac=document.querySelector('.act');if(ac){
    var fav=[];try{fav=JSON.parse(localStorage.getItem('tn_fav')||'[]')||[]}catch(e){}
    var on=fav.indexOf(o.u)>=0,cal=!/^\d{4}-\d\d-\d\d$/.test(o.s||'')?'':'https://calendar.google.com/calendar/render?action=TEMPLATE&text='+encodeURIComponent(o.n)+'&dates='+o.s.replace(/-/g,'')+'/'+(function(){var d=new Date((/^\d{4}-\d\d-\d\d$/.test(o.e||'')?o.e:o.s)+'T00:00:00Z');d.setUTCDate(d.getUTCDate()+1);return ymd(d).replace(/-/g,'')})()+'&details='+encodeURIComponent('公式：'+o.u+'\n'+location.href)+'&location='+encodeURIComponent((document.querySelector('.sub')||{}).textContent||'');
    var w=document.createElement('div');w.innerHTML='<a class="g mfav" href="#" role="button" aria-pressed="'+on+'">'+(on?'★ 行きたいに入っています':'☆ 行きたいに入れる')+'</a>'+(cal?'<a class="g" href="'+cal+'" target="_blank" rel="noopener">カレンダーに入れる</a>':'')+'<a class="g mshare" href="#" role="button">この催しを送る</a><div class="mshr"><a href="https://line.me/R/share?text='+encodeURIComponent(o.n+' '+location.href)+'" target="_blank" rel="noopener">LINE</a><a href="https://x.com/intent/post?text='+encodeURIComponent(o.n)+'&url='+encodeURIComponent(location.href)+'" target="_blank" rel="noopener">X</a><a href="#" class="mcp">URLをコピー</a></div>';
    var first=ac.querySelector('a.o');var ref=first?first.nextSibling:ac.firstChild;while(w.firstChild)ac.insertBefore(w.firstChild,ref);
    ac.addEventListener('click',function(e){var b=e.target.closest('a');if(!b)return;
      if(b.classList.contains('mfav')){e.preventDefault();var f=[];try{f=JSON.parse(localStorage.getItem('tn_fav')||'[]')||[]}catch(x){}var i=f.indexOf(o.u);if(i>=0)f.splice(i,1);else f.push(o.u);try{localStorage.setItem('tn_fav',JSON.stringify(f))}catch(x){}var y=i<0;b.setAttribute('aria-pressed',y);b.textContent=y?'★ 行きたいに入っています':'☆ 行きたいに入れる'}
      else if(b.classList.contains('mshare')){e.preventDefault();if(navigator.share){navigator.share({title:o.n,url:location.href}).catch(function(){})}else ac.querySelector('.mshr').classList.toggle('open')}
      else if(b.classList.contains('mcp')){e.preventDefault();try{navigator.clipboard.writeText(location.href).then(function(){b.textContent='コピーしました'})}catch(x){}}});
  }
}
function fin(i){if(i.classList.contains('in'))return;i.classList.add('in');var p=i.parentElement;if(p)p.classList.add('ld')}
function fade(){document.querySelectorAll('img.mfade:not(.in)').forEach(function(i){if(i.complete&&i.naturalWidth)fin(i)})}
/* 写真が読めたら出す（カードが作り直されて写真が写し替えられても拾えるよう、ページ全体で受ける） */
document.addEventListener('load',function(e){var i=e.target;if(i&&i.tagName==='IMG'&&i.classList.contains('mfade'))fin(i)},true);
document.addEventListener('error',function(e){var i=e.target;if(i&&i.tagName==='IMG'&&i.classList.contains('mfade'))fin(i)},true);
setInterval(fade,700);
/* 11/18 超ハイテク（見本）：①立体の地図（傾き・府県がばねで立ち上がる・今週の写真のピン）②今週の1件をスクロールで（GSAP ScrollTrigger）③カードのばね */
var SPR='linear(0,0.009,0.035 2.1%,0.141 4.4%,0.723 12.9%,0.938 16.7%,1.017 19.4%,1.067,1.099 24.3%,1.108 26%,1.1,1.077 30.6%,1.017 35.6%,0.991 38.3%,0.977 40.9%,0.98 46%,0.999 55.4%,1.003 61.7%,1)';
function hitech(){if(window.__ht)return;var svg=document.querySelector('svg.kmap');if(!svg||!/^\/(town-notes(\.html)?|index(\.html)?)?$/.test(location.pathname))return;window.__ht=1;
  var st=document.createElement('style');st.textContent=
   '.mapsec .nofilt{perspective:1000px;perspective-origin:50% 0}'+
   'svg.kmap.m3{transform-origin:50% 62%;transform:rotateX(var(--rx,22deg)) rotateY(var(--ry,0deg)) rotateZ(var(--rz,-2deg));}'+
   'svg.kmap.m3 .pf path{transform-box:fill-box;transform-origin:50% 100%}'+
   'svg.kmap .mb{cursor:pointer}svg.kmap .mb>g{transform-box:fill-box;transform-origin:50% 100%}'+
   'svg.kmap .mex path{fill:rgba(70,48,28,.26)!important;stroke:none!important;pointer-events:none}html.night svg.kmap .mex path{fill:rgba(0,0,0,.5)!important}'+'.mapsec{position:relative}.mtip{position:absolute;z-index:5;transform:translate(-50%,-100%);background:#fff;color:#2B2622;border-radius:14px;padding:10px 12px 10px 14px;box-shadow:0 14px 30px -10px rgba(40,25,10,.35);display:flex;align-items:center;gap:10px;max-width:250px;text-decoration:none;font:700 13px/1.4 "Zen Kaku Gothic New",sans-serif;opacity:0;scale:.9;transition:opacity .18s,scale .45s '+SPR+'}.mtip.on{opacity:1;scale:1}.mtip small{display:block;font-weight:500;font-size:11px;color:#6E655E;margin-top:2px}.mtip i{font-style:normal;flex:none;width:28px;height:28px;border-radius:50%;background:#2B2622;color:#fff;display:grid;place-items:center;font-size:14px}.mtip.dn{transform:translate(-50%,0)}.mtip.dn:after{bottom:auto;top:-6px}.mtip:after{content:"";position:absolute;left:50%;bottom:-6px;width:12px;height:12px;background:#fff;transform:translateX(-50%) rotate(45deg)}'+
   'svg.kmap .mb circle.r{fill:#fff}svg.kmap .mb .sh{fill:rgba(60,40,20,.22)}'+
   '@media (prefers-reduced-motion:reduce){svg.kmap.m3{transform:rotateX(14deg)}}'+
   'a.card,.mnews .mnsl,.pr5 .m1,a.fc,.mhl{transition:transform .55s '+SPR+'}a.card:active,.mnews .mnsl:active,.pr5 .m1:active,a.fc:active{transform:scale(.965);transition:transform .12s ease-out}';
  document.head.appendChild(st);svg.classList.add('m3');
  var RMq=matchMedia('(prefers-reduced-motion: reduce)').matches;
  // 府県がばねで立ち上がる
  var pf=svg.querySelector('.pf');if(pf&&!svg.querySelector('.mex')){var ex=pf.cloneNode(true);ex.setAttribute('class','mex');ex.removeAttribute('stroke');ex.setAttribute('transform','translate(0,7)');ex.querySelectorAll('path').forEach(function(q){q.removeAttribute('data-p')});pf.parentNode.insertBefore(ex,pf)}
  var ps=svg.querySelectorAll('.pf path');if(!RMq)ps.forEach(function(p,i){p.animate([{transform:'translateY(-46px) scale(.96)',opacity:0},{transform:'none',opacity:1}],{duration:900,delay:120+i*70,easing:SPR,fill:'backwards'})});
  // 今週の写真のピン（府県ごとに1つ・押すと1件ページ）
  var NS='http://www.w3.org/2000/svg',t=ymd(jst()),t7=ymd(new Date(jst().getTime()+6*864e5)),best={};
  for(var k in D){var o=D[k];if(!o.im||!o.id||!o.p)continue;var on=(!o.s||o.s<=t)&&(!o.e||o.e>=t),soon=o.s&&o.s>t&&o.s<=t7;if(!on&&!soon)continue;var sc=(on?2:1)+(o.hk?1:0)+(o.wk?-2:0);if(!best[o.p]||sc>best[o.p].sc)best[o.p]={o:o,sc:sc}}
  var LB={};svg.querySelectorAll('.lb>g').forEach(function(g){var m=/translate\(([\d.]+),([\d.]+)\)/.exec(g.getAttribute('transform')||''),j=g.querySelector('.jp');if(m&&j)LB[j.textContent.trim()]=[+m[1],+m[2]]});
  var defs=svg.querySelector('defs')||svg.insertBefore(document.createElementNS(NS,'defs'),svg.firstChild),lay=document.createElementNS(NS,'g');lay.setAttribute('class','mbs');svg.appendChild(lay);var n=0;
  Object.keys(best).forEach(function(P){var o=best[P].o,xy=LB[P];if(!xy)return;var id='mbc'+(n++),OF={'東京':[84,52],'神奈川':[-88,46]}[P]||[0,0],x=xy[0]+OF[0],y=xy[1]-84+OF[1],R=42;
    var cp=document.createElementNS(NS,'clipPath');cp.id=id;cp.innerHTML='<circle cx="'+x+'" cy="'+y+'" r="'+(R-3.5)+'"/>';defs.appendChild(cp);
    var g=document.createElementNS(NS,'g');g.setAttribute('class','mb');g.setAttribute('role','link');g.setAttribute('tabindex','0');g.setAttribute('aria-label',P+'：'+o.n);
    g.innerHTML='<ellipse class="sh" cx="'+x+'" cy="'+(y+R+26)+'" rx="13" ry="4"/><g><path d="M'+(x-9)+','+(y+R-6)+' L'+x+','+(y+R+12)+' L'+(x+9)+','+(y+R-6)+'Z" fill="#fff"/><circle class="r" cx="'+x+'" cy="'+y+'" r="'+R+'"/><image href="/assets/ph/t/'+o.im+'" x="'+(x-R)+'" y="'+(y-R)+'" width="'+(2*R)+'" height="'+(2*R)+'" preserveAspectRatio="xMidYMid slice" clip-path="url(#'+id+')"/></g>';
    var go=function(e){e.stopPropagation();e.preventDefault();var sec=svg.closest('.mapsec')||svg.parentNode,tip=sec.querySelector('.mtip');if(tip&&tip.dataset.id===o.id&&tip.classList.contains('on')){location.href='/o/'+o.id;return}
      if(!tip){tip=document.createElement('a');tip.className='mtip';sec.appendChild(tip);document.addEventListener('click',function(ev){if(!ev.target.closest('.mtip,.mb'))tip.classList.remove('on')})}
      var rb=g.querySelector('circle.r').getBoundingClientRect(),rs=sec.getBoundingClientRect(),en=o.e?(+o.e.slice(5,7))+'/'+(+o.e.slice(8))+'まで':'';tip.href='/o/'+o.id;tip.dataset.id=o.id;
      tip.innerHTML='<span>'+esc(o.n)+'<small>'+esc(P)+(en?'・'+en:'')+'</small></span><i>→</i>';tip.style.left=Math.max(130,Math.min(rs.width-130,rb.left+rb.width/2-rs.left))+'px';var up=rb.top>110;tip.classList.toggle('dn',!up);tip.style.top=(up?rb.top-rs.top-8:rb.bottom-rs.top+12)+'px';tip.classList.remove('on');void tip.offsetWidth;tip.classList.add('on')};g.addEventListener('click',go);g.addEventListener('keydown',function(e){if(e.key==='Enter')go(e)});
    lay.appendChild(g);var inner=g.lastChild;
    if(!RMq){inner.animate([{transform:'translateY(-30px) scale(0)'},{transform:'none'}],{duration:1000,delay:700+n*110,easing:SPR,fill:'backwards'});
}});
  // 傾き：指・マウスにだけ、ばねでついてくる（11/18 iPhoneで落ちた：ずっと動かす・影の重ね掛けをやめた）
  if(!RMq&&matchMedia('(hover:hover)').matches){var tx=0,ty=0,cx=0,cy=0,vx=0,vy=0,run=0,box=svg.closest('.mapsec')||svg;
    function tick(){vx+=(tx-cx)*.06;vy+=(ty-cy)*.06;vx*=.82;vy*=.82;cx+=vx;cy+=vy;svg.style.setProperty('--ry',(cx*6).toFixed(2)+'deg');svg.style.setProperty('--rx',(22-cy*5).toFixed(2)+'deg');
      if(Math.abs(tx-cx)+Math.abs(ty-cy)+Math.abs(vx)+Math.abs(vy)>.002)requestAnimationFrame(tick);else run=0}
    function kick(){if(!run){run=1;requestAnimationFrame(tick)}}
    box.addEventListener('pointermove',function(e){var r=svg.getBoundingClientRect();tx=((e.clientX-r.left)/r.width-.5)*2;ty=((e.clientY-r.top)/r.height-.5)*2;kick()});
    box.addEventListener('pointerleave',function(){tx=ty=0;kick()})}
  gsapHero();}
/* 今週の1件：スクロールで写真が奥へ・見出しが1文字ずつ（GSAP 3.13 の ScrollTrigger と SplitText。上の段だけで読む） */
function gsapHero(){var h=document.querySelector('.mhero');if(!h){setTimeout(gsapHero,400);return}if(matchMedia('(prefers-reduced-motion: reduce)').matches||h.dataset.g)return;h.dataset.g=1;
  if('IntersectionObserver' in window&&!h.dataset.seen){var io=new IntersectionObserver(function(es){if(es[0].isIntersecting){io.disconnect();h.dataset.seen=1;h.dataset.g='';gsapHero()}},{rootMargin:'400px 0px'});io.observe(h);return}
  var base='/assets/vendor/gsap/',L=function(f){return new Promise(function(ok,ng){var s=document.createElement('script');s.src=base+f;s.onload=ok;s.onerror=ng;document.head.appendChild(s)})};
  L('gsap.min.js').then(function(){return Promise.all([L('ScrollTrigger.min.js'),L('SplitText.min.js')])}).then(function(){var g=window.gsap;g.registerPlugin(ScrollTrigger,SplitText);
    var img=h.querySelector('img'),hh=h.querySelector('.mhh');
    g.fromTo(img,{scale:1.18,yPercent:-4},{scale:1,yPercent:6,ease:'none',scrollTrigger:{trigger:h,start:'top bottom',end:'bottom top',scrub:true}});
    if(hh){var sp=new SplitText(hh,{type:'chars',charsClass:'mch'});g.from(sp.chars,{yPercent:110,opacity:0,rotate:6,duration:.9,ease:'back.out(1.6)',stagger:.035,onComplete:function(){sp.revert()},scrollTrigger:{trigger:h,start:'top 75%'}})}
  }).catch(function(){})}
/* 11/18 全ページ点検（axe・小さい字・はみ出し）で出た物を見本で直す。月と燈の両方 */
function a11y(){
  if(!document.getElementById('mh-a11y')){var s=document.createElement('style');s.id='mh-a11y';s.textContent=
  '.inn li a{grid-template-columns:minmax(0,1fr) auto!important}.hn{overflow-wrap:anywhere}'+
  '.ib .lb{font-size:10px!important;letter-spacing:.1em!important}.ddw{font-size:11px!important}'+
  '.mbp small,.mncr,.mhcr,.kph small,figure small{font-size:10px!important}'+
  '.ot small,.nen,.ls .en,.head .en,.wrap>.ft,.kicker,.foot .sign,.adn{font-size:11px!important}'+
  'button>i,b>u,button>small,.tkclk i{font-size:10px!important}';
  document.head.appendChild(s)}
  var lens=document.getElementById('lens');
  if(lens){lens.querySelectorAll('button').forEach(function(b){b.setAttribute('role','tab');b.setAttribute('aria-selected',b.classList.contains('on')||b.getAttribute('aria-pressed')==='true'?'true':'false')})}
  document.querySelectorAll('svg.kmap[role=img]').forEach(function(s){s.setAttribute('role','group')});
  cfix();setTimeout(cfix,1800)
}
/* 字と後ろの色の差が足りない所（4.5:1 未満・大きい字は 3:1）だけ、同じ色みのまま濃くする */
var CF=new WeakSet();function cfix(){
  var root=document.documentElement,night=root.classList.contains('night');
  function rgb(s){if(!s)return null;var cl=s.indexOf('color(')===0;if(cl&&s.indexOf('srgb')<0)return null;var m=s.replace(/^color\(srgb/,'').match(/[\d.e-]+/g);if(!m)return null;m=m.map(Number);if(cl)for(var i=0;i<3;i++)m[i]*=255;if(m.length<4)m[3]=1;return m}
  function L(c){var k=[.2126,.7152,.0722],t=0;for(var i=0;i<3;i++){var v=c[i]/255;t+=k[i]*(v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4))}return t}
  function R(a,b){var x=L(a),y=L(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
  var bodyBg=night?[255,255,255,1]:(function(){var c=rgb(getComputedStyle(document.body).backgroundColor);return c&&c[3]>.5?c:[255,255,255,1]})();
  var BE=null;function bg(e){BE=null;for(;e&&e!==document.body&&e!==root;e=e.parentElement){var cs=getComputedStyle(e);if(cs.backgroundImage!=='none')return null;var c=rgb(cs.backgroundColor);if(c&&c[3]>.85){BE=e;return c}}return bodyBg}
  var w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT,null),seen=CF,n,cnt=0;
  while((n=w.nextNode())&&cnt<4000){var e=n.parentElement;if(!e||seen.has(e)||!n.nodeValue.trim())continue;seen.add(e);cnt++;
    if(e.closest('svg,.nofilt,script,style'))continue;
    var cs=getComputedStyle(e);if(cs.visibility==='hidden'||cs.display==='none')continue;
    var c=rgb(cs.color),b=bg(e);if(!c||!b)continue;
    if(c[3]<1)c=[0,1,2].map(function(i){return c[i]*c[3]+b[i]*(1-c[3])}).concat(1);
    var fs=parseFloat(cs.fontSize),big=fs>=24||(fs>=18.66&&+cs.fontWeight>=700),need=big?3.1:4.6;
    if(R(c,b)>=need)continue;
    var x=null;[[34,26,22],[255,255,255]].some(function(to){for(var k=1;k<=20;k++){var y=[0,1,2].map(function(i){return c[i]+(to[i]-c[i])*k/20});if(R(y,b)>=need){x=y;return true}}});
    if(!x){if(BE&&!BE.dataset.cf){BE.dataset.cf=1;var d=b.slice(0,3);for(var k=1;k<=12&&R(c,d)<need;k++)d=b.slice(0,3).map(function(v){return v*(1-k*.05)});BE.style.setProperty('background-color','rgb('+d.map(Math.round).join(',')+')','important')}continue}
    e.style.setProperty('color','rgb('+x.map(Math.round).join(',')+')','important')}
}
var q;function run(){clearTimeout(q);q=setTimeout(function(){if(!READY)return;cards();document.querySelectorAll('figure.mph-k[hidden]').forEach(function(f){f.hidden=false});fade();try{cfix()}catch(e){}},80)}
fetch('/assets/mihon.json?v='+(window.__mhv||3)).then(function(r){return r.json()}).then(function(j){D={};for(var x in j){D[x]=j[x];if(j[x].id)ID[j[x].id]=j[x]}READY=1;run();
  try{new MutationObserver(run).observe(document.body,{childList:true,subtree:true})}catch(e){}
  setInterval(function(){document.querySelectorAll(':is(.card,a.cd) .v2c').forEach(function(r){var a=r.closest(':is(.card,a.cd)'),t=a&&a.querySelector('.t');if(t)nowPill(r,find(t.textContent))})},60000)}).catch(function(){});
})();
