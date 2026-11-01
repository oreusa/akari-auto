/* トップ（11/2 オーナー「全部本番に」で本番）：3つの入口（いま行ける・地図・イルミネーション）を題名のすぐ下に。タブの言葉を初めての人にも分かる言葉に */
(function(){
var I={now:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1" fill="#3A2F28"/><path d="M12 12l6-6"/></svg>',
map:'<svg viewBox="0 0 24 24"><path d="M12 21s-6-5.3-6-10a6 6 0 0 1 12 0c0 4.7-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/></svg>',
il:'<svg viewBox="0 0 24 24"><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/><circle cx="12" cy="12" r="2.5"/></svg>'};
function go(){
  var h=document.querySelector(".head");if(!h||document.querySelector(".qk"))return;
  var il=document.querySelector("a.ilk[href*='illumination']"),ilt=il?il.textContent.replace("→","").trim():"";
  var q=document.createElement("nav");q.className="qk";q.setAttribute("aria-label","さがし方");
  q.innerHTML='<a href="ima" data-k="入口｜いま行ける">'+I.now+'<b>いま行ける</b><small>近い順に</small></a>'+
    '<a href="#" data-a="map" data-k="入口｜地図">'+I.map+'<b>地図で見る</b><small>場所から探す</small></a>'+
    (il?'<a href="'+il.getAttribute("href")+'" data-k="入口｜イルミ">'+I.il+'<b class="ln">イルミネーション</b><small>'+(/関東/.test(ilt)?"関東":"関西")+'の日程</small></a>':'');
  var hd=h.closest("header")||h;hd.parentNode.insertBefore(q,hd.nextSibling);var sb=document.getElementById("sale");if(sb)q.parentNode.insertBefore(sb,q.nextSibling);
  q.querySelector('[data-a="map"]').addEventListener("click",function(e){e.preventDefault();var m=document.querySelector(".tnbtn");if(m)m.click();});
  /* タブ：もうすぐ → 開業予定、できた → 最近開業（初めての人にも何のことか分かる言葉） */
  document.querySelectorAll(".tabs button b,.otab button").forEach(function(b){[].forEach.call(b.childNodes,function(t){if(t.nodeType!==3)return;
    if(t.nodeValue.trim()==="もうすぐ")t.nodeValue="開業予定";else if(t.nodeValue.trim()==="できた")t.nodeValue="最近開業";});});
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",function(){setTimeout(go,0)});else setTimeout(go,0);
})();
