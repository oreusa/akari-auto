// AIタイプ図鑑：ページを作る。node src/build.js （SITE_URL で公開先を変えられる）
'use strict';
const fs=require('fs'),path=require('path');
const ROOT=path.join(__dirname,'..'),OUT=path.join(ROOT,'site');
const SITE=(process.env.SITE_URL||'https://ai-type-zukan.pages.dev').replace(/\/$/,'');
const NOINDEX=process.env.NOINDEX!=='0';
const src=fs.readFileSync(path.join(__dirname,'data.js'),'utf8');
const D=new Function(src+';return {HOUSES,PACE,PACE_D,ROMAN,TYPES,KI,CH,ORACLE,USES,QS,OQS,VIRT,RANKS,KUSE,MISS,MISS_OF_V}')();
const {HOUSES,PACE,PACE_D,ROMAN,TYPES,KI,CH,USES,VIRT,RANKS,KUSE,MISS}=D;
fs.copyFileSync(path.join(__dirname,'data.js'),path.join(OUT,'assets','data.js'));
const V=String(Date.now()).slice(-8);// 読み直しの印

const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const pad=n=>String(n).padStart(2,'0');
const IMG=(t,k)=>`/img/${pad(t+1)}_${k+1}.webp`;
const full=(t,k)=>KI[k].n+TYPES[t].n;
const camp=t=>Math.floor(t/3),pace=t=>t%3;
const first=s=>String(s).split('。')[0]+'。';
const diag=c=>3-c,flipAsk=c=>(c+2)%4;
const pals=t=>{const c=camp(t),p=pace(t);return {best:diag(c)*3+p,learn:c*3+[2,0,1][p],clash:flipAsk(c)*3+[2,0,0][p]}};

const LOGO=`<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="14.5" fill="none" stroke="#D6B068" stroke-width="1.2"/><circle cx="16" cy="16" r="10.5" fill="none" stroke="#D6B06866" stroke-width=".8"/><path d="M16 3.5 18 14 28.5 16 18 18 16 28.5 14 18 3.5 16 14 14Z" fill="#F0DCAA"/><path d="M16 9.5 17 15 22.5 16 17 17 16 22.5 15 17 9.5 16 15 15Z" fill="#07070F"/></svg>`;
const NAV=[['/uranai/','占う','uranai'],['/hoshi/','十二の星','hoshi'],['/kurai/','主の位','kurai'],['/en/','縁','en'],['/zukan/','図鑑','zukan']];

function card(t,k,{size='',lazy=true,rev=false}={}){
  return `<div class="tcard c${camp(t)}${size?' '+size:''}${rev?' rev':''}"><img src="${IMG(t,k)}" alt="${esc(full(t,k))}のカード" width="640" height="960"${lazy?' loading="lazy"':''}><span class="num">${ROMAN[t]}</span><span class="nm"><small>${esc(TYPES[t].star)}</small><b>${esc(full(t,k))}</b></span></div>`;
}

function page({file,title,desc,page,body,og='/og/default.jpg',cur='',crumbs=null,ld=null,funnel=false,data={},extraHead=''}){
  const url=SITE+'/'+file.replace(/index\.html$/,'');
  const t=title?`${title}｜AIタイプ図鑑`:'AIタイプ図鑑｜あなたのAIが引く、あなたのカード';
  const crumbLd=crumbs?{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"AIタイプ図鑑","item":SITE+'/'},...crumbs.map((c,i)=>({"@type":"ListItem","position":i+2,"name":c[1],...(c[0]?{item:SITE+c[0]}:{})}))]}:null;
  const lds=[ld,crumbLd].filter(Boolean).map(x=>`<script type="application/ld+json">${JSON.stringify(x).replace(/</g,'\\u003c')}</script>`).join('');
  const dattr=Object.entries(data).map(([k,v])=>` data-${k}="${esc(v)}"`).join('');
  const html=`<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>${esc(t)}</title>
<meta name="description" content="${esc(desc)}">
${NOINDEX?'<meta name="robots" content="noindex,nofollow">\n':''}<link rel="canonical" href="${url}">
<meta name="theme-color" content="#07070F">
<meta property="og:type" content="${page==='home'?'website':'article'}">
<meta property="og:site_name" content="AIタイプ図鑑">
<meta property="og:title" content="${esc(title||'AIタイプ図鑑')}">
<meta property="og:description" content="${esc(desc)}">
<meta property="og:url" content="${url}">
<meta property="og:image" content="${SITE}${og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Shippori+Mincho+B1:wght@700;800&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap">
<link rel="stylesheet" href="/assets/site.css?v=${V}">
${extraHead}${lds}
</head>
<body data-page="${page}"${dattr}>
<canvas id="sky" aria-hidden="true"></canvas>
<a class="sr" href="#main">本文へ</a>
<header class="hdr"><div class="wrap">
<a class="logo" href="/">${LOGO}<span>AIタイプ図鑑<small>AI TYPE TAROT</small></span></a>
${funnel==='bare'?'':funnel?'<a class="hdr-exit" href="/uranai/">やめる</a>':`<nav class="nav" aria-label="メニュー">${NAV.map(([h,n,k])=>`<a href="${h}"${k===cur?' aria-current="page"':''}>${n}</a>`).join('')}<a class="only-sp" href="/uranai/">無料で占う</a></nav>
<a class="btn sm cta" href="/uranai/">無料で占う</a>
<button class="menu-btn" type="button" aria-label="メニュー" aria-expanded="false"><svg viewBox="0 0 24 24" fill="none" stroke="#EEE8DA" stroke-width="1.6" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>`}
</div></header>
<main id="main">
${crumbs?`<div class="wrap"><nav class="crumbs" aria-label="現在地"><a href="/">トップ</a>${crumbs.map(c=>`<span aria-hidden="true">/</span>${c[0]?`<a href="${c[0]}">${esc(c[1])}</a>`:`<span aria-current="page">${esc(c[1])}</span>`}`).join('')}</nav></div>`:''}
${body}
</main>
${funnel?'':FOOTER}
<script src="/assets/data.js?v=${V}"></script>
<script src="/assets/app.js?v=${V}"></script>
</body>
</html>
`;
  const fp=path.join(OUT,file);fs.mkdirSync(path.dirname(fp),{recursive:true});fs.writeFileSync(fp,html);
  return url;
}

const FOOTER=`<footer class="ftr"><div class="wrap">
<div class="cols">
<div><a class="logo" href="/">${LOGO}<span>AIタイプ図鑑<small>AI TYPE TAROT</small></span></a><p class="note">いつものAIに呪文を一つ送ると、AIがあなたとのやり取りを思い出して、六十枚のカードから一枚を引きます。登録なし・無料。</p></div>
<div><h3>占う</h3><ul><li><a href="/uranai/">AIに占ってもらう</a></li><li><a href="/uranai/jibun/">自分で答える（36問）</a></li><li><a href="/en/">縁を占う</a></li></ul></div>
<div><h3>読む</h3><ul><li><a href="/hoshi/">十二の星と六十枚</a></li><li><a href="/kurai/">主の位・癖・ミス</a></li><li><a href="/zukan/">わたしの図鑑</a></li></ul></div>
<div><h3>このサイト</h3><ul><li><a href="/about/">このサイトについて</a></li><li><a href="/privacy/">プライバシー</a></li><li><a href="/kiyaku/">利用規約</a></li></ul></div>
</div>
<div class="copy"><span>© 2026 AIタイプ図鑑</span><span>ChatGPT・Claude・Gemini・Copilot は各社の商標です。本サイトは各社とは関係ありません。</span></div>
</div></footer>`;

const SEO_DESC='いつものAIに呪文を一つ送るだけ。AIがあなたとのやり取りを思い出して、六十枚のカードからあなたの一枚と、主（あるじ）としての位を占います。登録なし・無料・約3分。';

/* ===== トップ ===== */
{
const gallery=HOUSES.map((h,c)=>`<div class="house-col c${c}"><div class="house-h"><i class="dot"></i><b>${h.n}</b><small>${h.d}</small></div><div class="house-cards">${[0,1,2].map(p=>{const t=c*3+p;return `<a class="gcard" href="/hoshi/${pad(t+1)}/">${card(t,[0,3,1,4,2][t%5])}<span><b>${esc(TYPES[t].n)}</b><small>${esc(TYPES[t].star)}</small></span></a>`}).join('')}</div></div>`).join('');
const ladder=RANKS.map((x,i)=>i).reverse().map(i=>`<li class="${i===6?'top':''}"><b>${RANKS[i].r}</b><span>${esc(RANKS[i].n)}</span><small>${esc(RANKS[i].p)}</small></li>`).join('');
const body=`
<section class="hero"><div class="wrap hero-in">
<div class="hero-t">
<span class="eyebrow">AI TYPE TAROT ─ 60 CARDS</span>
<h1>あなたのAIは、<br>あなたを<em>何者</em>だと<br class="sp">思っている？</h1>
<p class="lead">いつものAIに、呪文を一つ送るだけ。AIがあなたとのやり取りを思い出して答え、六十枚のカードから、あなたの一枚が引かれます。そしてもう一枚、AIが主（あるじ）であるあなたにつける「位」も。</p>
<div class="hero-cta"><a class="btn lg" href="/uranai/">無料で占う</a><a class="btn ghost lg" href="/hoshi/">十二の星を見る</a></div>
<ul class="trust"><li>登録なし</li><li>約3分</li><li>AIの答えは、あなたの端末の中だけ</li></ul>
<div id="again" hidden></div>
</div>
<div class="hero-v" aria-hidden="true">
<div class="hv-card l">${card(3,1,{lazy:false})}</div>
<div class="hv-arch"><img src="/img/00_guide.webp" alt="" width="640" height="960"></div>
<div class="hv-card r">${card(8,3,{lazy:false})}</div>
</div>
</div></section>

<section class="stats"><div class="wrap"><dl>
<div><dt>カード</dt><dd>60<small>枚</small></dd></div>
<div><dt>星</dt><dd>12<small>種</small></dd></div>
<div><dt>主の位</dt><dd>7<small>段</small></dd></div>
<div><dt>主の癖</dt><dd>16<small>種</small></dd></div>
<div><dt>占った人</dt><dd><span data-count>―</span><small>人</small></dd></div>
</dl></div></section>

<section class="section" id="how"><div class="wrap">
<div class="sec-head center"><span class="eyebrow">HOW IT WORKS</span><h2>占い方は、三つだけ</h2><p>質問に答えるのは、あなたではなくAIです。あなたをいちばん近くで見てきたAIが、遠慮なく答えます。</p></div>
<ol class="how">
<li><span class="how-n">01</span><h3>呪文を写す</h3><p>ボタンを押すと、AIへの呪文（質問の文）が写されます。</p></li>
<li><span class="how-n">02</span><h3>いつものAIに送る</h3><p>ChatGPT・Claude・Gemini など、いつも使っているAIに貼って送ります。</p></li>
<li><span class="how-n">03</span><h3>答えを貼って、引く</h3><p>AIの答えをこのサイトに貼ると、伏せた五枚からあなたが一枚を引きます。</p></li>
</ol>
<p class="how-ai"><span>使えるAI</span><b>ChatGPT</b><b>Claude</b><b>Gemini</b><b>Copilot</b><small>ほか、会話のできるAIならどれでも</small></p>
</div></section>

<section class="section" id="two"><div class="wrap">
<div class="sec-head center"><span class="eyebrow">TWO CARDS</span><h2>引かれるのは、二枚の札</h2></div>
<div class="two-cards">
<article class="tc"><div class="tc-v">${card(6,2)}</div><div class="tc-t"><span class="eyebrow">THE FIRST CARD</span><h3>第一の札　あなたの星</h3><p>AIをどう使う人か。四つの宮（炎・水・地・風）、十二の星、五つの相がかけ合わさり、六十枚のどれか一枚になります。本質、AIから見たあなた、表と裏の顔、四つの運、今日の託宣まで。</p><a class="more" href="/hoshi/">十二の星を見る →</a></div></article>
<article class="tc"><div class="tc-v"><ol class="mini-ladder">${ladder}</ol></div><div class="tc-t"><span class="eyebrow">THE SECOND CARD</span><h3>第二の札　主の位</h3><p>AIが、主であるあなたの「頼み方」を採点します。七つの位、指示の五つの徳、あなたの癖、AIがいつもミスる場所、そしてAIの本音。お世辞なしで、と念を押してあります。</p><a class="more" href="/kurai/">七つの位を見る →</a></div></article>
</div>
</div></section>

<section class="section" id="stars"><div class="wrap">
<div class="sec-head center"><span class="eyebrow">TWELVE STARS</span><h2>四つの宮と、十二の星</h2><p>「任せるか、一緒にやるか」「作るか、知るか」で宮が決まり、AIとの歩み方で星が決まります。</p></div>
<div class="houses">${gallery}</div>
<p class="center-btn"><a class="btn ghost" href="/hoshi/">六十枚すべてを見る</a></p>
</div></section>

<section class="section" id="get"><div class="wrap">
<div class="sec-head center"><span class="eyebrow">YOUR READING</span><h2>結果で分かること</h2></div>
<ul class="gets">
<li><b>本質</b><span>あなたがAIとどう向き合う人か</span></li>
<li><b>AIから見たあなた</b><span>AIが、口にしなかった事</span></li>
<li><b>表と裏の顔</b><span>人に見せる顔と、見せない顔</span></li>
<li><b>四つの運</b><span>仕事・学び・創作・心</span></li>
<li><b>今日の託宣</b><span>毎日変わる、一行の予言</span></li>
<li><b>主の位</b><span>七つのうちのどれか</span></li>
<li><b>指示の五つの徳</b><span>目的・材料・条件・確かめ・直し方</span></li>
<li><b>主の癖</b><span>十六のうち、AIが選んだ二つ</span></li>
<li><b>AIがミスる場所</b><span>その原因と、写せる直しの一文</span></li>
<li><b>AIの本音</b><span>一度だけ言いたかった事</span></li>
<li><b>縁</b><span>運命の相手・学べる相手・ぶつかる相手</span></li>
<li><b>カードの画像</b><span>保存して、送れる一枚</span></li>
</ul>
</div></section>

<section class="section" id="faq"><div class="wrap narrow">
<div class="sec-head center"><span class="eyebrow">FAQ</span><h2>よくある質問</h2></div>
<div class="faq">
<details><summary>無料ですか？</summary><p>はい、すべて無料です。登録もいりません。</p></details>
<details><summary>どのAIで占えますか？</summary><p>ChatGPT・Claude・Gemini・Copilot など、会話のできるAIならどれでも使えます。あなたとのやり取りを覚えている（メモリーや履歴が入っている）AIほど、よく当たります。</p></details>
<details><summary>AIの答えは、どこかに送られますか？</summary><p>送られません。貼った答えは、あなたのブラウザの中で読み取ります。「何人が占ったか」を数えるために、カードの番号と位とAIの種類だけを、名前なしで数えています。くわしくは<a href="/privacy/">プライバシー</a>をご覧ください。</p></details>
<details><summary>AIが「覚えていない」と言ったら？</summary><p>覚えていない分は、今の会話から推し量って答えます。結果にもそう書かれます。いつも使っている会話（アカウント）で占うと、もっと当たります。</p></details>
<details><summary>AIを使わずに占えますか？</summary><p>できます。<a href="/uranai/jibun/">自分で答える（36問・約5分）</a>から占えます。ただ、AIに答えてもらう方が正直な結果になります。</p></details>
<details><summary>何度でも占えますか？</summary><p>何度でも占えます。頼み方を変えてから占い直すと、主の位が上がることもあります。前回の位との違いも結果に出ます。</p></details>
<details><summary>当たりますか？</summary><p>AIの答えから決まるので、AIがあなたをどう見ているかがそのまま出ます。とはいえ占いは占いです。楽しみと、AIとの付き合い方を見直すきっかけとしてお使いください。</p></details>
</div>
</div></section>

<section class="final"><div class="wrap">
<span class="eyebrow">YOUR CARD IS WAITING</span>
<h2>あなたのAIに、聞いてみませんか。</h2>
<a class="btn lg" href="/uranai/">無料で占う</a>
</div></section>`;
page({file:'index.html',title:'',desc:SEO_DESC,page:'home',body,cur:'',ld:{"@context":"https://schema.org","@type":"WebSite","name":"AIタイプ図鑑","url":SITE+'/',"inLanguage":"ja"}});
}

/* ===== 占う ===== */
{
const AIS=[['ChatGPT','https://chatgpt.com/'],['Claude','https://claude.ai/new'],['Gemini','https://gemini.google.com/app'],['Copilot','https://copilot.microsoft.com/']];
const body=`<div class="wrap">
<header class="page-h"><span class="eyebrow">DIVINATION</span><h1>AIに占ってもらう</h1><p class="lead">呪文を写して、いつものAIに送り、返ってきた答えを貼るだけ。約3分です。</p></header>
<div class="flow">
<ol class="steps">
<li class="step now" id="s1"><div class="step-n"><span>1</span></div><div class="step-b">
<h2>呪文を写す</h2>
<p>AIへの質問の文です。下のボタンで、まるごと写せます。</p>
<button class="btn lg" id="copyPrompt" type="button">呪文を写す</button>
<p class="ok" id="copyOk" hidden>写しました。次は、いつものAIに貼って送ってください。</p>
<p class="err" id="copyNg" hidden>うまく写せませんでした。下の文が選ばれているので、長押し（右クリック）で「コピー」してください。</p>
<details class="pv"><summary>呪文の中身を見る（<span id="promptChars">―</span>文字）</summary><pre id="promptText" tabindex="0"></pre></details>
</div></li>
<li class="step" id="s2"><div class="step-n"><span>2</span></div><div class="step-b">
<h2>いつものAIに送る</h2>
<p>いつも使っているアカウントで、新しいチャットを開いて貼り、送ってください。あなたとのやり取りを覚えているAIほど、よく当たります。</p>
<div class="ai-links">${AIS.map(([n,u])=>`<a href="${u}" target="_blank" rel="noopener">${n}<span aria-hidden="true">↗</span></a>`).join('')}</div>
<p class="note">ほかのAIでも占えます。答えが「【AIタイプ図鑑】」の形で返ってくればだいじょうぶです。</p>
</div></li>
<li class="step" id="s3"><div class="step-n"><span>3</span></div><div class="step-b">
<h2>答えを貼って、カードを引く</h2>
<p>AIの答えを、「【AIタイプ図鑑】」の行から最後まで、まるごと貼ってください。</p>
<label class="sr" for="answer">AIの答え</label>
<textarea id="answer" rows="8" placeholder="【AIタイプ図鑑】&#10;AI：ChatGPT&#10;記憶：多い&#10;答え：4,3,2,…" spellcheck="false" autocomplete="off"></textarea>
<p class="err" id="err" hidden role="alert"></p>
<button class="btn lg" id="judge" type="button">カードを引く</button>
<p class="note">貼った答えは、このブラウザの中で読み取ります。どこにも送りません。</p>
</div></li>
</ol>
<aside class="side">
<div class="panel"><span class="eyebrow">TIPS</span><h2 class="side-h">よく当たる占い方</h2>
<ul class="tips"><li><b>いつものアカウントで</b>メモリーや履歴が入っているほど、AIはあなたを正直に答えます。</li><li><b>新しいチャットで</b>ほかの話の途中に貼ると、その話に引っぱられます。</li><li><b>答えを直さない</b>数字を書きかえると、位も星もずれます。</li><li><b>形がちがう時は</b>AIに「最後の形だけで、もう一度」と送ってください。</li></ul></div>
<div class="panel alt"><h2 class="side-h">AIを使わずに占う</h2><p class="note">36の問いに、あなたが自分で答えます。約5分。</p><a class="btn ghost" href="/uranai/jibun/">自分で答える</a></div>
</aside>
</div>
</div>`;
page({file:'uranai/index.html',title:'AIに占ってもらう',desc:'呪文を写して、いつものAIに送り、答えを貼るだけ。AIがあなたを占い、六十枚のカードから一枚と、主の位が決まります。',page:'uranai',body,cur:'uranai',crumbs:[[null,'占う']]});
}

/* ===== 自分で答える ===== */
page({file:'uranai/jibun/index.html',title:'自分で答える（36問）',desc:'AIを使わずに、36の問いに自分で答えて占います。約5分。',page:'jibun',funnel:true,body:`<div class="wrap narrow quiz">
<div class="q-top"><button class="q-back" id="qBack" type="button" aria-label="ひとつ前の問いへ">← もどる</button><span class="q-num" id="qNum">1 / 36</span></div>
<div class="q-prog" role="progressbar" aria-label="進み具合" aria-valuemin="0" aria-valuemax="36" aria-valuenow="0"><i id="qBar"></i></div>
<div class="q-box" id="qBox" aria-live="polite"></div>
<p class="note center">答えは自動で残るので、途中でやめても続きから始められます。</p>
</div>`});

/* ===== 結果 ===== */
page({file:'kekka/index.html',title:'あなたのカード',desc:'AIが引いた、あなたのカードと主の位。',page:'kekka',body:`<div class="wrap"><div id="kekka" class="kekka"><noscript><p class="lead">結果を出すには JavaScript を有効にしてください。</p></noscript></div></div>`,crumbs:[[null,'結果']],extraHead:''});

/* ===== 十二の星（一覧） ===== */
{
const body=`<div class="wrap">
<header class="page-h"><span class="eyebrow">TWELVE STARS · SIXTY CARDS</span><h1><span class="nw">十二の星と</span><span class="nw">六十枚のカード</span></h1><p class="lead">AIへの頼み方は、二つの問いで四つの宮に分かれます。「任せるか、一緒にやるか」。「作るか、知る・話すか」。そこにAIとの歩み方（即決・反復・長考）が重なって十二の星に、さらに五つの相が重なって六十枚になります。</p></header>
<div class="map">${HOUSES.map((h,c)=>`<a class="map-cell c${c}" href="#h${c}"><i class="dot"></i><b>${h.n}</b><small>${h.d}</small></a>`).join('')}</div>
${HOUSES.map((h,c)=>`<section class="hsec c${c}" id="h${c}"><header class="hsec-h"><span class="eyebrow">HOUSE ${['OF FIRE','OF WATER','OF EARTH','OF WIND'][c]}</span><h2>${h.n}<small>${h.d}</small></h2><p class="prose">${esc(h.lore)}</p></header>
<div class="stars">${[0,1,2].map(p=>{const t=c*3+p,T=TYPES[t];return `<a class="star" href="/hoshi/${pad(t+1)}/"><div class="star-v">${card(t,0)}</div><div class="star-t"><span class="chip"><b>${ROMAN[t]}</b>${esc(T.star)}</span><h3>${esc(T.n)}</h3><p class="alias">〈 ${esc(T.alias)} 〉</p><p>${esc(T.core.split('。').slice(0,2).join('。')+'。')}</p><span class="more">${PACE[p]}・くわしく見る →</span></div></a>`}).join('')}</div></section>`).join('')}
<section class="section tight"><div class="sec-head"><span class="eyebrow">FIVE ASPECTS</span><h2>五つの相</h2><p>同じ星でも、いつ・どんな気持ちでAIに向かうかで、相が変わります。</p></div>
<div class="grid g3 aspects-list">${KI.map((k,i)=>`<div class="panel"><h3>${esc(k.n.replace(/の$/,''))}の相</h3><p class="note">${esc(k.note)}</p><p class="prose">${esc(k.d)}</p></div>`).join('')}</div></section>
</div>`;
page({file:'hoshi/index.html',title:'十二の星と六十枚のカード',desc:'AIへの頼み方で分かれる四つの宮と十二の星、五つの相、六十枚のカードの一覧。',page:'hoshi-list',body,cur:'hoshi',crumbs:[[null,'十二の星']]});
}

/* ===== 星ごとのページ ===== */
TYPES.forEach((T,t)=>{
  const c=camp(t),p=pace(t),H=HOUSES[c],P=pals(t),prev=(t+11)%12,next=(t+1)%12;
  const body=`<div class="wrap">
<section class="st-hero c${c}">
<div class="st-v">${card(t,0,{size:'lg',lazy:false})}</div>
<div class="st-t">
<span class="eyebrow">${ROMAN[t]} · ${['FIRE','WATER','EARTH','WIND'][c]}</span>
<p class="st-star">${esc(T.star)}</p>
<h1>${esc(T.n)}<small>${esc(T.r)}</small></h1>
<p class="k-alias">〈 ${esc(T.alias)} 〉</p>
<dl class="facts"><div><dt>宮</dt><dd><i class="dot"></i>${H.n}（${H.d}）</dd></div><div><dt>歩み</dt><dd>${PACE[p]}（${PACE_D[p]}）</dd></div><div><dt>象徴</dt><dd>${esc(T.sym)}</dd></div><div><dt>口ぐせ</dt><dd>「${esc(T.q)}」</dd></div></dl>
<div class="k-acts"><a class="btn" href="/uranai/">自分の星を占う</a><a class="btn ghost" href="#aspects">五つの相を見る</a></div>
</div>
</section>
<div class="st-body">
<section class="rblock"><header class="rb-h"><span class="eyebrow">ESSENCE</span><h2>本質</h2></header><p class="prose">${esc(T.core)}</p></section>
<section class="rblock"><header class="rb-h"><span class="eyebrow">IN THE EYES OF AI</span><h2>AIから見た${esc(T.n)}</h2></header><p class="prose">${esc(T.ai)}</p></section>
<section class="rblock"><header class="rb-h"><span class="eyebrow">TWO FACES</span><h2>表と裏</h2></header><div class="pair"><div><small>表の顔</small><p>${esc(T.omote)}</p></div><div><small>裏の顔</small><p>${esc(T.ura)}</p></div></div></section>
<section class="rblock"><header class="rb-h"><span class="eyebrow">FORTUNE</span><h2>四つの運</h2></header><div class="lucks">${[['仕','仕事運',T.luck.work],['学','学び運',T.luck.learn],['創','創作運',T.luck.make],['心','心の運',T.luck.heart]].map(([i,n,x])=>`<div class="luck"><i>${i}</i><div><b>${n}</b><p>${esc(x)}</p></div></div>`).join('')}</div></section>
<section class="rblock"><header class="rb-h"><span class="eyebrow">LIGHT &amp; SHADOW</span><h2>才と影</h2></header><div class="pair"><div><small>才</small><p>${esc(T.s)}</p></div><div><small>影</small><p>${esc(T.w)}</p></div></div><h3 class="sub-h">${esc(T.n)}の、よくあること</h3><ul class="aru">${T.aru.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></section>
<section class="rblock"><header class="rb-h"><span class="eyebrow">REVERSED</span><h2>逆位置</h2></header><p class="prose">${esc(T.rev)}</p><p class="note">星の配置が二つの宮の境目にある時、カードは逆さに出ます。</p></section>
<section class="rblock"><header class="rb-h"><span class="eyebrow">KEY TO FORTUNE</span><h2>開運の一手</h2></header><p class="prose">${esc(T.t)}</p><div class="fix"><div class="fix-t"><small>${esc(T.n)}に効く呪文（AIへの一言）</small><p>「${esc(T.spell)}」</p></div></div></section>
<section class="rblock" id="aspects"><header class="rb-h"><span class="eyebrow">FIVE ASPECTS</span><h2>五つの相</h2></header><div class="aspects">${[0,1,2,3,4].map(k=>{const [a,l]=CH[t*5+k];return `<article class="aspect">${card(t,k,{size:'sm'})}<div><h3>${esc(full(t,k))}</h3><p class="alias">〈 ${esc(a)} 〉</p><p>${esc(l)}</p><span class="met-tag">出会ったカード</span></div></article>`}).join('')}</div></section>
<section class="rblock"><header class="rb-h"><span class="eyebrow">BONDS</span><h2>縁のある星</h2></header><div class="pals">${[['運命の相手',P.best],['学べる相手',P.learn],['ぶつかる相手',P.clash]].map(([l,x])=>`<a class="pal" href="/hoshi/${pad(x+1)}/"><small>${l}</small>${card(x,0,{size:'sm'})}<span>${esc(TYPES[x].n)}｜${esc(TYPES[x].star)}</span></a>`).join('')}</div></section>
</div>
<nav class="pn" aria-label="ほかの星"><a href="/hoshi/${pad(prev+1)}/"><small>← ${ROMAN[prev]}</small>${esc(TYPES[prev].n)}</a><a href="/hoshi/">十二の星</a><a href="/hoshi/${pad(next+1)}/"><small>${ROMAN[next]} →</small>${esc(TYPES[next].n)}</a></nav>
<section class="final in"><span class="eyebrow">ARE YOU THE ${esc(['GENERAL','DIRECTOR','ARCHITECT','DETECTIVE','DISCIPLE','LIBRARIAN','INVENTOR','ARTISAN','STORYTELLER','TRAVELER','ADVISOR','PHILOSOPHER'][t])}?</span><h2>あなたのAIは、あなたを${esc(T.n)}だと思っている？</h2><a class="btn lg" href="/uranai/">無料で占う</a></section>
</div>`;
  page({file:`hoshi/${pad(t+1)}/index.html`,title:`${T.n}（${T.star}）`,desc:`${T.n}｜${T.star}〈${T.alias}〉。${first(T.core)}本質・AIから見た姿・四つの運・五つの相。`,page:'hoshi',data:{t},body,cur:'hoshi',og:`/og/${pad(t+1)}-1.jpg`,crumbs:[['/hoshi/','十二の星'],[null,T.n]],
    ld:{"@context":"https://schema.org","@type":"Article","headline":`${T.n}（${T.star}）`,"description":first(T.core),"image":SITE+`/og/${pad(t+1)}-1.jpg`,"inLanguage":"ja","publisher":{"@type":"Organization","name":"AIタイプ図鑑"}}});
});

/* ===== 主の位 ===== */
{
const body=`<div class="wrap">
<header class="page-h"><span class="eyebrow">THE SECOND CARD</span><h1>主の位</h1><p class="lead">AIは、頼む人の言葉だけを手がかりに動きます。だから、答えのよしあしの半分は「主（あるじ）」の頼み方で決まります。第二の札は、あなたのAIがあなたにつける、主としての位です。</p></header>
<section class="section tight"><div class="sec-head"><span class="eyebrow">SEVEN RANKS</span><h2>七つの位</h2><p>AIへの15の問いから、指示の五つの徳を点にします。最上の位は、五つの徳がすべてそろった人だけです。</p></div>
<div class="ranks">${RANKS.map((x,i)=>i).reverse().map(i=>{const R=RANKS[i];return `<article class="rank r${i}"><div class="seal sm r${i}" aria-hidden="true"><span class="ring"></span><b>${R.r}</b></div><div><h3>${esc(R.n)}<small>${esc(R.p)}</small></h3><p>${esc(R.d)}</p><blockquote>${esc(R.ai)}</blockquote></div></article>`}).join('')}</div></section>
<section class="section tight"><div class="sec-head"><span class="eyebrow">FIVE VIRTUES</span><h2>指示の五つの徳</h2><p>いちばん弱い徳に、写せる一文を一つ足すだけで、AIの答えは目に見えて変わります。</p></div>
<div class="grid g2 virtue-list">${VIRT.map(v=>`<article class="panel vt"><div class="vt-h"><i>${esc(v.k)}</i><div><span class="eyebrow">${esc(v.lat)}</span><h3>${esc(v.n)}</h3><small>${esc(v.d)}</small></div></div><p class="note"><b>強い人：</b>${esc(v.hi)}</p><p class="note"><b>弱い人：</b>${esc(v.lo)}</p><div class="fix"><div class="fix-t"><small>足す一文</small><p>「${esc(v.fix)}」</p></div></div></article>`).join('')}</div></section>
<section class="section tight"><div class="sec-head"><span class="eyebrow">SIXTEEN HABITS</span><h2>主の十六の癖</h2><p>占うと、このうち二つをあなたのAIが選びます。</p></div>
<div class="grid g2 kuse-all">${KUSE.map((k,i)=>`<article class="kuse"><header><span class="eyebrow">No.${pad(i+1)}</span><h3>${esc(k.n)}</h3><small>${esc(k.p)}</small></header><p class="kuse-ai">${esc(k.ai)}</p><div class="fix"><div class="fix-t"><small>この癖を消す一文</small><p>「${esc(k.cure)}」</p></div></div></article>`).join('')}</div></section>
<section class="section tight"><div class="sec-head"><span class="eyebrow">WHERE AI FALLS</span><h2>AIがミスる十二の場所</h2><p>AIのミスの多くは、頼み方に原因があります。</p></div>
<div class="miss-table" role="table" aria-label="AIがミスる十二の場所"><div class="mt-row mt-h" role="row"><span role="columnheader">場所</span><span role="columnheader">よくある形</span><span role="columnheader">なぜ起きるか</span></div>${MISS.map(m=>`<div class="mt-row" role="row"><b role="cell">${esc(m.n)}</b><span role="cell">${esc(m.sign)}</span><span role="cell">${esc(m.why)}<em>効く徳：${esc(VIRT[m.v].n)}</em></span></div>`).join('')}</div></section>
<section class="final in"><span class="eyebrow">WHAT IS YOUR RANK?</span><h2>あなたは、何の位？</h2><a class="btn lg" href="/uranai/">無料で占う</a></section>
</div>`;
page({file:'kurai/index.html',title:'主の位・五つの徳・十六の癖',desc:'AIがあなたの頼み方を採点する「主の位」。七つの位、指示の五つの徳、十六の癖、AIがミスる十二の場所と直し方。',page:'kurai',body,cur:'kurai',crumbs:[[null,'主の位']]});
}

/* ===== 縁 ===== */
page({file:'en/index.html',title:'縁を占う',desc:'ふたりの星の符号を入れると、AIの使い方から見たふたりの縁が分かります。',page:'en',cur:'en',crumbs:[[null,'縁']],body:`<div class="wrap narrow">
<header class="page-h"><span class="eyebrow">BOND</span><h1>縁を占う</h1><p class="lead">結果ページの「縁」にある星の符号（AI- から始まる文字）を、ふたり分入れてください。</p></header>
<div class="panel en-form">
<label for="codeA">あなたの符号</label><input id="codeA" inputmode="latin" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="AI-XXXXXXX">
<label for="codeB">相手の符号</label><input id="codeB" inputmode="latin" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="AI-XXXXXXX">
<p class="err" id="enErr" hidden role="alert"></p>
<button class="btn lg" id="enGo" type="button">縁を占う</button>
<p class="note" id="enMine" hidden>まだ自分の符号がない方は、<a href="/uranai/">先に占ってください</a>。</p>
</div>
<div class="panel en-out" id="enOut" hidden aria-live="polite"></div>
<section class="section tight"><div class="sec-head"><span class="eyebrow">SIX BONDS</span><h2>六つの縁</h2></div>
<dl class="bonds"><div><dt>双星</dt><dd>同じ星の二人。通じ合うが、同じ所でつまずく。</dd></div><div><dt>師と弟子</dt><dd>同じ宮で、歩く速さだけが違う二人。</dd></div><div><dt>運命の対</dt><dd>頼み方も使い道も正反対で、歩みだけが同じ。めったに出会えない。</dd></div><div><dt>相剋</dt><dd>速さが合わずぶつかる。ぶつかる所に火花が散る。</dd></div><div><dt>同じ歩幅</dt><dd>歩く速さが同じで、見ている景色が違う二人。</dd></div><div><dt>月と潮</dt><dd>近すぎず遠すぎず、満ち引きを分け合う二人。</dd></div></dl></section>
</div>`});

/* ===== 図鑑 ===== */
page({file:'zukan/index.html',title:'わたしの図鑑',desc:'あなたが出会った六十枚のカードと、みんなの占いの結果。',page:'zukan',cur:'zukan',crumbs:[[null,'図鑑']],body:`<div class="wrap">
<header class="page-h"><span class="eyebrow">YOUR COLLECTION</span><h1>わたしの図鑑</h1><p class="lead">自分で引いたカードと、縁を占った相手のカードが、ここに集まります。</p>
<div class="met"><div class="met-n"><b id="metN">0</b><small>/ 60 枚</small></div><div class="met-bar"><i id="metBar"></i></div></div></header>
<div class="dex-tabs" id="dexTabs" role="group" aria-label="宮で絞る"></div>
<div class="dex" id="dex"></div>
<section class="panel hist" id="hist" hidden><h2 class="side-h">これまでの占い</h2><ul id="histList"></ul></section>
<section class="section tight"><div class="sec-head"><span class="eyebrow">EVERYONE</span><h2>みんなの占い</h2></div>
<div class="grid g3 everyone">
<div class="panel"><h3>生まれた星</h3><p class="note" id="popNote">占った人が増えると表れます。</p><div id="pop"></div></div>
<div class="panel"><h3>主の位の分かれ方</h3><p class="note">AIに占わせた人の位（10人から）</p><div id="rkDist"><p class="note">占った人が増えると表れます。</p></div></div>
<div class="panel"><h3>主に厳しいAI</h3><p class="note" id="aiNote">どのAIが主に厳しいかは、占った人が増えると表れます。</p><div id="aiCmp"></div></div>
</div></section>
</div>`});

/* ===== このサイトについて・プライバシー・規約 ===== */
page({file:'about/index.html',title:'このサイトについて',desc:'AIタイプ図鑑の仕組みと、占いの決まり方。',page:'about',crumbs:[[null,'このサイトについて']],body:`<div class="wrap narrow doc">
<header class="page-h"><span class="eyebrow">ABOUT</span><h1>このサイトについて</h1></header>
<h2>AIタイプ図鑑とは</h2><p>あなたがふだん使っているAIに、あなた自身を占ってもらうサイトです。AIは、あなたとのやり取りを思い出しながら35の問いに答え、その答えから、六十枚のカードのうちの一枚と、主（あるじ）としての位が決まります。</p>
<h2>カードの決まり方</h2><p>はじめの20の問いで、「任せるか、一緒にやるか」「作るか、知る・話すか」の二つの軸と、AIとの歩み方（即決・反復・長考）、相（月夜・疾風・祈り・流星・誓約）を出します。二つの軸で四つの宮が、歩み方で十二の星が、相で六十枚のカードが決まります。二つの軸のどちらかが真ん中に近い時は、カードが逆位置で出ます。</p>
<h2>主の位の決まり方</h2><p>あとの15の問いは、目的・材料・条件・確かめ・直し方の「指示の五つの徳」を3問ずつ聞いています。五つの徳の平均が主の点（100点満点）になり、点に応じて七つの位のどれかになります。最上の「星詠みの主」は、五つの徳がすべて70点以上の人だけです。AIには「ふつうの使い手を3とし、お世辞は禁止」と念を押しています。</p>
<h2>楽しみ方の注意</h2><p>AIの答えは、聞くたびに少し変わることがあります。結果は占いとして、また、AIとの付き合い方を見直すきっかけとしてお楽しみください。仕事や健康などの大事な判断には使わないでください。</p>
<h2>AIの名前について</h2><p>ChatGPT・Claude・Gemini・Copilot は、それぞれの会社の商標です。本サイトは、どの会社とも関係のない、独立したサイトです。</p>
</div>`});
page({file:'privacy/index.html',title:'プライバシー',desc:'AIタイプ図鑑で扱うデータについて。',page:'privacy',crumbs:[[null,'プライバシー']],body:`<div class="wrap narrow doc">
<header class="page-h"><span class="eyebrow">PRIVACY</span><h1>プライバシー</h1><p class="note">2026年11月15日</p></header>
<h2>貼ったAIの答え</h2><p>あなたが貼ったAIの答えは、あなたのブラウザの中だけで読み取ります。サーバーには送りません。AIの「ひとこと」「本音」「場面」も、あなたの端末の中にだけ残ります。</p>
<h2>端末に残すもの</h2><p>前回の結果、出会ったカード、自分で答えている途中の答えを、ブラウザの保存領域（localStorage）に残します。ブラウザのサイトデータを消すと、すべて消えます。</p>
<h2>数えているもの</h2><p>「何人が占ったか」「どの星が多いか」「どのAIが厳しいか」を表すために、占うたびに次のものだけを、名前や端末の情報と結びつけずに数えています：カードの番号、主の位と主の点、AIの種類（ChatGPT など）。</p>
<h2>共有のリンク</h2><p>「結果を送る」で作るリンクには、カードと主の位を表す符号が入ります。AIの「ひとこと」と「本音」は入りません。</p>
<h2>外のサービス</h2><p>文字の形（フォント）に Google Fonts を使っています。サイトは Cloudflare の上で動いています。どちらも、ページを届けるために、ふつうのアクセスの記録を扱います。広告や、行動を追いかける仕組みは使っていません。</p>
</div>`});
page({file:'kiyaku/index.html',title:'利用規約',desc:'AIタイプ図鑑の利用規約。',page:'kiyaku',crumbs:[[null,'利用規約']],body:`<div class="wrap narrow doc">
<header class="page-h"><span class="eyebrow">TERMS</span><h1>利用規約</h1><p class="note">2026年11月15日</p></header>
<h2>1. このサイトの使い方</h2><p>AIタイプ図鑑（以下「本サイト」）は、無料で、登録なしで使えます。本サイトを使った時点で、この規約に同意したものとします。</p>
<h2>2. 結果について</h2><p>結果は、あなたのAIの答えから決まる占いです。内容の正しさや、何かに役立つことは約束しません。大事な判断には使わないでください。</p>
<h2>3. AIの使い方</h2><p>AIに呪文を送る時は、そのAIの利用規約に従ってください。人の名前や連絡先など、知られたくない事は送らないでください。</p>
<h2>4. カードの絵と文</h2><p>本サイトの絵と文の権利は本サイトにあります。結果の画像やリンクを、SNS などで個人として送ることは自由です。絵や文をそのまま別のサービスや販売に使うことはお断りします。</p>
<h2>5. してはいけない事</h2><p>本サイトの動きを妨げる事、数を不正にふやす事、ほかの人を困らせる事はしないでください。</p>
<h2>6. 変更</h2><p>本サイトの中身とこの規約は、予告なく変わることがあります。</p>
</div>`});

/* ===== 共有リンク（カードごとの OGP） ===== */
for(let t=0;t<12;t++)for(let k=0;k<5;k++){
  const [a,l]=CH[t*5+k];
  page({file:`s/${pad(t+1)}-${k+1}/index.html`,title:`${full(t,k)}〈${a}〉`,desc:`${l} ── あなたのAIは、あなたを何だと思ってる？`,page:'share',og:`/og/${pad(t+1)}-${k+1}.jpg`,funnel:'bare',
    body:`<div class="wrap narrow center s-wrap">${card(t,k,{lazy:false})}<p class="lead">カードを開いています…</p><p><a class="btn" href="/kekka/">結果を開く</a></p></div>`});
}

/* ===== 404 ===== */
page({file:'404.html',title:'ページが見つかりません',desc:'ページが見つかりません。',page:'404',body:`<div class="wrap narrow center nf"><span class="eyebrow">404 · LOST STAR</span><h1>この星は、まだ見つかっていません</h1><p class="lead">ページが動いたか、アドレスがちがうようです。</p><p class="center-btn"><a class="btn" href="/">トップへ</a><a class="btn ghost" href="/hoshi/">十二の星を見る</a></p></div>`});

/* ===== sitemap・robots・headers ===== */
const urls=['','uranai/','uranai/jibun/','hoshi/',...TYPES.map((_,t)=>`hoshi/${pad(t+1)}/`),'kurai/','en/','zukan/','about/','privacy/','kiyaku/'];
fs.writeFileSync(path.join(OUT,'sitemap.xml'),`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map(u=>`<url><loc>${SITE}/${u}</loc></url>`).join('\n')}\n</urlset>\n`);
fs.writeFileSync(path.join(OUT,'robots.txt'),NOINDEX?`User-agent: *\nDisallow: /\n`:`User-agent: *\nDisallow: /kekka/\nDisallow: /s/\nAllow: /\nSitemap: ${SITE}/sitemap.xml\n`);
fs.writeFileSync(path.join(OUT,'_headers'),`/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n${NOINDEX?'  X-Robots-Tag: noindex\n':''}\n/assets/*\n  Cache-Control: public, max-age=86400\n/img/*\n  Cache-Control: public, max-age=2592000, immutable\n/og/*\n  Cache-Control: public, max-age=604800\n`);
fs.writeFileSync(path.join(OUT,'favicon.svg'),LOGO.replace('<svg ','<svg xmlns="http://www.w3.org/2000/svg" ').replace('aria-hidden="true"','').replace('<circle cx="16" cy="16" r="14.5"','<rect width="32" height="32" rx="7" fill="#07070F"/><circle cx="16" cy="16" r="14.5"'));
console.log('built',SITE,NOINDEX?'(noindex)':'(public)');
