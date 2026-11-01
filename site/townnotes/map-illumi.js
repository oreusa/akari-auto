/* TOWN NOTE（仮）: おでかけリストに、押すだけで寄っていく地図を組み込む（関西 → 府県 → 市・区）。
   指2本の操作はなし。府県・市区町村の形は links/townnotes/kansai.json（国土数値情報を加工）、場所は geo.json。
   今のページ（タブ・府県ボタン・カード）をそのまま読み、選んでいるタブのカードだけをピンにする。 */
// 地図のファイルは map.js と同じ場所から読む（どのページ・どの置き場所から使っても同じに動く）
(function(){
var TNB=(document.currentScript&&document.currentScript.src||"").replace(/[?#].*$/,"").replace(/[^/]*$/,"");
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return [].slice.call((r||document).querySelectorAll(s))};
var NS="http://www.w3.org/2000/svg";
var key=function(s){return String(s||"").replace(/\s+/g,"")};
var RM=matchMedia("(prefers-reduced-motion: reduce)").matches;
// ---- 地域の設定（関西・関東など。build.py が tools/townnotes/region-*.json から入れる） ----
var R={
name:"関東",en_all:"KANTO",unit:"都県",shapes:"kanto.json",
proj:[138,80.9,37.4],
prefs:["群馬","栃木","茨城","埼玉","千葉","東京","神奈川"],
pc:{"東京":"#4F86C6","神奈川":"#3FA3B5","埼玉":"#E09A3E","千葉":"#D9775A","茨城":"#5FA06A","栃木":"#D2697E","群馬":"#9C7BB8"},
fill:{"東京":"#CADBEE","神奈川":"#C5E3E9","埼玉":"#F6E1C5","千葉":"#F4D6CE","茨城":"#CFE2D2","栃木":"#F2D2D8","群馬":"#E1D7EA"},
deep:{"東京":"#A3C0E1","神奈川":"#9BCFD9","埼玉":"#EFCA9B","千葉":"#EBB8A9","茨城":"#ACCEB2","栃木":"#E8B1BC","群馬":"#CCBADA"},
en:{"東京":"TOKYO","神奈川":"KANAGAWA","埼玉":"SAITAMA","千葉":"CHIBA","茨城":"IBARAKI","栃木":"TOCHIGI","群馬":"GUNMA"},
lp:{"東京":[139.45,35.7],"神奈川":[139.3,35.42],"埼玉":[139.35,36.0],"千葉":[140.2,35.5],"茨城":[140.25,36.3],"栃木":[139.8,36.65],"群馬":[138.95,36.5]},
light:{"東京":"#E8EFF8","神奈川":"#E6F3F5","埼玉":"#FBF2E6","千葉":"#FAEDEA","茨城":"#EAF3EC","栃木":"#F9ECEE","群馬":"#F2EEF6"},
mini:{"茨城":"M230.2 166.0L215.0 140.7L207.2 110.8L226.4 54.6L207.6 48.4L199.3 60.8L182.5 47.0L185.4 68.7L182.4 87.8L167.0 101.8L136.5 119.8L144.0 131.7L156.9 145.9L174.5 155.7L203.1 144.1L230.2 166.0Z","栃木":"M112.8 49.7L107.6 77.2L120.0 82.2L110.1 101.6L135.5 119.2L136.5 119.8L167.0 101.8L182.4 87.8L185.4 68.7L182.5 47.0L172.9 29.3L153.3 24.7L112.8 49.7Z","群馬":"M58.0 140.7L85.8 124.8L91.4 111.7L117.6 120.9L135.5 119.2L110.1 101.6L120.0 82.2L107.6 77.2L112.8 49.7L88.3 38.0L66.2 63.8L44.0 69.6L32.4 96.6L52.4 99.2L52.1 135.0L58.0 140.7Z","埼玉":"M135.5 119.2L117.6 120.9L91.4 111.7L85.8 124.8L58.0 140.7L76.4 154.5L82.8 150.3L123.7 160.6L153.1 161.7L144.0 131.7L136.5 119.8L135.5 119.2Z","千葉":"M151.4 176.1L171.2 183.1L146.6 209.4L147.6 248.9L172.6 227.8L188.1 226.0L193.9 198.1L201.9 182.4L230.2 166.0L203.1 144.1L174.5 155.7L156.9 145.9L144.0 131.7L153.1 161.7L151.4 176.1Z","東京":"M141.3 185.6L151.4 176.1L153.1 161.7L123.7 160.6L82.8 150.3L76.4 154.5L92.8 173.3L93.4 173.4L116.9 185.9L123.4 175.7L141.3 185.6Z","神奈川":"M92.8 173.3L81.1 200.1L83.3 225.0L107.6 208.8L134.4 207.2L132.4 194.5L141.3 185.6L123.4 175.7L116.9 185.9L93.4 173.4L92.8 173.3Z"},
icons:{
 "東京":{at:[139.03,35.8],n:"東京タワー",s:'<path d="M20 3v5"/><path d="M18.5 8h3l5.5 27h-4l-3-8-3 8h-4z" fill="#EFA48C"/><path d="M15.5 16h9v3h-9z" fill="#fff"/><path d="M14.5 25h11"/><path d="M11 35h18"/>'},
 "神奈川":{at:[139.72,35.37],n:"観覧車",s:'<circle cx="20" cy="17" r="12" fill="#fff"/><path d="M20 5v24M8 17h24M11.5 8.5l17 17M28.5 8.5l-17 17"/><circle cx="20" cy="17" r="2.6" fill="#F2C9B8"/><circle cx="20" cy="5" r="1.6" fill="#F2C9B8"/><circle cx="32" cy="17" r="1.6" fill="#BFD7F2"/><circle cx="8" cy="17" r="1.6" fill="#F4DC9A"/><path d="M16 29l-3 6M24 29l3 6M10 35h20"/>'},
 "埼玉":{at:[138.86,35.98],n:"時の鐘",s:'<path d="M12 10h16l-8-6z" fill="#B9CFA8"/><path d="M15.5 10h9v5h-9z" fill="#fff"/><circle cx="20" cy="12.5" r="1.6" fill="#E7B84B"/><path d="M12 17h16l-3-2H15z" fill="#B9CFA8"/><path d="M16.5 17v18M23.5 17v18M16.5 23h7M16.5 29h7"/><path d="M12 35h16"/>'},
 "千葉":{at:[140.24,35.24],n:"落花生",s:'<path d="M20 4c-5.5 0-7.5 4-6.5 8.5.6 2.6.6 4.4-.6 6.8C10.6 24.6 13 34 20 34s9.4-9.4 7.1-14.7c-1.2-2.4-1.2-4.2-.6-6.8C27.5 8 25.5 4 20 4z" fill="#EBD6AE"/><path d="M17 9.5l1.2 1M22.5 9l1.2 1M16.5 15l1.2 1M23.5 14.5l-1.2 1M15.5 24l1.2 1M23.5 23.5l1.2 1M19.5 29l1.2 1"/>'},
 "茨城":{at:[140.52,36.58],n:"ネモフィラ",s:'<path d="M20 26v10M20 31c-3-1-5-3-6-5M20 33c3-1 5-3 6-5"/><path d="M20 4c3 0 4.5 3 3.5 6.2 3-1.5 6.2 0 6.5 2.8.3 2.9-2.4 4.7-5.4 4.5 2.2 2.3 2 5.6-.4 6.8-2.6 1.3-5-.5-5.2-3.4-.2 2.9-2.6 4.7-5.2 3.4-2.4-1.2-2.6-4.5-.4-6.8-3 .2-5.7-1.6-5.4-4.5.3-2.8 3.5-4.3 6.5-2.8C15.5 7 17 4 20 4z" fill="#C4DBF3"/><circle cx="20" cy="14.5" r="2.6" fill="#fff"/>'},
 "栃木":{at:[139.62,36.98],n:"いちご",s:'<path d="M20 12c-7 0-11 3-11 8 0 7 6 14 11 15 5-1 11-8 11-15 0-5-4-8-11-8z" fill="#F4ADA5"/><path d="M13.5 12.5l3-4.5 3.5 3 3.5-3 3 4.5" fill="#B9D7A6"/><path d="M20 8V4"/><g fill="#fff" stroke="none"><circle cx="15" cy="19" r="1"/><circle cx="20" cy="17.5" r="1"/><circle cx="25" cy="19" r="1"/><circle cx="17" cy="25" r="1"/><circle cx="23" cy="25" r="1"/><circle cx="20" cy="30" r="1"/></g>'},
 "群馬":{at:[139.05,36.8],n:"温泉",s:'<path d="M7 26c0 6 6 9 13 9s13-3 13-9z" fill="#fff"/><path d="M7 26c3.5-2 7 1.5 13 0s9.5-2 13 0" fill="#CFE3F0"/><path d="M14 22c-2.2-3 2.2-5 0-8s2.2-5 0-8M20 22c-2.2-3 2.2-5 0-8s2.2-5 0-8M26 22c-2.2-3 2.2-5 0-8s2.2-5 0-8"/>'}
}
};
var PREFS=R.prefs,PC=R.pc,FILL=R.fill,DEEP=R.deep,EN=R.en;
// 経度・緯度 → 地図の座標（その地域で形がゆがまないよう、経度に cos(緯度) をかける）
function P(lon,lat){return [(lon-R.proj[0])*R.proj[1],(R.proj[2]-lat)*100]}

// ---- 見た目 ----
var css=`
.tn{margin:0 0 18px}
.tn.shut{display:none}
.tnbtn{display:flex;align-items:center;justify-content:flex-start;gap:12px;width:100%;height:68px;margin:0 0 16px;padding:0 14px 0 8px;text-align:left;background:#fff;border:1px solid #DADADA;border-radius:14px;font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:14px;letter-spacing:.08em;color:#3A2F28;cursor:pointer;touch-action:manipulation;-webkit-tap-highlight-color:transparent;box-shadow:0 1px 0 rgba(43,38,34,.04)}
.tnbtn .mm{flex:none;width:56px;height:56px;border-radius:10px;background:#EEF6F9;display:flex;align-items:center;justify-content:center;overflow:hidden}
.tnbtn .mm svg{width:46px;height:46px;display:block}
.tnbtn .tx{flex:1;min-width:0;display:flex;flex-direction:column;gap:3px}
.tnbtn .t1{font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:15px;letter-spacing:.08em;color:#2B2622}
.tnbtn .t2{font-family:"Zen Kaku Gothic New",sans-serif;font-weight:500;font-size:11.5px;letter-spacing:.02em;color:#8C7B6E;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tnbtn .ar{flex:none;width:30px;height:30px;border-radius:50%;background:#B5532F;color:#fff;font-style:normal;font-family:Jost,sans-serif;font-size:18px;line-height:28px;text-align:center}
.tnbtn b{font-family:Jost,sans-serif;font-weight:500;font-size:15px;color:#B3AAA1;transition:transform .25s}
.tnbtn.on b{transform:rotate(180deg)}
.tnbtn.on{margin-bottom:10px}
.tn .chips{display:none;flex-wrap:wrap;gap:8px;margin:10px 0 2px}
.tn .chips.on{display:flex}
.tn .chips button{flex:1 1 calc(50% - 4px);display:flex;align-items:center;justify-content:space-between;gap:8px;min-height:46px;padding:0 14px;background:#fff;border:1px solid #DADADA;border-left:4px solid var(--c);font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:14px;letter-spacing:.04em;color:#3A2F28;cursor:pointer;touch-action:manipulation;-webkit-tap-highlight-color:transparent;text-align:left}
.tn .chips button b{font-family:Jost,sans-serif;font-weight:500;font-size:13px;color:#fff;background:var(--c);border-radius:10px;padding:1px 8px}
.tn .chips button.cur{background:var(--c);color:#fff}.tn .chips button.cur b{background:#fff;color:var(--c)}
.tn .chips button:active{transform:scale(.98)}
.tn .fr,.tn .fr *{-webkit-tap-highlight-color:transparent;-webkit-touch-callout:none}
.tn button,.tn .pop a,.tnbtn{touch-action:manipulation;-webkit-tap-highlight-color:transparent}
.tgrp{display:grid;grid-template-columns:1fr 1fr;gap:0 14px;margin:2px 0 6px}
.tgrp span{display:block;text-align:center;font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:11px;letter-spacing:.14em;color:#8C7B6E;padding:0 0 6px;border-bottom:1px solid #CECECE;position:relative}
.tgrp span:after{content:"";position:absolute;left:50%;bottom:-4px;width:7px;height:7px;background:#FFFFFF;border-right:1px solid #CECECE;border-bottom:1px solid #CECECE;transform:translateX(-50%) rotate(45deg)}
.tn-top{margin-top:-16px}.tn-top .flt{margin:0 0 10px;border-top:0;padding:8px 0;gap:0 13px;flex-wrap:nowrap}
.tn .n{position:absolute;left:18px;top:46px;z-index:5;pointer-events:none;font-family:"Zen Kaku Gothic New",sans-serif;font-size:10.5px;color:#8C7B6E;letter-spacing:.06em}
.tn .n b{font-family:Jost,sans-serif;font-weight:500;font-size:14px;color:#2B2622;margin:0 2px}
.tn .hd{display:flex;justify-content:space-between;align-items:flex-end;margin:2px 0 10px}
.tn .hd .e{font-family:Jost,sans-serif;font-size:9.5px;letter-spacing:.36em;color:#A07E66}
.tn .hd .j{display:block;font-family:"Shippori Mincho",serif;font-weight:600;font-size:15px;letter-spacing:.1em;color:#2B2622;margin-top:4px}
.tn .hd .n{font-family:"Zen Kaku Gothic New",sans-serif;font-size:11px;color:#8C7B6E;letter-spacing:.06em}
.tn .hd .n b{font-family:Jost,sans-serif;font-weight:500;font-size:16px;color:#2B2622;margin:0 2px}
.tn .fr{position:relative;aspect-ratio:1/.86;margin:0 -14px;background:#FFFFFF;overflow:hidden;user-select:none;-webkit-user-select:none}
.tn .fr:before{content:"";position:absolute;inset:8px;border:1px solid rgba(43,38,34,.28);pointer-events:none;z-index:3}
.tn .fr:after{content:"";position:absolute;inset:0;background:url(${TNB}grain.png);opacity:.05;pointer-events:none;z-index:4}
.tn svg.m{position:absolute;inset:0;width:100%;height:100%;display:block}
.tn .pf,.tn .mu,.tn .dot,.tn .sel-r{vector-effect:non-scaling-stroke}
.tn .pf{stroke:#FFFFFF;stroke-width:2px;stroke-linejoin:round;cursor:pointer;transition:fill .5s,opacity .5s}
.tn .mu{fill:transparent;stroke:#FFFFFF;stroke-width:1.1px;stroke-linejoin:round;cursor:pointer;transition:fill .4s,opacity .4s}
.tn .sh{fill:rgba(120,88,58,.16);transition:opacity .4s}
.tn .psh{fill:rgba(70,45,25,.22)}
.tn .pn{font-family:Jost,sans-serif;font-weight:600;fill:#fff;text-anchor:middle;dominant-baseline:central;pointer-events:none}
.tn .chips button.sp{flex:1 1 100%;justify-content:flex-start;font-family:"Shippori Mincho",serif;font-weight:600;font-size:14px;min-height:48px}
.tn .chips button.sp i{flex:none;font-style:normal;font-family:Jost,sans-serif;font-weight:600;font-size:12px;width:22px;height:22px;line-height:22px;text-align:center;border-radius:50%;background:var(--c);color:#fff}
.tn .chips button.sp span{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tn .chips button.sp:after{content:"›";font-family:Jost,sans-serif;font-size:18px;color:#B3AAA1}
.tn .lbs{position:absolute;inset:0;pointer-events:none;z-index:2}
.tn .lb{position:absolute;left:0;top:0;will-change:transform;white-space:nowrap;text-shadow:0 0 2px #FFFFFF,0 0 3px #FFFFFF,0 0 6px rgba(253,252,250,.9)}
.tn .lb.p{text-align:center;font-family:"Shippori Mincho",serif;font-weight:600;font-size:16px;letter-spacing:.16em;line-height:1.2}
.tn .lb.p small{display:block;font-family:Jost,sans-serif;font-weight:400;font-size:8.5px;letter-spacing:.32em;margin-top:3px}
.tn .lb.p.sm{font-size:14px;letter-spacing:.1em}.tn .lb.p.sm small{letter-spacing:.14em;margin-top:1px}
.tn .lb.m{pointer-events:auto;cursor:pointer;display:flex;align-items:center;gap:6px;padding:4px 5px 4px 10px;background:#fff;border-radius:99px;box-shadow:0 1px 2px rgba(60,40,20,.10),0 3px 10px rgba(60,40,20,.10);text-shadow:none;font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:11.5px;letter-spacing:.06em;color:#3A2F28}
.tn .ldr{position:absolute;left:0;top:0;height:1px;background:var(--c,#8A7B6E);opacity:.55;transform-origin:0 50%;pointer-events:none;display:none}
.tn .lb.m.cm{gap:3px;padding:2px 3px 2px 7px;font-size:9.5px;letter-spacing:0}.tn .lb.m.cm b{font-size:9px;line-height:14px;min-width:14px;padding:0 3px}
.tn .lb.m b{font-family:Jost,sans-serif;font-weight:500;font-size:10.5px;line-height:18px;min-width:18px;text-align:center;color:#fff;background:var(--c);border-radius:9px;padding:0 4px}
.tn .lb.w{font-family:"Zen Kaku Gothic New",sans-serif;font-weight:500;font-size:10px;letter-spacing:.06em;color:#A89C91}
.tn .lb.w.h{font-weight:700;font-size:11px;color:#4A3F37}
.tn .lb.t.fl{transform:translate(calc(-100% - 12px),-50%)}
.tn .lb.t{transform:translate(12px,-50%);font-family:"Shippori Mincho",serif;font-weight:600;font-size:12px;color:#2B2622}
.tn .lb.hide{visibility:hidden}
.tn .hit{fill:transparent;cursor:pointer}
.tn .sel-r{fill:none;opacity:.5}
.tn .qb{position:absolute;left:0;top:0;z-index:4;max-width:min(240px,70%);padding:7px 11px 8px;background:#fff;border:1px solid #D8D8D8;border-top:3px solid var(--c);border-radius:4px;box-shadow:0 4px 14px rgba(60,45,35,.16);pointer-events:none;opacity:0;transition:opacity .18s}
.tn .qb.on{opacity:1}
.tn .qb.ph{display:flex;align-items:center;gap:9px;max-width:min(270px,78%);padding-left:8px}
.tn .qth{flex:0 0 40px;height:40px;border-radius:4px;display:flex;align-items:center;justify-content:center}.tn .qth svg{width:26px;height:26px}
.tn .qx{min-width:0}
.tn .cc.ph{position:relative}.tn .cc.ph .cb>:not(.ac){padding-right:58px}
.tn .cth{position:absolute;top:12px;right:12px;width:48px;height:48px;border-radius:4px;display:flex;align-items:center;justify-content:center}.tn .cth svg{width:30px;height:30px}
.tn .qb:after{content:"";position:absolute;left:var(--ax);bottom:-6px;width:10px;height:10px;margin-left:-5px;background:#fff;border-right:1px solid #D8D8D8;border-bottom:1px solid #D8D8D8;transform:rotate(45deg)}
.tn .qb.dn:after{bottom:auto;top:-6px;transform:rotate(225deg);background:var(--c);border:0}
.tn .qb .qm{display:flex;flex-wrap:wrap;align-items:center;gap:2px 8px;font-size:10.5px;line-height:1.4;color:#7A6F66}
.tn .qb .qp{color:var(--c);font-weight:700}
.tn .qb .qf{padding:0 5px;border:1px solid currentColor;border-radius:2px;color:#4E8A5A;font-size:10px}
.tn .qb .qt{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-top:2px;font-size:13px;line-height:1.35;font-weight:700;color:#2B2622}
.tn .pinx{transition:opacity .25s}
.tn .pinx.dim{opacity:.35}
.tn .glo{fill:none;stroke-width:2;transform-box:fill-box;transform-origin:center;animation:tnglo 1.3s cubic-bezier(.2,.7,.3,1) 3;opacity:0}
@keyframes tnglo{0%{transform:scale(.7);opacity:.85}100%{transform:scale(2.1);opacity:0}}
@media (prefers-reduced-motion:reduce){.tn .glo{animation:none}}
.tn .chips button.sp{transition:background .2s,border-left-width .2s}
.tn .chips button.sp.on{background:color-mix(in srgb,var(--c) 9%,#fff);border-left-width:7px}
.tn .chips button.sp.on i{transform:scale(1.15);box-shadow:0 0 0 3px color-mix(in srgb,var(--c) 22%,#fff)}
.tn .chips button.sp.on:after{content:"−"}
.tn .chips .pop{flex:1 1 100%;margin-top:-8px}
.tn .chips .pop .nb{display:none}
.tn .pop .nb{display:inline-block;vertical-align:2px;margin-right:8px;width:22px;height:22px;line-height:22px;border-radius:50%;background:var(--pc);color:#fff;text-align:center;font-family:Jost,sans-serif;font-style:normal;font-weight:600;font-size:12px}
.tn .crumb{position:absolute;left:18px;top:16px;z-index:5;display:flex;align-items:center;gap:6px;font-family:"Shippori Mincho",serif;font-weight:600;font-size:13px;letter-spacing:.08em;color:#2B2622}
.tn .crumb button{font:inherit;color:#8C7B6E;background:none;border:0;padding:6px 0;cursor:pointer;text-decoration:underline;text-decoration-color:#CFCFCF;text-underline-offset:4px}
.tn .crumb i{font-style:normal;font-family:Jost,sans-serif;color:#B3AAA1;font-weight:300}
.tn .bk{position:absolute;right:12px;top:10px;z-index:6;display:none;font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:12px;letter-spacing:.06em;color:#5E534B;background:#fff;border:1px solid #D4D4D4;border-radius:99px;padding:8px 14px;cursor:pointer;box-shadow:0 1px 4px rgba(60,40,20,.08)}
.tn .cen{position:absolute;right:18px;top:20px;z-index:5;font-family:Jost,sans-serif;font-size:9px;letter-spacing:.34em;color:#A39A90;transition:color .4s}
.tn .hint{position:absolute;left:50%;transform:translateX(-50%);white-space:nowrap;bottom:14px;background:rgba(255,255,255,.88);border-radius:99px;padding:5px 12px;z-index:5;text-align:center;font-family:"Zen Kaku Gothic New",sans-serif;font-size:10.5px;letter-spacing:.08em;color:#8C7B6E;pointer-events:none}
.tn .mo{display:none;flex:none;gap:6px;align-items:center;overflow-x:auto;scrollbar-width:none;padding:8px 14px 0;background:#FFFFFF}.tn .mo::-webkit-scrollbar{display:none}.tn .mo button{flex:none}
.tn:not(.fs) .mo{display:none!important}
.tn .mo span{flex:none;font-family:"Zen Kaku Gothic New",sans-serif;font-size:11px;color:#8C7B6E;background:rgba(255,255,255,.88);border-radius:99px;padding:4px 9px}
.tn .mo button{height:30px;padding:0 10px;border-radius:99px;border:1px solid #D8D8D8;background:#fff;font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:12px;color:#2B2622;box-shadow:0 2px 6px rgba(60,45,35,.08)}
.tn .mo button b{display:inline-block;margin-left:6px;min-width:18px;height:18px;line-height:18px;border-radius:9px;background:var(--c);color:#fff;font-family:Jost,sans-serif;font-size:10.5px;font-weight:600}
.tn.fs .hint{opacity:0;transition:opacity .5s;pointer-events:none}.tn.fs .hint.sh{opacity:1}
.tn .hint:before{content:"";display:inline-block;width:5px;height:5px;border-radius:50%;background:#D9775A;margin-right:7px;vertical-align:1px}
.tn .g-ic{pointer-events:none;transition:opacity .35s}
.tn .ic .icb{filter:drop-shadow(0 1.5px 0 rgba(255,255,255,.9)) drop-shadow(0 2px 2px rgba(80,60,40,.18))}
/* 全画面の地図（地図の中だけで全部できる） */
.tn.fs{position:fixed;left:0;right:0;top:0;bottom:0;height:100dvh;z-index:200;margin:0;background:#FFFFFF;display:flex;flex-direction:column;overscroll-behavior:contain}
.tn.fs .fr{flex:1 1 auto;min-height:0;aspect-ratio:auto;margin:0;touch-action:none}
.tn.fs .chips,.tn.fs .pop,.tn.fs .lg,.tn.fs .g-mini{display:none!important}
.tn.fs .fr:before{display:none}
.tn .fsh{display:none}
.tn.fs .fsh{display:block;flex:none;padding:8px 14px 4px;background:#fff;border-bottom:1px solid #E3E3E3;box-shadow:0 2px 10px rgba(60,45,35,.06);position:relative;z-index:8}
.tn .fsh .ttl{display:flex;align-items:center;justify-content:space-between;margin:0 0 6px}
.tn .fsh .ttl b{display:flex;align-items:baseline;gap:10px;font-family:"Shippori Mincho",serif;font-weight:600;font-size:16px;letter-spacing:.12em;color:#2B2622}
@media(max-width:379px){.tn .fsh .ttl b small{display:none}}
.tn .fsh .ttl b{white-space:nowrap}
.tn .fsh .ttl b small{order:2;font-family:Jost,sans-serif;font-weight:400;font-size:8.5px;letter-spacing:.3em;color:#A39A90}
.tn .fsh .cl{width:36px;height:36px;border-radius:50%;border:1px solid #D4D4D4;background:#fff;font-family:Jost,sans-serif;font-size:20px;color:#5E534B;cursor:pointer;display:flex;align-items:center;justify-content:center;padding:0}
.tn .fsh .row{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;padding:2px 0 6px}
.tn .fsh .row::-webkit-scrollbar{display:none}
.tn .fsh .row button{flex:none;height:32px;padding:0 13px;border-radius:17px;border:1px solid #DADADA;background:#fff;font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:12.5px;letter-spacing:.04em;color:#5E534B;cursor:pointer;white-space:nowrap}
.tn .fsh .row button.on{background:#2B2622;border-color:#2B2622;color:#fff}
.tn .fsh .row.pf button{color:var(--c,#5E534B)}
.tn .fsh .row.pf button.on{background:var(--c,#2B2622);border-color:var(--c,#2B2622);color:#fff}
.tn .fsh .row button small{font-family:Jost,sans-serif;font-weight:500;font-size:11px;margin-left:5px;opacity:.75}
.tn .car{display:none}
.tn.fs .car{display:flex;flex:none;gap:10px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;padding:10px 9% calc(14px + env(safe-area-inset-bottom));background:linear-gradient(rgba(253,252,250,0),#FFFFFF 30%);margin-top:-6px;position:relative;z-index:7}
.tn .car::-webkit-scrollbar{display:none}
.tn .cc{flex:0 0 82%;scroll-snap-align:center;background:#fff;border:1px solid #D8D8D8;border-left:4px solid var(--c);border-radius:3px;padding:11px 14px 10px;box-shadow:0 4px 14px rgba(60,45,35,.08);transition:transform .25s,box-shadow .25s;cursor:pointer}
.tn .cc.on{transform:translateY(-3px);box-shadow:0 8px 20px rgba(60,45,35,.14)}
.tn .cc .d{font-family:"Zen Kaku Gothic New",sans-serif;font-size:11px;color:#8C7B6E;letter-spacing:.04em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tn .cc .d i{font-style:normal;font-weight:700;margin-right:6px}
.tn .cc .d u{text-decoration:none;margin-left:6px}
.tn .cc .t{font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:15px;line-height:1.45;color:#2B2622;margin:4px 0 8px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.tn .cc .t .nb{display:inline-block;vertical-align:1px;margin-right:6px;width:20px;height:20px;line-height:20px;border-radius:50%;background:var(--c);color:#fff;text-align:center;font-family:Jost,sans-serif;font-style:normal;font-weight:600;font-size:11px}
.tn .cc .w{display:flex;gap:6px;align-items:center;min-height:22px;margin:-2px 0 6px}
.tn .cc .w .cpl{font-family:"Zen Kaku Gothic New",sans-serif;font-size:12px;font-weight:500;color:#5F544B}
.tn .cc .w .cpl:before{content:"";display:inline-block;width:9px;height:11px;margin-right:4px;vertical-align:-1px;background:var(--c);-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 11'%3E%3Cpath d='M4.5 0A4.5 4.5 0 0 0 0 4.5C0 7.6 4.5 11 4.5 11S9 7.6 9 4.5A4.5 4.5 0 0 0 4.5 0Zm0 6.2a1.7 1.7 0 1 1 0-3.4 1.7 1.7 0 0 1 0 3.4Z'/%3E%3C/svg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 9 11'%3E%3Cpath d='M4.5 0A4.5 4.5 0 0 0 0 4.5C0 7.6 4.5 11 4.5 11S9 7.6 9 4.5A4.5 4.5 0 0 0 4.5 0Zm0 6.2a1.7 1.7 0 1 1 0-3.4 1.7 1.7 0 0 1 0 3.4Z'/%3E%3C/svg%3E") center/contain no-repeat}
.tn .cc .w .cfr{font-family:"Zen Kaku Gothic New",sans-serif;font-size:10.5px;font-weight:700;color:#4F7A3E;background:#EAF2E4;border-radius:99px;padding:2px 8px}
.tn .cc .ac{display:flex;gap:16px;align-items:center}
.tn .cc .ac a{font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:12px;color:#2B2622;text-decoration:none;border-bottom:1px solid #C7C7C7;padding:6px 0 2px}
.tn .cc .ac .ix{margin-left:auto;font-family:Jost,sans-serif;font-size:10.5px;color:#B3AAA1;letter-spacing:.08em}
.tn .zm{position:absolute;right:10px;bottom:46px;z-index:6;display:flex;flex-direction:column;gap:6px}
.tn .zm button,.tn .omk{display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,.94);border:1px solid #D4D4D4;box-shadow:0 1px 4px rgba(60,45,35,.1);color:#5E534B;cursor:pointer;touch-action:manipulation;-webkit-tap-highlight-color:transparent;padding:0}
.tn .zm button{width:34px;height:34px;border-radius:50%;font-family:Jost,sans-serif;font-size:19px;font-weight:400;line-height:1}
.tn .zm button:active,.tn .omk:active{transform:scale(.93)}
.tn .omk{position:absolute;left:12px;bottom:46px;z-index:6;gap:6px;height:36px;padding:0 14px;border-radius:18px;font-family:"Zen Kaku Gothic New",sans-serif;font-weight:700;font-size:12px;letter-spacing:.06em}
.tn .omk svg{width:15px;height:15px}
.tn .cr{position:absolute;right:16px;bottom:4px;z-index:5;font-size:7.5px;color:#BBBBBB;pointer-events:none}
.tn .pop{position:relative;background:#fff;border:1px solid #D8D8D8;border-top:0;border-left:3px solid var(--pc,#2B2622);max-height:0;overflow:hidden;opacity:0;transition:max-height .38s cubic-bezier(.2,.8,.2,1),opacity .25s}
.tn .pop.on{max-height:440px;opacity:1;overflow:auto}
.tn .pop .x{position:absolute;right:4px;top:2px;width:38px;height:38px;background:none;border:0;font-family:Jost,sans-serif;font-size:19px;color:#8C7B6E;cursor:pointer}
.tn .pop .gh{font-family:"Zen Kaku Gothic New",sans-serif;font-size:11px;letter-spacing:.12em;color:#A07E66;padding:12px 14px 0}
.tn .pi{padding:12px 46px 12px 14px;border-bottom:1px solid #EBEBEB}
.tn .pi:last-child{border-bottom:0}
.tn .pi .d{font-size:11px;color:#8C7B6E;letter-spacing:.04em}
.tn .pi .d i{font-style:normal;font-weight:700;margin-right:6px}
.tn .pi .d u{text-decoration:none;font-size:9.5px;border:1px solid currentColor;padding:0 4px;margin-left:6px}
.tn .pi .t{font-family:"Shippori Mincho",serif;font-weight:600;font-size:15px;line-height:1.45;color:#2B2622;margin:3px 0 0}
.tn .pi .ac{display:flex;flex-wrap:wrap;gap:4px 18px;margin-top:8px}
.tn .pi .ac a{white-space:nowrap;display:inline-block;font-size:11.5px;letter-spacing:.08em;color:#2B2622;text-decoration:underline;text-decoration-color:#C8C8C8;text-underline-offset:4px;padding:5px 0}
.tn .yd{margin-top:10px;border-top:1px dashed #E3E3E3;padding-top:8px}.tn .yd b{display:block;font-family:"Zen Kaku Gothic New",sans-serif;font-size:10.5px;font-weight:700;letter-spacing:.12em;color:#8C7B6E;margin-bottom:2px}.tn .yd a{display:flex;align-items:baseline;gap:8px;padding:5px 0;font-family:"Zen Kaku Gothic New",sans-serif;font-size:12.5px;font-weight:700;color:#2B2622;text-decoration:none;border-bottom:1px solid #F0F0F0}.tn .yd a:last-child{border-bottom:0}.tn .yd a span{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.tn .yd a em{font-style:normal;font-weight:500;font-size:11px;color:#8C7B6E;white-space:nowrap}.tn .yd a:after{content:"→";color:#B3AAA1;font-size:11px}.tn .cc{max-width:82%}.tn .cc .cb{min-width:0}.tn .yd a span{width:0}.tn .cc .yd,.tn .cc.ph .cb>.yd{margin-top:6px;padding-top:4px;padding-right:0}.tn .cc .yd a{padding:3px 0;font-size:12px}
.tn .pi.mini{cursor:pointer;padding:10px 46px 10px 14px;position:relative}
.tn .pi.mini:after{content:"›";position:absolute;right:18px;top:50%;transform:translateY(-50%);font-family:Jost,sans-serif;font-size:18px;color:#B3AAA1}
.tn .pi.mini .t{font-size:13.5px}
.tn .lg{display:none;justify-content:center;gap:16px;margin:8px 0 0;font-size:10px;color:#9C9187;letter-spacing:.06em}
.tn .lg span:before{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;background:#9C9187;margin-right:5px;vertical-align:-1px}
.tn .lg span.s:before{background:#fff;box-shadow:inset 0 0 0 2px #9C9187}
.tn .lg span.o:before{width:5px;height:5px;opacity:.5;vertical-align:1px}
.tn .g-mini circle{pointer-events:none}
.it.tnf .card{box-shadow:0 0 0 2px var(--pc,#2B2622)!important;transition:box-shadow .3s}
`;
var st=document.createElement("style");st.textContent=css;document.head.appendChild(st);

// ---- 枠 ----
var box=document.createElement("div");box.className="tn";
box.innerHTML=''+
 '<div class="fsh"><div class="ttl"><b><small>TOWN NOTE MAP</small>'+R.name+'おでかけマップ</b><button type="button" class="cl" aria-label="地図を閉じる">×</button></div><div class="row tb"></div><div class="row pf"></div></div>'+
 '<div class="fr"><svg class="m" preserveAspectRatio="xMidYMid meet"><g class="g-sh"></g><g class="g-pf"></g><g class="g-mu"></g><g class="g-mini"></g><g class="g-pin"></g></svg><div class="lbs"></div>'+
 '<div class="crumb"></div><div class="n" id="tnn"></div><div class="cen">'+R.en_all+'</div><button type="button" class="bk"></button><div class="hint"></div><div class="zm"><button type="button" data-z="in" aria-label="近づく">＋</button><button type="button" data-z="out" aria-label="はなれる">−</button></div><div class="cr">地図：国土数値情報（行政区域）を加工</div></div>'+
 '<div class="car"></div>'+
 '<div class="chips"></div>'+
 '<div class="pop" role="dialog"><button class="x" type="button" aria-label="閉じる">×</button><div class="pb"></div></div>'+
 '<div class="lg"><span>開催・オープン</span><span class="s">これからできる</span></div>';
var svg=$("svg.m",box),G={sh:$(".g-sh",svg),pf:$(".g-pf",svg),mu:$(".g-mu",svg),mini:$(".g-mini",svg),pin:$(".g-pin",svg)},LBS=$(".lbs",box),pop=$(".pop",box);

// ---- 今のページの状態を読む ----
var GEO={},OTH=[];
// ---- 燈の「関東イルミネーション」ページ（akari-auto scripts/illumi.py）とつなぐ所 ----
// ページの作り：都県ボタン .tabs button[data-f]（すべては空）、都県ごとの箱 .ps（地図の形が .pf なので別の名前）、カード li.it > .cw > a.cd（.nm 名前・.dt 日程・.fr 無料）と a.mp（地図）
function curPref(){var b=$(".tabs button.on");return b?b.dataset.f||"":""}
function curTab(){return "イルミネーション"}
function items(){var pf=curPref(),seen={},out=[];
 $$(".ps .it").forEach(function(w){var p=w.getAttribute("data-p")||"";if(pf&&p!==pf)return;var a=$(".cd",w);if(!a)return;var tt=$(".nm",a),k=key(tt&&tt.textContent);if(!k||seen[k])return;seen[k]=1;
  var g=GEO[k],d=$(".dt",a),mp=$(".mp",w),tags=$$(".fr",a).map(function(e){return e.textContent});
  out.push({w:w,a:a,k:k,t:tt.textContent,pref:p,d:d?d.textContent:"",tags:tags,href:a.getAttribute("href"),map:mp?mp.href:"",lat:g&&g[0],lon:g&&g[1],soon:false})});
 return out}
function others(){return[]}
function pickPref(pf){var b=$('.tabs button[data-f="'+(pf||"")+'"]');if(b)b.click()}
// 「地図で見る」は都県ボタンのすぐ下
function mount(){var f=$(".tabs");if(!f)return;if(f.nextSibling!==mb)f.parentNode.insertBefore(mb,f.nextSibling);
 if(!FS&&mb.nextSibling!==box)mb.parentNode.insertBefore(box,mb.nextSibling)}
function tabList(){return[]}
function prefList(){return $$(".tabs button").map(function(b){return {el:b,name:b.textContent,on:b.classList.contains("on")}})}
function tabCount(){return String(items().length)}
var ZONE=".tabs";
// 燈のページでは押された数を数えない
function cnt1(k){}

// ---- 形のデータ ----
var PF={},MU=[],GR={},HOME=null;
var LP=R.lp;
function ring2d(r){return r.map(function(c,i){var q=P(c[0],c[1]);return (i?"L":"M")+q[0].toFixed(2)+" "+q[1].toFixed(2)}).join("")+"Z"}
function geom2d(g){var ps=g.type==="Polygon"?[g.coordinates]:g.coordinates;return ps.map(function(p){return p.map(ring2d).join("")}).join("")}
function gbb(g){var b=[1e9,1e9,-1e9,-1e9],ps=g.type==="Polygon"?[g.coordinates]:g.coordinates;ps.forEach(function(p){p[0].forEach(function(c){var q=P(c[0],c[1]);b[0]=Math.min(b[0],q[0]);b[1]=Math.min(b[1],q[1]);b[2]=Math.max(b[2],q[0]);b[3]=Math.max(b[3],q[1])})});return b}
// 点が形の中にあるか（ピンがどの市・区にあるかを決める）
function inRing(x,y,r){var c=false;for(var i=0,j=r.length-1;i<r.length;j=i++){var a=r[i],b=r[j];if(((a[1]>y)!==(b[1]>y))&&(x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]))c=!c}return c}
function inGeom(lon,lat,g){var ps=g.type==="Polygon"?[g.coordinates]:g.coordinates;return ps.some(function(p){return inRing(lon,lat,p[0])&&!p.slice(1).some(function(h){return inRing(lon,lat,h)})})}
function el(t,a,par){var e=document.createElementNS(NS,t);for(var k in a)e.setAttribute(k,a[k]);if(par)par.appendChild(e);return e}
// ---- 点描（Xeno風）：面を細かい点で描く。色ごとに模様を1つ作る ----
var DEFS=null,DP={};
function mix(h,w){var n=parseInt(h.slice(1),16),r=n>>16,g=n>>8&255,b=n&255;return "rgb("+Math.round(r+(255-r)*w)+","+Math.round(g+(255-g)*w)+","+Math.round(b+(255-b)*w)+")"}
function shade(h,k){var n=parseInt(h.slice(1),16);return "rgb("+Math.round((n>>16)*k)+","+Math.round((n>>8&255)*k)+","+Math.round((n&255)*k)+")"}
function D(col){return col;  // 点描はやめた（10/29 オーナー：前の方が見やすい）。元の塗りのまま
 if(col==="#EAEAEA")return col;  // 選んでいない所は点なし（うるさくしない）
 if(!DEFS){DEFS=el("defs",{},svg);svg.insertBefore(DEFS,svg.firstChild)}var id="dp"+col.slice(1);
 if(!DP[id]){var pt=el("pattern",{id:id,patternUnits:"userSpaceOnUse",width:4,height:4},DEFS);el("rect",{width:"100%",height:"100%",fill:mix(col,.55)},pt);DP[id]=el("circle",{cx:2,cy:2,r:1,fill:shade(col,.93)},pt)}
 return "url(#"+id+")"}
function dotSize(u){var S=5.2*u;$$("pattern",DEFS||svg).forEach(function(pt){pt.setAttribute("width",S);pt.setAttribute("height",S);var c=pt.querySelector("circle");c.setAttribute("cx",S/2);c.setAttribute("cy",S/2);c.setAttribute("r",1.55*u)})}
function setup(KS){
 KS.pref.features.forEach(function(f){var p=f.properties.p,d=geom2d(f.geometry);PF[p]={bb:gbb(f.geometry),sh:el("path",{d:d,"class":"sh"},G.sh),path:el("path",{d:d,"class":"pf",fill:D(FILL[p])},G.pf)};
  PF[p].path.addEventListener("click",function(){if(level()===1&&PF[p].has)flash(PF[p].path,DEEP[p],function(){pickPref(p)})})});
 KS.muni.features.forEach(function(f){var pr=f.properties,m={p:pr.p,n:pr.n,c:pr.c,g:f.geometry,bb:gbb(f.geometry)};m.id=m.p+"|"+m.c+"|"+m.n;
  m.path=el("path",{d:geom2d(f.geometry),"class":"mu"},G.mu);m.path.__mu=m;m.path.addEventListener("click",function(ev){if(level()===2&&state.pref===m.p&&m.grp.has){ev.stopPropagation();var g=m.grp;g.mus.forEach(function(x){x.path.style.fill=D(DEEP[x.p])});setTimeout(function(){goMuni(g)},180)}});MU.push(m)});
 // 大阪市・京都市・神戸市・堺市などは、区をまとめて「市」として寄る
 MU.forEach(function(m){var cc=m.c&&/市$/.test(m.c)?m.c:"";var gid=m.p+"|"+(cc||m.n);var g=GR[gid];if(!g){g=GR[gid]={id:gid,p:m.p,n:cc||m.n,city:!!cc,mus:[],bb:[1e9,1e9,-1e9,-1e9]}}g.mus.push(m);m.grp=g;g.bb=[Math.min(g.bb[0],m.bb[0]),Math.min(g.bb[1],m.bb[1]),Math.max(g.bb[2],m.bb[2]),Math.max(g.bb[3],m.bb[3])]});
 var b=[1e9,1e9,-1e9,-1e9];PREFS.forEach(function(p){var x=PF[p].bb;b=[Math.min(b[0],x[0]),Math.min(b[1],x[1]),Math.max(b[2],x[2]),Math.max(b[3],x[3])]});HOME=b;
}

// ---- 見ている範囲（なめらかに寄る） ----
var vb=[0,0,100,100],anim=0;
function aspect(){var r=$(".fr",box).getBoundingClientRect();return r.width?r.height/r.width:1.12}
function fit(b,pad){var w=b[2]-b[0],h=b[3]-b[1],A=aspect();pad=pad||.12;var W=w*(1+pad*2),H=h*(1+pad*2)+h*.16;if(H/W>A)W=H/A;else H=W*A;var cx=(b[0]+b[2])/2,cy=(b[1]+b[3])/2;return [cx-W/2,cy-H/2,W,H]}
function fly(to){var from=vb.slice(),t0=performance.now(),D=RM?1:450;cancelAnimationFrame(anim);
 (function f(n){var k=Math.min(1,(n-t0)/D),e=1-Math.pow(1-k,3);vb=from.map(function(v,i){return v+(to[i]-v)*e});apply(k>=1);if(k<1)anim=requestAnimationFrame(f)})(t0)}
// ---- 地図は動かさない（押すと寄るだけ）。押し間違いを防ぐ ----
// ・指が少しでもずれたら「押した」にしない（ページを下にずらしただけで寄らない）
// ・府県の画面で色のついた所の少し外を押したときは、いちばん近い色のついた市・区へ寄る
var FR=$(".fr",box),tap0=null,moved=false;
FR.addEventListener("pointerdown",function(e){tap0={x:e.clientX,y:e.clientY};moved=false});
FR.addEventListener("pointermove",function(e){if(tap0&&Math.hypot(e.clientX-tap0.x,e.clientY-tap0.y)>10)moved=true});
FR.addEventListener("pointercancel",function(){moved=true});
FR.addEventListener("click",function(e){if(moved&&!e.target.closest("button")){e.stopPropagation();e.preventDefault();return}
 if(level()!==2||e.target.closest("button,.lb")||(e.target.classList&&e.target.classList.contains("hit")))return;
 var hit=null;if(e.target.__mu&&e.target.__mu.grp.has)return;
 var best=30;LB.forEach(function(l){if(!l.e.classList.contains("m")||l.e.classList.contains("hide"))return;var b=l.e.getBoundingClientRect(),d=Math.hypot(Math.max(b.left-e.clientX,0,e.clientX-b.right),Math.max(b.top-e.clientY,0,e.clientY-b.bottom));if(d<best){best=d;hit=l}});
 if(hit){e.stopPropagation();hit.e.click()}},true);
function px(){var r=svg.getBoundingClientRect();return vb[2]/(r.width||360)}  // 画面の1pxが地図の何単位か
// full=false：動いている途中（軽く：文字の位置だけ動かす）／full：止まったとき（文字の重なりも整える）
function apply(full){if(full===undefined)full=true;svg.setAttribute("viewBox",vb.join(" "));var u=px(),lv=level();dotSize(u);
 if(ICG){ICG.style.opacity=lv===1?1:0;$$(".ic",ICG).forEach(function(g){var k=34/40*u;g.setAttribute("transform","translate("+(g.__q[0]-20*k)+" "+(g.__q[1]-20*k)+") scale("+k+")")})}G.sh.setAttribute("transform","translate("+(1.4*u)+" "+(2.2*u)+")");
 // 文字は HTML で重ねる（小さくてもきれいに出る）。重なる文字は、大事な方だけ出す
 var r=svg.getBoundingClientRect(),placed=[];
 function pos(l){var x=((l.flip?l.x2:l.x)-vb[0])/vb[2]*r.width+(l.ox||0),y=(l.y-vb[1])/vb[3]*r.height+(l.oy||0);l.e.style.transform="translate("+x.toFixed(1)+"px,"+y.toFixed(1)+"px) "+(l.side?(l.flip?"translate(calc(-100% - 8px),-50%)":"translate(8px,-50%)"):"translate(-50%,-50%)");
  // ずらした札は、点から細い線でつなぐ（どの点の名前か分かるように）
  if(l.side){var far=Math.hypot(l.ox||0,l.oy||0)>=14;if(far&&!l.ln){l.ln=document.createElement("i");l.ln.className="ldr";LBS.insertBefore(l.ln,LBS.firstChild)}
   if(l.ln){l.ln.style.display=far?"block":"none";if(far){var dx=((l.x+l.x2)/2-vb[0])/vb[2]*r.width,dy=(l.y-vb[1])/vb[3]*r.height,ax=x+(l.flip?-8:8),ay=y,L=Math.hypot(ax-dx,ay-dy);
    l.ln.style.width=L.toFixed(1)+"px";l.ln.style.transform="translate("+dx.toFixed(1)+"px,"+dy.toFixed(1)+"px) rotate("+Math.atan2(ay-dy,ax-dx)+"rad)";l.ln.style.setProperty("--c",l.e.style.getPropertyValue("--c"))}}}}
 LB.forEach(function(l){if(full){l.flip=false;l.ox=l.oy=0;l.e.classList.remove("hide","sm","cm")}pos(l)});
 if(full)LB.forEach(function(l){if(!l.side)return;var b=l.e.getBoundingClientRect();if(b.right>r.right-(FS?56:12)){l.flip=true;pos(l)}});
 if(full)LB.slice().sort(function(a,b){return b.pri-a.pri}).forEach(function(l){l.e.classList.remove("fl");var b=l.e.getBoundingClientRect();if(l.e.classList.contains("t")&&b.right>r.right-16){l.e.classList.add("fl");b=l.e.getBoundingClientRect()}if(b.right<r.left||b.left>r.right||b.bottom<r.top+40||b.top>r.bottom-30){l.e.classList.add("hide");return}
  function hit(b){return placed.some(function(o){return b.left<o.right+2&&b.right>o.left-2&&b.top<o.bottom+1&&b.bottom>o.top-1})}
  // 府県の名前は消さない（どの府県も同じように出す）。重なるときは少しずらし、それでも重なれば件数の行を小さくまとめる
  if(hit(b)&&l.e.classList.contains("p")){var OF=[[0,10],[0,-10],[14,0],[-14,0],[0,20],[0,-20],[22,10],[-22,10],[22,-10],[-22,-10],[0,30],[0,-30]];
   for(var t=0;t<2&&hit(b);t++){if(t)l.e.classList.add("sm");for(var i=0;i<OF.length;i++){l.ox=OF[i][0];l.oy=OF[i][1];pos(l);b=l.e.getBoundingClientRect();if(!hit(b))break}}
   if(hit(b)){l.ox=l.oy=0;pos(l);b=l.e.getBoundingClientRect()}placed.push(b);return}
  // 色のついた市（件数つき）は、重なったら反対側・少し上下にずらして、なるべく地図に残す（「ほかにも」に行く市を減らす）
  if(hit(b)&&l.side&&l.e.classList.contains("m")&&l.e.querySelector("b")){var f0=l.flip,ok=false,inF=function(b){return b.left>=r.left+4&&b.right<=r.right-(FS?56:12)&&b.top>=r.top+40&&b.bottom<=r.bottom-30};
   // 重なった市の札は、点のまわりの空いている所をさがして置く（近い所から。遠いときは線でつなぐ）。それでもだめなら小さい札で
   var C=[];[0,14,26,40,56,72].forEach(function(R){(R?[0,1,2,3,4,5,6,7]:[0]).forEach(function(k){var an=k*Math.PI/4;C.push([Math.round(R*Math.cos(an)),Math.round(R*Math.sin(an))])})});
   for(var st2=0;st2<2&&!ok;st2++){if(st2)l.e.classList.add("cm");for(var q=0;q<C.length&&!ok;q++)for(var fz=0;fz<2&&!ok;fz++){l.flip=fz?!f0:f0;l.ox=C[q][0];l.oy=C[q][1];pos(l);b=l.e.getBoundingClientRect();if(!hit(b)&&inF(b))ok=true}}
   if(!ok){l.e.classList.remove("cm");l.flip=f0;l.ox=l.oy=0;pos(l);b=l.e.getBoundingClientRect()}}
  if(hit(b)){l.e.classList.add("hide");return}placed.push(b)});
 if(full&&lv===3){var gs=$$(".pinx",G.pin).filter(function(g){return g.dataset.n}),D=23;
  // 近すぎるピンは、おたがいに少しずつ押しのけて、どれも指で押せる間をあける（画面で23px）
  var P2=gs.map(function(g){return [g.__q[0]/u,g.__q[1]/u]}),O=P2.map(function(q){return q.slice()});
  for(var it=0;it<80;it++){var mv=false;for(var i=0;i<P2.length;i++)for(var j=i+1;j<P2.length;j++){var dx=P2[j][0]-P2[i][0],dy=P2[j][1]-P2[i][1],d=Math.hypot(dx,dy);if(d<D){mv=true;if(d<.01){dx=Math.cos(i+j);dy=Math.sin(i+j);d=1}var k=(D-d)/2/d;P2[i][0]-=dx*k;P2[i][1]-=dy*k;P2[j][0]+=dx*k;P2[j][1]+=dy*k}}if(!mv)break}
  gs.forEach(function(g,i){var dx=(P2[i][0]-O[i][0])*u,dy=(P2[i][1]-O[i][1])*u;if(Math.abs(dx)+Math.abs(dy)<1e-6)g.removeAttribute("transform");else g.setAttribute("transform","translate("+dx+" "+dy+")")})}
 var mr=(lv===1?1.4:lv===2?2.4:3)*u;$$("circle",G.mini).forEach(function(c){c.setAttribute("r",mr);c.setAttribute("stroke-width",.6*u)});
 $$(".pinx",G.pin).forEach(function(g){var r=+g.dataset.r,d=g.querySelector(".dot");d.setAttribute("r",r*u);var tn=g.querySelector(".pn");if(tn)tn.setAttribute("font-size",10*u);if(!full)g.removeAttribute("transform");var ps=g.querySelector(".psh");if(ps){ps.setAttribute("r",(r+.6)*u);ps.setAttribute("transform","translate(0 "+(1.6*u)+")")}if(full)d.setAttribute("stroke-width",r>4?2:1.2);g.querySelector(".hit").setAttribute("r",(lv===1?0:lv===3?(r<4?0:12):22)*u);var s=g.querySelector(".sel-r");if(s){s.setAttribute("r",(r+7)*u);s.setAttribute("stroke-width",1.5)}});
 // 番号ピンに重なる区の名前は消す（番号を見やすく・押しやすく）
 if(full&&lv===3){var DR=$$(".pinx",G.pin).filter(function(g){return g.dataset.n}).map(function(g){return g.querySelector(".dot").getBoundingClientRect()});
  LB.forEach(function(l){if(l.e.classList.contains("hide"))return;var b=l.e.getBoundingClientRect();if(DR.some(function(o){return b.left<o.right&&b.right>o.left&&b.top<o.bottom&&b.bottom>o.top}))l.e.classList.add("hide")})}
 if(full)moreCities(lv);
 placeBub();
}
// 選んだピンの上に小さな吹き出し（名前・日付・無料）。物件サイトの地図のように、下のカードを見なくても分かる。押せない（押し間違いを作らない）
var BUB=document.createElement("div");BUB.className="qb";FR.appendChild(BUB);var bubIt=null;
// 吹き出しは市に寄ったときだけ（全体・府県の画面では、府県や市の名前の札をかくさないため。そこでは下のカードで見る）
function placeBub(){if(!FS||!sel||sel.lat==null||level()<3){BUB.classList.remove("on");bubIt=null;return}
 var g=$$(".pinx",G.pin).filter(function(x){return x.querySelector(".sel-r")})[0];if(!g){BUB.classList.remove("on");return}
 if(bubIt!==sel){bubIt=sel;var fr=(sel.tags||[]).some(function(t){return t.indexOf("無料")>=0});
  BUB.style.setProperty("--c",PC[sel.pref]||"#2B2622");
  BUB.classList.toggle("ph",PH);BUB.innerHTML=(PH?thumb(sel,'qth'):'')+'<div class="qx"><div class="qm"><span class="qp">'+esc(sel.pref)+'</span>'+(sel.d?'<span class="qd">'+esc(sel.d)+'</span>':'')+(fr?'<span class="qf">無料</span>':'')+'</div><div class="qt">'+esc(sel.t)+'</div></div>'}
 var R=FR.getBoundingClientRect(),d=g.querySelector(".dot").getBoundingClientRect(),cx=d.left+d.width/2-R.left,top=d.top-R.top,bot=d.bottom-R.top;
 if(cx<0||cx>R.width||top<0||bot>R.height){BUB.classList.remove("on");return}
 BUB.classList.add("on");var w=BUB.offsetWidth,h=BUB.offsetHeight,x=Math.max(8,Math.min(R.width-w-8,cx-w/2));
 // 上と下で、市の名前の札に重ならない方に出す（重なりが少ない方）
 var L=$$(".lb.m:not(.hide)",box).map(function(e){var b=e.getBoundingClientRect();return [b.left-R.left,b.top-R.top,b.right-R.left,b.bottom-R.top]});
 function cover(y){if(y<44||y+h>R.height-28)return 1e9;var a=0;L.forEach(function(q){var ox=Math.min(x+w,q[2])-Math.max(x,q[0]),oy=Math.min(y+h,q[3])-Math.max(y,q[1]);if(ox>0&&oy>0)a+=ox*oy});return a}
 var yu=top-h-10,yd=bot+10,cu=cover(yu),cd=cover(yd),below=cd<cu,y=below?yd:yu;if(cu>=1e9&&cd>=1e9){below=top-h-12<44;y=below?yd:yu}
 BUB.classList.toggle("dn",below);BUB.style.transform="translate("+x.toFixed(1)+"px,"+y.toFixed(1)+"px)";BUB.style.setProperty("--ax",(cx-x).toFixed(1)+"px")}
// 重なって名前が消えた市は、地図の下にボタンで並べる（全画面のとき）
function moreCities(lv){var mo=$(".mo",box),hn=$(".hint",box);if(!mo){mo=document.createElement("div");mo.className="mo";var fr=$(".fr",box);fr.parentNode.insertBefore(mo,fr.nextSibling)}
 var hid=FS&&lv===2?LB.filter(function(l){return l.g&&l.e.classList.contains("hide")}):[];
 if(!hid.length){mo.style.display="none";return}
 mo.innerHTML="<span>ほかにも</span>";hid.forEach(function(l){var b=document.createElement("button");b.type="button";b.innerHTML=esc(l.g.n)+"<b>"+l.g.mus.length+"</b>";b.querySelector("b").textContent=(l.e.querySelector("b")||{}).textContent||"";b.style.setProperty("--c",PC[l.g.p]);b.onclick=function(ev){ev.stopPropagation();goMuni(l.g)};mo.appendChild(b)});
 mo.style.display="flex"}

// ---- 状態：関西（1）→ 府県（2）→ 市・区（3） ----
var LB=[];function addL(x,y,cls,html,pri,c){var e=document.createElement("div");e.className="lb "+cls;e.innerHTML=html;if(c)e.style.setProperty("--c",c);LBS.appendChild(e);LB.push({e:e,x:x,y:y,pri:pri});return e}
var state={pref:"",muni:null},list=[],lastSig="",ready=false,sel=null;
function level(){return state.muni?3:state.pref?2:1}
function goMuni(g){state.muni=g;sel=null;pop.classList.remove("on");render();fly(fit(g.bb,g.city?.04:.22));
 var only=list.filter(function(i){return i.lat!=null&&i.pref===g.p&&muniOf(i)&&muniOf(i).grp===g});if(only.length===1)setTimeout(function(){openPin(only[0])},700)}
function hotBox(pf){var b=null;list.forEach(function(i){if(i.lat==null||i.pref!==pf)return;var m=muniOf(i);if(!m)return;var g=m.grp.bb;b=b?[Math.min(b[0],g[0]),Math.min(b[1],g[1]),Math.max(b[2],g[2]),Math.max(b[3],g[3])]:g.slice()});return b}
function goPref(){state.muni=null;sel=null;pop.classList.remove("on");render();var hb=state.pref&&hotBox(state.pref);fly(state.pref?(hb?fit(hb,.18):fit(PF[state.pref].bb,.03)):fit(HOME,.02))}
// 押した所を一瞬こく光らせてから動く（押せたことが分かるように）
function flash(path,col,fn){path.setAttribute("fill",D(col));setTimeout(fn,180)}

function muniOf(it){if(it._m!==undefined)return it._m;it._m=null;for(var i=0;i<MU.length;i++){var m=MU[i];if(m.p===it.pref&&inGeom(it.lon,it.lat,m.g)){it._m=m;break}}
 if(!it._m){var q=P(it.lon,it.lat),best=1e9;MU.forEach(function(m){if(m.p!==it.pref)return;var cx=(m.bb[0]+m.bb[2])/2,cy=(m.bb[1]+m.bb[3])/2,d=(cx-q[0])*(cx-q[0])+(cy-q[1])*(cy-q[1]);if(d<best){best=d;it._m=m}})}return it._m}

function render(){var lv=level(),pf=state.pref,m=state.muni,pins=list.filter(function(i){return i.lat!=null});
 PREFS.forEach(function(p){var n=pins.filter(function(i){return i.pref===p}).length;PF[p].has=n>0;var on=lv===1?n>0:p===pf;PF[p].path.setAttribute("fill",D(on?FILL[p]:"#EAEAEA"));PF[p].sh.style.opacity=on?1:0;PF[p].path.style.cursor=lv===1&&n>0?"pointer":"default"});
 var cnt={};pins.forEach(function(i){if(i.pref!==pf)return;var mm=muniOf(i);if(mm){cnt[mm.grp.id]=(cnt[mm.grp.id]||0)+1}});
 var LIGHT=function(p){return R.light[p]};
 Object.keys(GR).forEach(function(id){GR[id].has=!!cnt[id]});
 if(lv===2)PF[pf].path.setAttribute("fill",D(LIGHT(pf)));
 if(lv===3)PF[pf].path.setAttribute("fill",D(LIGHT(pf)));
 // 線は「おでかけ先がある市・区」と「今いる市の区」だけ描く（ほかは描かず、すっきり見せる）
 var hw={};if(lv===3)pins.forEach(function(i){var mm=muniOf(i);if(mm&&mm.grp===m)hw[mm.id]=1});
 MU.forEach(function(x){var inP=x.p===pf,mine=lv===3&&x.grp===m,hot=x.grp.has,show=inP&&(lv===2?hot:(mine||hot));x.path.style.display=show?"":"none";if(!show)return;
  x.path.style.pointerEvents=lv===2?"auto":"none";x.path.style.cursor=lv===2?"pointer":"default";
  x.path.style.fill=D(mine?(hw[x.id]?DEEP[x.p]:FILL[x.p]):FILL[x.p]);x.path.style.opacity=lv===3&&!mine?.55:1});
 LBS.innerHTML="";LB=[];
 if(lv===1)PREFS.forEach(function(p){var c=LP[p],q=P(c[0],c[1]),n=pins.filter(function(i){return i.pref===p}).length;addL(q[0],q[1],"p",p+(n?"<small>"+n+(n>1?" SPOTS":" SPOT")+"</small>":""),9).style.color=n?PC[p]:"#B9AFA5"});
 if(lv===2)Object.keys(GR).forEach(function(id){var g=GR[id];if(g.p!==pf||!cnt[id])return;
  // ラベルはその市のピンのすぐ横に（形の端だと、広い市では離れすぎるため）
  var gp=pins.filter(function(i){var mm=muniOf(i);return mm&&mm.grp===g}).map(function(i){return P(i.lon,i.lat)});
  var x1=Math.max.apply(null,gp.map(function(q){return q[0]})),x0=Math.min.apply(null,gp.map(function(q){return q[0]})),cy=gp.reduce(function(a,q){return a+q[1]},0)/gp.length;
  var e=addL(x1,cy,"m",esc(g.n)+"<b>"+cnt[id]+"</b>",cnt[id],PC[pf]);LB[LB.length-1].side=1;LB[LB.length-1].x2=x0;LB[LB.length-1].g=g;e.addEventListener("click",function(ev){ev.stopPropagation();goMuni(g)})});
 if(lv===3&&m.city)m.mus.forEach(function(x){var cx=(x.bb[0]+x.bb[2])/2,cy=(x.bb[1]+x.bb[3])/2;addL(cx,cy,"w"+(hw[x.id]?" h":""),esc(x.n),hw[x.id]?2:0)});
 G.mini.innerHTML="";OTH.forEach(function(o){if(pf&&o.pref!==pf)return;var q=P(o.lon,o.lat);el("circle",{cx:q[0],cy:q[1],fill:PC[o.pref]||"#9C9187","fill-opacity":.5,stroke:"#fff","data-m":1},G.mini)});
 G.pin.innerHTML="";var selG=null;
 // 市の画面では、ピンに北から順に番号をふる（下の一覧と同じ番号）
 var NUM=lv===3?pins.filter(function(i){var mm=muniOf(i);return mm&&mm.grp===m}).sort(function(a,b){return b.lat-a.lat||a.lon-b.lon}):[];NUM.forEach(function(it,i){it._n=i+1});
 pins.forEach(function(it){if(pf&&it.pref!==pf)return;var q=P(it.lon,it.lat),c=PC[it.pref]||"#2B2622",inM=lv===3&&muniOf(it)&&muniOf(it).grp===m,isS=sel&&sel.k===it.k,r=lv===1?(isS?6:2.6):lv===2?(isS?8:5):(inM?(isS?11:9):3.5);
  var g=el("g",{"class":"pinx"+(lv===3&&sel&&inM&&!isS?" dim":"")},G.pin);g.dataset.r=r;if(isS)selG=g;
  if(lv>1)el("circle",{"class":"psh",cx:q[0],cy:q[1]},g);
  if(isS){el("circle",{"class":"sel-r",cx:q[0],cy:q[1],stroke:c},g);if(inM||FS)el("circle",{"class":"glo",cx:q[0],cy:q[1],stroke:c},g)}
  el("circle",{"class":"dot",cx:q[0],cy:q[1],fill:it.soon?"#fff":c,stroke:it.soon?c:"#fff"},g);
  if(inM){var t=el("text",{"class":"pn",x:q[0],y:q[1]},g);t.textContent=it._n;g.dataset.n=1;if(it.soon)t.setAttribute("fill",c)}
  g.__it=it;g.__q=q;
  var h=el("circle",{"class":"hit",cx:q[0],cy:q[1]},g);h.addEventListener("click",function(ev){ev.stopPropagation();tapPin(it)});
  });
 if(selG)G.pin.appendChild(selG);  // 選んだピンをいちばん上に
 var cr=$(".crumb",box);cr.innerHTML="";
 function cb(txt,fn){var b=document.createElement("button");b.type="button";b.textContent=txt;b.onclick=fn;cr.appendChild(b)}
 function sep(){var i=document.createElement("i");i.textContent="›";cr.appendChild(i)}
 function cur(txt){var s=document.createElement("span");s.textContent=txt;cr.appendChild(s)}
 if(lv===1)cur(R.name);else{cb(R.name,function(){pickPref("")});sep();if(lv===2)cur(pf);else{cb(pf,function(){goPref()});sep();cur(m.n)}}
 var ce=$(".cen",box);ce.textContent=pf?EN[pf]:R.en_all;ce.style.color=pf?PC[pf]:"";ce.style.display=lv===1?"":"none";
 var bk=$(".bk",box);bk.style.display=lv===1?"none":"block";bk.textContent=lv===3?"‹ "+pf+"にもどる":"‹ "+R.name+"にもどる";bk.onclick=function(){if(level()===3)goPref();else pickPref("")};
 var ch=$(".chips",box);if(pop.parentNode===ch)box.insertBefore(pop,ch);ch.innerHTML="";
 if(lv===3)NUM.forEach(function(it){var b=document.createElement("button");b.type="button";b.className="sp";b.style.setProperty("--c",PC[pf]);b.dataset.k=it.k;if(sel&&sel.k===it.k&&pop.classList.contains("on"))b.classList.add("on");b.innerHTML="<i>"+it._n+"</i><span>"+esc(it.t)+"</span>";b.onclick=function(){if(sel&&sel.k===it.k&&pop.classList.contains("on"))closePop();else openPin(it,null,"list")};ch.appendChild(b)});
 if(lv===2){Object.keys(GR).map(function(id){return GR[id]}).filter(function(g){return g.p===pf&&cnt[g.id]}).sort(function(a,b){return cnt[b.id]-cnt[a.id]}).forEach(function(g){var b=document.createElement("button");b.type="button";b.style.setProperty("--c",PC[pf]);if(m===g)b.className="cur";b.innerHTML=esc(g.n)+"<b>"+cnt[g.id]+"</b>";b.onclick=function(){if(state.muni!==g)goMuni(g)};ch.appendChild(b)})}
 if(FS)buildCar(lv===3?NUM:pins.filter(function(i){return !pf||i.pref===pf}));
 ch.classList.toggle("on",lv>1&&ch.children.length>0);ch.classList.toggle("l3",lv===3);
 placePop();
 var hn=$(".hint",box),ht=FS?(lv===1?R.unit+"を押すか、カードをめくってください":lv===2?"市の名前を押すと近づきます":"番号を押すか、カードをめくってください"):"";if(FS&&ht!==hn.textContent){hn.classList.add("sh");clearTimeout(hn._t);hn._t=setTimeout(function(){hn.classList.remove("sh")},3200)}
 $(".hint",box).textContent=FS?(lv===1?R.unit+"を押すか、カードをめくってください":lv===2?"市の名前を押すと近づきます":"番号を押すか、カードをめくってください"):lv===1?"色のついた府県を押すと、近づきます":lv===2?"下のボタンか、色のついた所を押すと近づきます":"番号を押すか、下の一覧から選べます";
 $("#tnn",box).innerHTML=(lv===3?m.n:pf||R.name)+"の"+curTab()+"<b>"+(lv===3?(cnt[m.id]||0):pins.filter(function(i){return !pf||i.pref===pf}).length)+"</b>か所";
 apply();}

// ---- ピンを押したとき（指1本分のまわりのピンも一緒に出す） ----
function tapPin(it){var lv=level();if(lv===1){pickPref(it.pref);return}
 if(lv===3){openPin(it);return}
 var u=px(),q=P(it.lon,it.lat),near=list.filter(function(o){if(o.lat==null||(state.pref&&o.pref!==state.pref))return false;var z=P(o.lon,o.lat);return Math.hypot(z[0]-q[0],z[1]-q[1])<24*u});
 if(lv===2&&near.length>2){var mm=muniOf(it);if(mm){goMuni(mm.grp);return}}
 openPin(it,near)}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function row(it,full){var c=PC[it.pref]||"#2B2622";
 var h='<div class="d"><i style="color:'+c+'">● '+esc(it.pref)+'</i>'+esc(it.d)+it.tags.map(function(t){return '<u style="color:#5E8A4A">'+esc(t)+'</u>'}).join("")+'</div><div class="t">'+esc(it.t)+'</div>';
 if(full)h+='<div class="ac"><a href="'+esc(it.href)+'" target="_blank" rel="noopener" data-k="地図ピン｜'+esc(it.t)+'">くわしく見る →</a>'+(it.map?'<a href="'+esc(it.map)+'" target="_blank" rel="noopener" data-k="地図ピン地図｜'+esc(it.t)+'">行き方 ↗</a>':'')+'<a href="#" class="go2">リストで見る ↓</a></div>';
 if(full&&typeof extraRow==="function")h+=extraRow(it);  // ページごとに足す行（泊まりのページ＝近くの宿）
 return h}
// カードの出る場所：地図で押したら地図のすぐ下、一覧で押したらその行のすぐ下
var popAt="map";
function placePop(){var ch=$(".chips",box),row=popAt==="list"&&sel&&level()===3?$$("button.sp",ch).filter(function(b){return b.dataset.k===String(sel.k)})[0]:null;
 if(row)row.after(pop);else if(pop.previousElementSibling!==$(".fr",box))$(".fr",box).after(pop)}
function openPin(it,near,from){if(!it)return;if(FS){sel=it;render();carTo(it);return}sel=it;popAt=from==="list"?"list":"map";near=(near&&near.length?near:[it]).slice();near.sort(function(a,b){return a===it?-1:b===it?1:0});
 var pb=$(".pb",pop);pop.style.setProperty("--pc",PC[it.pref]||"#2B2622");
 if(near.length>1){pb.innerHTML='<div class="gh">この辺りに '+near.length+' 件</div>'+near.map(function(o,i){return '<div class="pi'+(i?" mini":"")+'" data-i="'+i+'">'+row(o,!i)+'</div>'}).join("");
  $$(".pi.mini",pb).forEach(function(e){e.addEventListener("click",function(){openPin(near[+e.dataset.i],near)})});}
 else pb.innerHTML='<div class="pi">'+row(it,true)+'</div>';
 var t1=$(".t",pb);if(t1&&level()===3&&it._n){var nb=document.createElement("i");nb.className="nb";nb.textContent=it._n;t1.prepend(nb)}  // 地図と同じ番号をカードにも
 var g2=$(".go2",pb);if(g2)g2.addEventListener("click",function(e){e.preventDefault();toList(it)});
 pop.classList.add("on");render();
 setTimeout(function(){var b=pop.getBoundingClientRect();if(b.bottom>innerHeight-20)scrollBy({top:Math.min(b.bottom-innerHeight+40,b.top-60),behavior:"smooth"})},60);}
function closePop(){pop.classList.remove("on");if(sel){sel=null;if(ready)render()}}
$(".x",pop).addEventListener("click",closePop);
function toList(it){var w=it.w;if(w.classList.contains("cap")){var m=$(".cmore",w.parentNode);if(m)m.click();}
 w.classList.add("tnf");w.style.setProperty("--pc",PC[it.pref]||"#2B2622");w.scrollIntoView({behavior:"smooth",block:"center"});setTimeout(function(){w.classList.remove("tnf")},2200)}


// ---- 名物の絵（関西の画面だけ。見て楽しむ飾りなので押せない） ----
// 形は 40×40 の中に描く。線は府県の色、中は白
var ICON=R.icons;
var ICG=null;
function drawIcons(){if(!ICG){ICG=el("g",{"class":"g-ic"},svg);svg.insertBefore(ICG,G.mini)}ICG.innerHTML="";
 PREFS.forEach(function(p){var I=ICON[p];if(!I)return;var q=P(I.at[0],I.at[1]),g=el("g",{"class":"ic"},ICG);g.__q=q;
  g.innerHTML='<g class="icb" fill="none" stroke="'+PC[p]+'" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round">'+I.s+'</g>';var t=el("title",{},g);t.textContent=I.n})}
// ---- カードと吹き出しに、中身が分かる小さな絵（写真の代わり。公式の写真は使わない）。10/30 オーナー「月が完璧と思うなら実行」で本番に ----
// TRY：試作ページ（window.TN_TRY）だけで次の見せ方を試すときに使う
var TRY=!!window.TN_TRY,PH=true,LIGHT=R.light||{};
var KIND=[[/ハロウィ|HALLOWEEN|仮装|YOKAI|妖怪/i,"pumpkin"],[/クリスマス|Xmas|ツリー/i,"xmas"],[/コンサート|ライブ|LIVE|音楽|ジャズ|オーケストラ|演奏|森の音/i,"music"],
 [/サーカス|公演|演劇|舞台|寄席|ショー/,"stage"],[/謎|スタンプ|ラリー|めぐり|周遊|リサーチ/,"quest"],[/鉄道|SL|電車|列車|エクスプレス|トロッコ/,"rail"],
 [/花火/,"spark"],[/紅葉|もみじ|モミジ|錦秋|いちょう|イチョウ|銀杏/,"leaf"],[/拝観/,"torii"],[/スワップ|フリマ|蚤の市|古着/,"bag"],[/古本|本まつり|ブック|BOOK/i,"book"],
 [/菊花|菊まつり|菊花壇|バラ|ばら|コスモス|ダリア/,"flower"],
 [/キャラクター|サンリオ|ポケモン|ウルトラ|仮面ライダー|コナン|ムーミン|PINGU|トミカ|プラレール|アニメ|ジブリ|ちいかわ|戦隊|エヴァ|EVANGELION/i,"chara"],[/ネコ|猫/,"paw"],
 [/美術|博物|博覧|展|アート|芸術|ミュージアム|資料館|文化館|ドラマ館|記念館|ギャラリー|コレクション|漫画|Superblue|チームラボ|teamLab|モネ|浮世絵|広重|人形|EXHIBITION|イマーシブ/i,"frame"],
 [/イルミ|ミネーション|Illum|ライトアップ|光の|光と|の光|光る|ひかり|ナイト|NIGHT|夜景|夜散歩|灯|あかり|ENLIGHT|ルミナ|LIGHT|LuCe|HIKARI|燈/i,"spark"],
 [/花|はな|ガーデン|植物|フラワー/,"flower"],
 [/水族|アクア|ニフレル|海遊館/,"fish"],[/動物|アニマル|牧場|ズー|ZOO|どうぶつ|ネコ|猫|犬|アニタッチ/i,"paw"],
 [/酒|ワイン|ビール|ブルワリー/,"sake"],[/狩り|みかん|いちご|ぶどう|りんご|収穫|農園|枝豆|芋掘り/,"fruit"],
 [/カフェ|コーヒー|COFFEE|珈琲|喫茶|パン|スイーツ|ケーキ|チョコ/i,"cup"],
 [/ラーメン|ラー1|餃子|中華|美食|グルメ|食|やきいも|キッチンカー|市場|昼市|朝市|マルシェ|カレー|肉|しらす|魚/,"food"],
 [/体験|クラフト|ワークショップ|手作り|陶芸/,"craft"],[/温泉|湯|サウナ|スパ/,"onsen"],[/神社|寺|大社|神宮|八幡宮|天満宮|東照宮|城|参道|御朱印|戦国/,"torii"],
 [/展望|テラス|タワー|Sky|スカイ|ハルカス|ブリッジ|Bridge/i,"view"],[/ランド|遊園地|映画村|おもちゃ王国|ワールド|テーマパーク|アスレチック|リゾート/,"park"],
 [/祭|まつり|フェス|フェア|縁日|カーニバル|マーケット/i,"lantern"],[/水上|クルーズ|船|川下り|舟/,"boat"],[/公園|丘陵|高原|森|山|雲海|棚田|ハイキング|自然/,"tree"],
 [/モール|ストア|ショップ|店|ルクア|LUCUA/i,"bag"],[/オープン|開業|新店|施設|ホテル|アリーナ|駅/,"shop"]];
var KI={leaf:'<path d="M12 3l1.6 3.6 3.6-1-1 3.6 3.3 1.8-3.6 1.6 1.2 3.4-3.6-1.4L12 18l-1.5-3.4-3.6 1.4 1.2-3.4L4.5 11l3.3-1.8-1-3.6 3.6 1z"/><path d="M12 18v3.5"/>',
 spark:'<path d="M12 3c.8 4.6 2.9 6.9 7.5 7.6-4.6.8-6.7 3-7.5 7.6-.8-4.6-2.9-6.8-7.5-7.6C9.1 9.9 11.2 7.6 12 3z"/><path d="M18.5 16.5l.6 1.6 1.6.6-1.6.6-.6 1.6-.6-1.6-1.6-.6 1.6-.6z"/>',
 lantern:'<path d="M9 4.5h6M9 19.5h6M12 2.5v2M12 19.5v2"/><path d="M8.5 6.5c-2.6 3.3-2.6 7.7 0 11h7c2.6-3.3 2.6-7.7 0-11z"/><path d="M6.6 10h10.8M6.6 14h10.8"/>',
 flower:'<circle cx="12" cy="10" r="2.2"/><path d="M12 7.8c-1.6-3.4 1.6-3.4 0 0M14.1 9.3c2.8-2.5 3.8.5 0 1.4M13.3 12c1.8 3.3-1.2 4.1-1.3.2M10.7 12c-1.8 3.3 1.2 4.1 1.3.2M9.9 9.3c-2.8-2.5-3.8.5 0 1.4"/><path d="M12 12.2V21M12 17c1.5-1.6 3-2 4.5-1.8"/>',
 frame:'<rect x="4" y="5" width="16" height="13" rx="1"/><path d="M4 15l4.5-4 3.5 3 2.5-2 5.5 4.5"/><circle cx="15.5" cy="8.8" r="1.3"/><path d="M9 21h6"/>',
 cup:'<path d="M5 9h11v5a5 5 0 0 1-5 5h-1a5 5 0 0 1-5-5z"/><path d="M16 10.5h1.5a2.3 2.3 0 0 1 0 4.6H16"/><path d="M8.5 3.5c-1 1.2 1 2 0 3.3M12 3.5c-1 1.2 1 2 0 3.3"/>',
 onsen:'<path d="M4.5 13c0 4.2 3.4 7 7.5 7s7.5-2.8 7.5-7z"/><path d="M8 10c-1.2-1.6 1.2-2.6 0-4.4M12 10c-1.2-1.6 1.2-2.6 0-4.4M16 10c-1.2-1.6 1.2-2.6 0-4.4"/>',
 paw:'<ellipse cx="12" cy="15.5" rx="4" ry="3.3"/><circle cx="6.8" cy="10.5" r="1.7"/><circle cx="17.2" cy="10.5" r="1.7"/><circle cx="9.7" cy="6.8" r="1.7"/><circle cx="14.3" cy="6.8" r="1.7"/>',
 torii:'<path d="M3.5 5.5c5.6 1.2 11.4 1.2 17 0M5.5 9.5h13M7.5 7v13.5M16.5 7v13.5M12 6.6v2.9"/>',
 shop:'<path d="M4 9l1.5-4.5h13L20 9"/><path d="M4 9c0 1.5 1.3 2.3 2.7 2.3S9.3 10.5 9.3 9c0 1.5 1.3 2.3 2.7 2.3s2.7-.8 2.7-2.3c0 1.5 1.3 2.3 2.6 2.3S20 10.5 20 9"/><path d="M5.5 11.3V20h13v-8.7M10 20v-5h4v5"/>',
 quest:'<circle cx="10.5" cy="10.5" r="5.5"/><path d="M14.5 14.5l5 5"/><path d="M10.5 8.2v.1M10.5 10v2.6"/>',
 rail:'<rect x="6" y="3.5" width="12" height="13" rx="3"/><path d="M6 10h12"/><circle cx="9" cy="13.3" r=".6"/><circle cx="15" cy="13.3" r=".6"/><path d="M8.5 16.5L6.5 20.5M15.5 16.5l2 4M7.5 19h9"/>',
 pumpkin:'<path d="M12 7c-4.5 0-7.5 2.7-7.5 6.5S7.5 20 12 20s7.5-2.7 7.5-6.5S16.5 7 12 7z"/><path d="M12 7c-1.8 1.8-1.8 11.2 0 13M12 7c1.8 1.8 1.8 11.2 0 13M12 7V4.5c1-.8 2-1 3-.8"/>',
 xmas:'<path d="M12 4l3.5 5h-2l4 5h-2.5l3.5 5H5.5L9 14H6.5l4-5h-2z"/><path d="M12 19v2.5M12 2v.5"/>',
 music:'<path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/>',
 stage:'<path d="M3.5 19.5L12 4l8.5 15.5z"/><path d="M12 4v15.5M9 19.5l3-5 3 5"/>',
 chara:'<path d="M12 3.5l2.5 5.2 5.7.8-4.1 4 1 5.6L12 16.4l-5.1 2.7 1-5.6-4.1-4 5.7-.8z"/>',
 fish:'<path d="M3.5 12c3-4.5 9-5.5 13-1.5l3.5-3v9l-3.5-3c-4 4-10 3-13-1.5z"/><circle cx="8" cy="11" r=".7"/>',
 sake:'<path d="M7 3.5h10l-1.5 8a3.5 3.5 0 0 1-7 0z"/><path d="M12 15v5M8.5 20.5h7M7.6 7h8.8"/>',
 fruit:'<circle cx="12" cy="13.5" r="6.5"/><path d="M12 7V4.5M12 6c1.5-2 3.5-2.3 5-1.7-1 1.8-2.8 2.3-5 1.7z"/>',
 food:'<path d="M3.5 11.5h17a8.5 8.5 0 0 1-17 0z"/><path d="M8 20h8M14 3.5l-3 7M18 4.5l-4 6"/>',
 craft:'<circle cx="6.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/><path d="M8.3 15.7L18 4M15.7 15.7L6 4"/>',
 view:'<path d="M12 2.5v3M9.5 21l2.5-15.5L14.5 21M10.3 13h3.4M7 21h10M8.5 8.5h7"/>',
 park:'<circle cx="12" cy="10" r="6.5"/><circle cx="12" cy="10" r="1.2"/><path d="M12 3.5v13M5.5 10h13M7.4 5.4l9.2 9.2M16.6 5.4l-9.2 9.2M9 21l3-5 3 5M7.5 21h9"/>',
 bag:'<path d="M5 8h14l-1 12.5H6z"/><path d="M9 10V6.5a3 3 0 0 1 6 0V10"/>',
 book:'<path d="M12 6.5c-2-1.6-5-2-8-1.5v13c3-.5 6 0 8 1.5 2-1.5 5-2 8-1.5V5c-3-.5-6-.1-8 1.5z"/><path d="M12 6.5v13"/>',
 boat:'<path d="M3.5 14.5h17l-2.5 4h-12z"/><path d="M12 4v10.5M12 5l5.5 7.5H12"/><path d="M3 21c1.5-1 3-1 4.5 0s3 1 4.5 0 3-1 4.5 0 3 1 4.5 0"/>',
 tree:'<circle cx="12" cy="9" r="5.5"/><path d="M12 14.5V21M9.5 17.5l2.5 1.5 2.5-1.5"/>',
 pin:'<path d="M12 21s6.5-6.1 6.5-11A6.5 6.5 0 0 0 5.5 10c0 4.9 6.5 11 6.5 11z"/><circle cx="12" cy="10" r="2.3"/>'};
function kindOf(it){var t=(it.t||"")+" "+(it.tags||[]).join(" ");for(var i=0;i<KIND.length;i++)if(KIND[i][0].test(t))return KIND[i][1];return it.soon||/できた|もうすぐ/.test(curTab())?"shop":"pin"}
function thumb(it,cls){var c=PC[it.pref]||"#2B2622",k=kindOf(it);return '<div class="'+cls+'" data-k="'+k+'" style="background:'+(LIGHT[it.pref]||"#F0F0F0")+'"><svg viewBox="0 0 24 24" fill="none" stroke="'+c+'" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'+KI[k]+'</svg></div>'}
// ---- 全画面の地図：下のカードを横にめくると、地図のピンが光る ----
var FS=false,CAR=$(".car",box),carSig="",carItems=[],carLock=null,carQ=false;
function buildCar(arr){var sig=arr.map(function(i){return i.k}).join("|")+"#"+level();if(sig===carSig)return;carSig=sig;carItems=arr.slice();
 CAR.innerHTML=arr.map(function(it,i){var mm=muniOf(it),pl=mm?mm.grp.n:"",fr=it.tags.indexOf("無料")>=0;
  var w='<div class="w">'+(pl?'<span class="cpl">'+esc(pl)+'</span>':'')+(fr?'<span class="cfr">無料</span>':'')+'</div>';
  return '<div class="cc'+(PH?' ph':'')+'" data-i="'+i+'" style="--c:'+(PC[it.pref]||"#2B2622")+'">'+(PH?thumb(it,'cth')+'<div class="cb">':'')+row(it,true).replace(/<u style[^>]*>無料<\/u>/,"").replace('<div class="t">','<div class="t">'+(level()===3&&it._n?'<i class="nb">'+it._n+'</i>':'')).replace('<div class="ac">',w+'<div class="ac">')+(PH?'</div>':'')+'</div>'}).join("");
 $$(".cc",CAR).forEach(function(c,i){var ac=$(".ac",c);if(ac){var g2=$(".go2",ac);if(g2)g2.remove();var ix=document.createElement("span");ix.className="ix";ix.textContent=(i+1)+" / "+arr.length;ac.appendChild(ix)}
  c.addEventListener("click",function(e){if(e.target.closest("a"))return;var it=carItems[i];if(sel!==it){carTo(it)}})});
 CAR.scrollLeft=0;if(arr.length&&(!sel||arr.indexOf(sel)<0)){sel=arr[0];setTimeout(function(){render()},0)}markCar()}
function markCar(){$$(".cc",CAR).forEach(function(c,i){c.classList.toggle("on",carItems[i]===sel)})}
function carTo(it){var i=carItems.indexOf(it);if(i<0)return;var c=$$(".cc",CAR)[i];carLock=it;sel=it;markCar();
 CAR.scrollTo({left:c.offsetLeft-(CAR.clientWidth-c.offsetWidth)/2,behavior:RM?"auto":"smooth"});setTimeout(function(){carLock=null},700);seePin(it)}
function seePin(it){var q=P(it.lon,it.lat),mx=vb[2]*.12,my=vb[3]*.18;if(q[0]<vb[0]+mx||q[0]>vb[0]+vb[2]-mx||q[1]<vb[1]+my||q[1]>vb[1]+vb[3]-my)fly([q[0]-vb[2]/2,q[1]-vb[3]/2,vb[2],vb[3]])}
CAR.addEventListener("scroll",function(){if(carQ)return;carQ=true;requestAnimationFrame(function(){carQ=false;var mid=CAR.scrollLeft+CAR.clientWidth/2,best=-1,bd=1e9;
 $$(".cc",CAR).forEach(function(c,i){var d=Math.abs(c.offsetLeft+c.offsetWidth/2-mid);if(d<bd){bd=d;best=i}});var it=carItems[best];
 if(!it||it===sel)return;if(carLock&&carLock!==it)return;sel=it;render();markCar();seePin(it)})},{passive:true});
// 上の帯：タブと府県ボタン（ページの本物のボタンを押す）
function buildHead(){var tb=$(".fsh .tb",box),pr=$(".fsh .pf",box);tb.innerHTML="";pr.innerHTML="";
 tabList().forEach(function(t){if(t.off)return;var x=document.createElement("button");x.type="button";x.innerHTML=esc(t.name)+(t.count?"<small>"+esc(t.count)+"</small>":"");if(t.on)x.className="on";x.onclick=function(){t.el.click();setTimeout(function(){sync();buildHead()},120)};tb.appendChild(x)});
 prefList().forEach(function(t){var x=document.createElement("button");x.type="button";x.textContent=t.name;if(PC[t.name])x.style.setProperty("--c",PC[t.name]);if(t.on)x.className="on";x.onclick=function(){t.el.click();setTimeout(function(){sync();buildHead()},120)};pr.appendChild(x)})}
// スマホの「戻る」でも地図を閉じる
addEventListener("popstate",function(){if(OPEN)setOpen(false,true)});
// 別のページから戻った時・開き直した時は、地図を閉じて最初の状態から（前の続きのまま残さない）
function fresh(){var st=history.state;if(st&&st.tnmap)try{history.replaceState(null,"")}catch(e){}
 if(OPEN)setOpen(false,true);
 var t=tabList().filter(function(x){return !x.off})[0];if(t&&!t.on)t.el.click();
 var a=prefList()[0];if(a&&!a.on)a.el.click()}
addEventListener("pageshow",function(e){if(e.persisted)fresh()});
if(history.state&&history.state.tnmap)fresh();
$(".fsh .cl",box).addEventListener("click",function(){if(history.state&&history.state.tnmap)history.back();else setOpen(false)});
// ---- ＋／−／⟳ボタン（指の操作なしで、寄る・引く・最初にもどる） ----
function zoomBy(k){var H0=fit(HOME,.02),cx=vb[0]+vb[2]/2,cy=vb[1]+vb[3]/2,W=Math.max(10,Math.min(vb[2]*k,H0[2])),H=W*vb[3]/vb[2];
 if(W>=H0[2]-1e-6){fly(H0);return}fly([cx-W/2,cy-H/2,W,H])}
$$(".zm button",box).forEach(function(b){b.addEventListener("click",function(e){e.stopPropagation();var z=b.dataset.z;
 if(z==="in")zoomBy(.6);else if(z==="out")zoomBy(1.7);else{if(level()>1)pickPref("");else fly(fit(HOME,.02))}})});

// ---- 今のページとつなぐ ----
var mb=document.createElement("button");mb.type="button";mb.className="tnbtn";
var OPEN=false;
var MINI=R.mini;
mb.innerHTML='<span class="mm"><svg>'+Object.keys(MINI).map(function(k){return '<path d="'+MINI[k]+'" fill="'+DEEP[k]+'" stroke="#fff" stroke-width="1" vector-effect="non-scaling-stroke"/>'}).join("")+'</svg></span><span class="tx"><b class="t1">地図で見る</b><small class="t2"></small></span><i class="ar">›</i>';
// ボタンの小さい文字：地図に出る件数（今のタブ・府県・無料だけに合い、場所が分かるカード。例：開催中の76か所を、関西の地図で）
function mbUpd(){var a=items(),n=a.filter(function(i){return i.lat!=null}).length,t=curTab();/* 10/31 オーナー「数あってる？」：場所が1つに決まらないカード（3か所くらべ等）があるときは、全部の数も出す */var x=!n?R.name+"の地図で探す":n<a.length?t+a.length+"件のうち、"+n+"か所を地図で":t+"の"+n+"か所を、"+R.name+"の地図で",e=$(".t2",mb);if(e.textContent!==x)e.textContent=x}
// 開くと画面いっぱいの地図になる。閉じるとリストのいつもの場所にもどる
function setOpen(v,fromPop){if(v===OPEN&&v)return;OPEN=v;FS=v;
 if(v){document.body.appendChild(box);box.classList.remove("shut");box.classList.add("fs");document.documentElement.style.overflow="hidden";
  if(!fromPop)try{history.pushState({tnmap:1},"")}catch(e){}
  buildHead();carSig="";if(!loading)load();else if(ready){lastSig="";sync()}}
 else{box.classList.remove("fs");box.classList.add("shut");document.documentElement.style.overflow="";sel=null;pop.classList.remove("on");mount()}
 if(v===false)mbUpd()}
mb.addEventListener("click",function(){cnt1("地図｜地図で見る");setOpen(true)});
function toMap(){var y=box.getBoundingClientRect().top+scrollY-12;scrollTo({top:y,behavior:RM?"auto":"smooth"})}
function sync(){mount();if(!ready||!OPEN)return;var pf=curPref(),sig=pf+"|"+curTab();if(sig===lastSig)return;var first=!lastSig,pfChanged=first||lastSig.split("|")[0]!==pf;lastSig=sig;
 list=items();OTH=others();var tb=curTab();$(".lg",box).innerHTML='<span'+(tb==="もうすぐ"?' class="s"':'')+'>'+esc(tb)+'</span><span class="o">ほかのタブ</span>';$(".lg",box).style.display="flex";sel=null;pop.classList.remove("on");
 if(!pfChanged&&state.muni&&!list.some(function(i){var mm=i.lat!=null&&i.pref===state.pref&&muniOf(i);return mm&&mm.grp===state.muni})){goPref();return}
 if(pfChanged){state.pref=pf;state.muni=null;if(first){var hb=pf&&hotBox(pf);vb=pf?(hb?fit(hb,.18):fit(PF[pf].bb,.03)):fit(HOME,.02);render()}else goPref()}else render();}
document.addEventListener("click",function(e){if(e.target.closest(ZONE)){if(!FS){mount();mbUpd()}setTimeout(function(){sync();mbUpd()},90)}});
addEventListener("resize",function(){if(ready)apply()});
mount();
// ページがタブや府県ボタンを動かした瞬間に、見出し・府県ボタン・地図ボタンを元の場所へ戻す（画面に出る前に直すので、一瞬消えたり位置がずれたりしない）
try{new MutationObserver(function(){if(!FS){mount();mbUpd()}}).observe(document.body,{childList:true,subtree:true})}catch(e){}
// タブ・府県ボタンを押したときの灰色の四角（スマホの押した印）を出さない
st.textContent+=ZONE.split(",").map(function(z){return z+" button"}).join(",")+"{-webkit-tap-highlight-color:transparent;touch-action:manipulation}";
// 地図のデータは、はじめて開いたときだけ読む（開かない人は軽いまま）
// 場所の一覧（小さい）は最初に読む：ボタンの「Nか所」を地図に出るピンの数と合わせるため
var geoP=fetch(TNB+"geo.json",{cache:"no-store"}).then(function(r){return r.json()}).catch(function(){return{}}).then(function(g){Object.keys(g).forEach(function(k){if(g[k][0]!=null)GEO[key(k)]=g[k]});mbUpd()});
var loading=false;function load(){loading=true;
Promise.all([geoP,fetch(TNB+R.shapes).then(function(r){return r.json()})]).then(function(a){
 setup(a[1]);drawIcons();ready=true;lastSig="";sync();mbUpd();window.__tnReady=true;
}).catch(function(e){console.error(e);$(".fr",box).style.display="none"});}
setOpen(OPEN);mbUpd();
// 小さい関西の絵の大きさを合わせる
try{var ms=$(".mm svg",mb),bb=ms.getBBox();ms.setAttribute("viewBox",[bb.x-2,bb.y-2,bb.width+4,bb.height+4].join(" "))}catch(e){}
})();
