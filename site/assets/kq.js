/* 11/3 くらべたおかいものリストの「聞く」欄。
   オーナー「みんな使いやすく、このAIに調べさせたら楽だと」→ 入れた言葉で、燈が毎日比べたカードを全部のタブから探して出す。
   その場でAIが考えるのではない（お金がかからない）。無い物は /c に記録して、次の日に燈が比べる。 */
(function(){
  var qi=document.getElementById("kq"),qr=document.getElementById("kqr"),od=document.getElementById("odekake"),box=document.querySelector(".kq");
  if(!qi||!qr||!od||!box)return;
  var F="";try{F=sessionStorage.getItem("f")||"";}catch(e){}
  var AMZ=box.dataset.amz||"",YH=box.dataset.yh||"",qt=0,last="";
  function nz(x){return (x||"").normalize("NFKC").toLowerCase().replace(/[\s　]/g,"")
    .replace(/[ァ-ヶ]/g,function(c){return String.fromCharCode(c.charCodeAt(0)-96);});}
  function esc(x){return x.replace(/[<>&"']/g,function(c){return "&#"+c.charCodeAt(0)+";";});}
  function ask(v,log){
    var q=nz(v);qr.innerHTML="";if(typeof mark==="function")mark(q?v:"");
    if(!q){qr.hidden=true;od.classList.remove("kqon");document.body.classList.remove("kqon2");return;}
    /* 11/5 オーナー「動作に使いにくさがある、操作を考えろ」→ 言い方がちがっても出す（トイペ・洗濯・オムツ など）。
       それでも無ければ、後ろから1字ずつ短くして近い物を出す（「トイレットペーパー12ロール」→「トイレットペーパー」） */
    var SY={"といぺ":"といれっとぺーぱー","ぺーぱー":"といれっとぺーぱー","てぃっしゅ":"てぃっしゅ","せんたく":"洗剤","せんざい":"洗剤","じゅうなん":"柔軟剤",
      "こめ":"米","おこめ":"米","みず":"水","おちゃ":"茶","こーひー":"こーひー","でんち":"電池","おむつ":"おむつ","おしりふき":"おしりふき","ますく":"ますく",
      "ごみぶくろ":"ごみ","ごみ袋":"ごみ","しゃんぷー":"しゃんぷー","ぼでぃそーぷ":"ぼでぃ","はみがき":"歯磨","ふるさと":"ふるさと","ふるさとのうぜい":"ふるさと"};
    function find(w){var r=[];["unit","pick","down","sale"].forEach(function(t){
      document.querySelectorAll('#odekake .pane[data-t="'+t+'"] .card.it').forEach(function(c){
        if(r.indexOf(c)<0&&nz(c.textContent+" "+(c.dataset.pref||"")).indexOf(w)>=0)r.push(c);});});
      /* うさぎの結論（いちばん上の比べた物の一覧）も探す。見えているのに「まだ比べていません」と出ていたため */
      document.querySelectorAll("details.kpr").forEach(function(c){if(c.closest("#kqr"))return;var sm=c.querySelector("summary");
        if(r.indexOf(c)<0&&nz(sm?sm.textContent:c.textContent).indexOf(w)>=0)r.push(c);});return r;}
    var hit=find(q),near="";
    if(!hit.length&&SY[q]){hit=find(nz(SY[q]));}
    for(var cut=q.length-1;!hit.length&&cut>=2;cut--){var w=q.slice(0,cut);hit=find(w);if(hit.length)near=w;}
    /* その種類そのもの（「水」なら種類が水の物）を先に。炭酸水などの「水」を含む物はあと */
    hit=hit.filter(function(c){return nz(c.dataset.pref)===q;}).concat(hit.filter(function(c){return nz(c.dataset.pref)!==q;}));
    od.classList.add("kqon");document.body.classList.add("kqon2");qr.hidden=false;
    var sh=esc(v.slice(0,30));
    if(hit.length){
      var h=document.createElement("p");h.className="kqt";
      h.innerHTML="「"+sh+"」の答え　"+hit.length+"件"+(near?"（近い物）":"")+"<small>うさぎが送料込み・1個あたりで比べた中から出しています</small>";
      qr.appendChild(h);
      /* ひと目でわかる差：同じ物差し（1Lあたり など）の上位5つを棒で並べる。文字を読まなくても差が見える */
      var rows=[],lab="";
      hit.forEach(function(c){var b=c.querySelector(".kv b"),l=c.querySelector(".kvl"),u=c.querySelector(".kvu");if(!b||!l)return;
        var v=parseFloat(b.textContent.replace(/[^\d.]/g,""));if(!(v>0))return;var L=l.textContent.trim()+"|"+(u?u.textContent.trim():"");
        if(!lab)lab=L;if(L===lab)rows.push({v:v,c:c,u:u?u.textContent.trim():""});});
      rows.sort(function(a,b){return a.v-b.v;});rows=rows.slice(0,5);
      if(rows.length>=3){var mx=Math.max.apply(null,rows.map(function(r){return r.v;})),g=document.createElement("div");g.className="kqg";
        g.innerHTML='<p>'+esc(lab.split("|")[0])+'の値段（短いほど安い）</p>'+rows.map(function(r,i){
          var im=r.c.querySelector(".kp img");
          return '<div class="kqr'+(i===0?" b":"")+'">'+(im?'<img src="'+im.getAttribute("src")+'" alt="" referrerpolicy="no-referrer">':'<i></i>')
            +'<span><em style="width:'+Math.max(8,Math.round(r.v/mx*100))+'%"></em></span><b>'+r.v+'<small>'+esc(r.u)+'</small></b></div>';}).join("");
        qr.appendChild(g);}
      hit.slice(0,12).forEach(function(c,i){var k=c.cloneNode(true);k.hidden=false;k.removeAttribute("id");k.style.display="";if(k.tagName==="DETAILS"&&i===0)k.open=true;
        if(i===0){var b=document.createElement("p");b.className="kqb";b.textContent="うさぎの答え　いちばんお得なのはこれ";qr.appendChild(b);k.classList.add("kq1");}
        qr.appendChild(k);});
      /* 賢い誘導：セール中なら、買う前のエントリーを答えのすぐ下に（押し忘れるとポイントが付かない） */
      var en=document.querySelector('a.ilk[rel~="sponsored"]');
      if(en){var w=document.createElement("div");w.className="kqe";w.innerHTML='<small>買う前に、これだけ</small>';var a=en.cloneNode(true);w.appendChild(a);qr.appendChild(w);}
    }else{
      var e=encodeURIComponent(v.slice(0,40)),n=document.createElement("div");n.className="kqn";
      n.innerHTML="「"+sh+"」は、まだ比べていません。<br>聞かれた物は記録して、うさぎが近いうちに比べてここに足します。<br>"
        +(AMZ?'<a href="https://www.amazon.co.jp/s?k='+e+'&tag='+encodeURIComponent(AMZ)+'" rel="sponsored noopener" target="_blank">Amazonで探す ›</a>':"")
        +(YH?'<a href="'+YH+encodeURIComponent("https://shopping.yahoo.co.jp/search?p="+e)+'" rel="sponsored noopener" target="_blank">Yahoo!で探す ›</a>':"");
      qr.appendChild(n);
    }
    var x=document.createElement("button");x.type="button";x.className="kqx";x.textContent="はじめの画面にもどる";
    x.onclick=function(){qi.value="";ask("");scrollTo({top:box.getBoundingClientRect().top+scrollY-70,behavior:"smooth"});};qr.appendChild(x);
    if(log&&q!==last&&navigator.sendBeacon){last=q;
      try{navigator.sendBeacon("/c?f="+encodeURIComponent(F||"direct")+"&s=okai-ask&k="+encodeURIComponent((hit.length?"有｜":"無｜")+v.slice(0,24)));}catch(e){}}
  }
  /* 11/3 オーナー「項目ごとに切り替えにして。下に行ったり上に行ったり使いにくい」→ 答えの上に種類の切り替え（横に流せる列）を貼り付け、
     押すとその場で中身だけ入れ替える。上のタイルまで戻らなくていい */
  var sst=document.createElement("style");sst.textContent=".kqsw{position:sticky;top:0;z-index:20;display:flex;gap:6px;overflow-x:auto;background:#fff;padding:8px 0;margin-bottom:6px;scrollbar-width:none;box-shadow:0 1px 0 #ECECEC}.kqsw::-webkit-scrollbar{display:none}.kqsw[hidden]{display:none}.kqsw button{flex:0 0 auto;display:flex;align-items:center;gap:5px;border:1px solid #DADADA;background:#fff;border-radius:99px;padding:4px 12px 4px 4px;font-size:12.5px;color:#333;white-space:nowrap}.kqsw button img{width:24px;height:24px;border-radius:50%;object-fit:contain;background:#F5F5F7;mix-blend-mode:multiply}.kqsw button.on{background:#1A1A1A;border-color:#1A1A1A;color:#fff}.kqsw button.on img{mix-blend-mode:normal;background:#fff}";document.head.appendChild(sst);
  var bar=document.createElement("nav");bar.className="kqsw";bar.setAttribute("aria-label","種類の切り替え");bar.hidden=true;
  box.querySelectorAll(".kqc button[data-q]").forEach(function(t){var c=document.createElement("button");c.type="button";c.dataset.q=t.dataset.q;
    var im=t.querySelector("img");c.innerHTML=(im?'<img src="'+im.getAttribute("src")+'" alt="" referrerpolicy="no-referrer">':"")+"<span>"+esc(t.dataset.q)+"</span>";
    c.addEventListener("click",function(){qi.value=c.dataset.q;ask(c.dataset.q,true);top();});bar.appendChild(c);});
  qr.parentNode.insertBefore(bar,qr);
  function mark(v){var on=null;bar.querySelectorAll("button").forEach(function(c){var y=nz(c.dataset.q)===nz(v);c.classList.toggle("on",y);if(y)on=c;});
    bar.hidden=!v;if(on)bar.scrollTo({left:on.offsetLeft-(bar.clientWidth-on.offsetWidth)/2,behavior:"smooth"});}
  function top(){var r=qr.getBoundingClientRect().top-bar.offsetHeight-4;if(r<0||r>innerHeight*0.5)scrollTo({top:r+scrollY,behavior:"smooth"});}
  function go(){var r=(bar.hidden?box:bar).getBoundingClientRect().top+scrollY-6;scrollTo({top:r,behavior:"smooth"});}
  /* 結論の行を押した時も、その種類の切り替え画面へ */
  document.addEventListener("click",function(ev){var a=ev.target.closest&&ev.target.closest(".kcon a[data-p]");if(!a)return;ev.preventDefault();ev.stopImmediatePropagation();
    var q=a.dataset.p;qi.value=q;ask(q,true);go();},true);
  qi.addEventListener("input",function(){clearTimeout(qt);var v=qi.value;qt=setTimeout(function(){ask(v,false);},200);});
  box.querySelector("form").addEventListener("submit",function(ev){ev.preventDefault();ask(qi.value,true);qi.blur();go();});
  var mo=box.querySelector(".kqmore");if(mo)mo.addEventListener("click",function(){box.querySelector(".kqc").classList.add("op");});
  box.querySelectorAll(".kqc button[data-q]").forEach(function(b){b.addEventListener("click",function(){qi.value=b.dataset.q;ask(b.dataset.q,true);go();});});
  qi.addEventListener("change",function(){if(qi.value)ask(qi.value,true);});
})();
