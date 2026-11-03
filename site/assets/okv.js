/* 11/3 オーナー「バーの方の項目が使いにくい。項目ごとに切り替えにして。下に行ったり上に行ったり使いにくい」
   → 下のバー（くらべた物・1個あたり・値下がり・セール）を押したら、その項目だけの画面に切り替える。
   上の見出し・聞く欄・結論などは隠し、ページのいちばん上から始める。種類のしぼりこみは上に貼り付く。
   「はじめの画面」で元に戻る。 */
(function(){
  if(document.body.dataset.bar!=="okai")return;
  var st=document.createElement("style");
  st.textContent=".okv-hide{display:none!important}"
    +"body.okv .v2tabs,body.okv #odekake>.otab{display:none!important}"
    +"body.okv .flt[data-v=odekake]{position:sticky;top:0;z-index:20;background:#fff;padding:10px 0 8px;box-shadow:0 1px 0 #ECECEC}"
    +"#okvh{display:none;align-items:center;gap:12px;padding:18px 2px 10px}"
    +"body.okv #okvh{display:flex}"
    +"#okvh b{font-size:19px;letter-spacing:.06em;color:#1A1A1A}#okvh b small{margin-left:8px;font:500 12px Jost,sans-serif;color:#6B6B6B;letter-spacing:0}"
    +"#okvh button{border:1px solid #DADADA;background:#fff;border-radius:99px;padding:7px 13px;font-size:12px;color:#333}";
  document.head.appendChild(st);
  var hidden=[],cur="";
  function anchor(){return document.querySelector(".v2tabs")||document.querySelector("#odekake .otab");}
  function head(){var h=document.getElementById("okvh");if(h)return h;var a=anchor();if(!a)return null;
    h=document.createElement("div");h.id="okvh";h.innerHTML='<button type="button">‹ はじめの画面</button><b></b>';
    h.querySelector("button").addEventListener("click",off);a.parentNode.insertBefore(h,a);return h;}
  function fixed(e){try{var p=getComputedStyle(e).position;return p==="fixed";}catch(x){return false;}}
  function on(t){var a=anchor();if(!a)return;var h=head();
    /* 聞く欄で探していたら消す（答えの画面と重ならないように） */
    var q=document.getElementById("kq");if(q&&q.value){q.value="";q.dispatchEvent(new Event("input"));}
    if(!document.body.classList.contains("okv")){
      for(var e=h;e&&e!==document.body;e=e.parentElement){
        for(var s=e.previousElementSibling;s;s=s.previousElementSibling){
          if(/^(SCRIPT|STYLE|LINK)$/.test(s.tagName)||s.id==="v2bar"||fixed(s)||s.classList.contains("okv-hide"))continue;
          s.classList.add("okv-hide");hidden.push(s);}}
      document.body.classList.add("okv");}
    var b=document.querySelector('.otab button[data-t="'+t+'"]');
    var lb=b&&b.childNodes[1]?b.childNodes[1].textContent:"";var n=b&&b.querySelector("small")?b.querySelector("small").textContent:"";
    h.querySelector("b").innerHTML="";h.querySelector("b").appendChild(document.createTextNode(lb));
    /* 1個あたりは種類が多いので、「すべて」のままなら最初の種類から見せる（全部並べると長すぎる） */
    if(t==="unit")setTimeout(function(){var al=document.querySelector('.flt button[data-p=""]');if(al&&al.classList.contains("on")){
      var f=[].slice.call(document.querySelectorAll('.flt button[data-p]')).filter(function(x){return x.dataset.p&&!x.classList.contains("hid");})[0];if(f)f.click();}
      scrollTo(0,0);},150);
    cur=t;scrollTo(0,0);}
  function off(){hidden.forEach(function(s){s.classList.remove("okv-hide");});hidden=[];document.body.classList.remove("okv");cur="";
    var bar=document.getElementById("v2bar");if(bar)bar.querySelectorAll("button[data-t]").forEach(function(b){b.classList.remove("cur");});
    scrollTo(0,0);}
  document.addEventListener("click",function(ev){var b=ev.target.closest&&ev.target.closest("#v2bar button[data-t]");if(!b)return;
    var t=b.dataset.t;setTimeout(function(){on(t);},0);setTimeout(function(){scrollTo(0,0);},60);},true);
  /* はじめは「はじめの画面」なので、下のバーはどれも選ばれていない形に */
  setTimeout(function(){var bar=document.getElementById("v2bar");if(bar&&!cur)bar.querySelectorAll("button[data-t]").forEach(function(b){b.classList.remove("cur");});},300);
})();
