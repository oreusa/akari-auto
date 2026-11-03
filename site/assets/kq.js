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
    var q=nz(v);qr.innerHTML="";
    if(!q){qr.hidden=true;od.classList.remove("kqon");document.body.classList.remove("kqon2");return;}
    var hit=[];
    ["unit","pick","down","sale"].forEach(function(t){
      document.querySelectorAll('#odekake .pane[data-t="'+t+'"] .card.it').forEach(function(c){
        if(nz(c.textContent+" "+(c.dataset.pref||"")).indexOf(q)>=0)hit.push(c);});});
    od.classList.add("kqon");document.body.classList.add("kqon2");qr.hidden=false;
    var sh=esc(v.slice(0,30));
    if(hit.length){
      var h=document.createElement("p");h.className="kqt";
      h.innerHTML="「"+sh+"」の答え　"+hit.length+"件<small>うさぎが送料込み・1個あたりで比べた中から出しています</small>";
      qr.appendChild(h);
      hit.slice(0,12).forEach(function(c,i){var k=c.cloneNode(true);k.hidden=false;k.removeAttribute("id");k.style.display="";
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
    var x=document.createElement("button");x.type="button";x.className="kqx";x.textContent="ほかの物も見る（言葉を消す）";
    x.onclick=function(){qi.value="";ask("");scrollTo({top:box.getBoundingClientRect().top+scrollY-70,behavior:"smooth"});};qr.appendChild(x);
    if(log&&q!==last&&navigator.sendBeacon){last=q;
      try{navigator.sendBeacon("/c?f="+encodeURIComponent(F||"direct")+"&s=okai-ask&k="+encodeURIComponent((hit.length?"有｜":"無｜")+v.slice(0,24)));}catch(e){}}
  }
  function go(){var r=qr.getBoundingClientRect().top+scrollY-70;scrollTo({top:r,behavior:"smooth"});}
  qi.addEventListener("input",function(){clearTimeout(qt);var v=qi.value;qt=setTimeout(function(){ask(v,false);},200);});
  box.querySelector("form").addEventListener("submit",function(ev){ev.preventDefault();ask(qi.value,true);qi.blur();go();});
  box.querySelectorAll(".kqc button").forEach(function(b){b.addEventListener("click",function(){qi.value=b.dataset.q;ask(b.dataset.q,true);go();});});
  qi.addEventListener("change",function(){if(qi.value)ask(qi.value,true);});
})();
