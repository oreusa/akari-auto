/* 11/20 見た目の見本（look.css）：A は後ろの光のにじみ、どれも流すとふわっと出る */
(function(){var H=document.documentElement;if(!H.classList.contains("lk"))return;
function go(){if(H.classList.contains("lk-a")&&!document.querySelector(".lk-bg")){var b=document.createElement("div");b.className="lk-bg";b.setAttribute("aria-hidden","true");b.innerHTML="<i></i><i></i><i></i><i></i><b></b>";document.body.insertBefore(b,document.body.firstChild)}
 if(matchMedia("(prefers-reduced-motion:reduce)").matches||!("IntersectionObserver" in window))return;
 var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add("in");io.unobserve(e.target)}})},{rootMargin:"0px 0px -6% 0px"});
 var seen=new WeakSet();function scan(){[].forEach.call(document.querySelectorAll(".mc,.go,.go2,.yh,.ls,.tb,.cmpt,.faq,.qr,.qr-h,.tiles,.rk li,.sec>h2,.dq"),function(el){if(seen.has(el))return;seen.add(el);var r=el.getBoundingClientRect();if(r.top<innerHeight*.92)return;el.classList.add("rv");io.observe(el)})}
 scan();new MutationObserver(function(){scan()}).observe(document.body,{childList:true,subtree:true})}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",function(){setTimeout(go,60)});else setTimeout(go,60)})();
