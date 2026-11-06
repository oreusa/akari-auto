/* 11/7 近くの宿：泊まる日と人数を選んで、楽天トラベルの「その日の空室・料金」へ（夜の調査：日付が引き継がれず選び直しになっていた）。
   宿の一覧（.ykl）を開いたとき、上に「泊まる日・大人」を出し、宿のリンクをその日の空室一覧（hotelinfo/plan）に替える。紹介リンク（hb.afl）はそのまま。 */
(function(){
if(window.__ydate)return;window.__ydate=1;
var st=document.createElement("style");
st.textContent=".ykl .yd{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;padding:10px 4px 8px;font-size:12.5px;color:#5E544D;border-bottom:1px solid #ECECEC}"+
".ykl .yd label{display:flex;align-items:center;gap:6px}.ykl .yd input,.ykl .yd select{font:inherit;font-size:14px;padding:5px 6px;border:1px solid #D9D9D9;border-radius:8px;background:#fff;color:#2B2622}"+
".ykl .yd .nt{flex-basis:100%;font-size:11px;color:#8C7B6E}";
document.head.appendChild(st);
function p2(n){return(n<10?"0":"")+n}
function iso(d){return d.getFullYear()+"-"+p2(d.getMonth()+1)+"-"+p2(d.getDate())}
function today(){var d=new Date();d.setHours(0,0,0,0);return d}
function pd(s){var m=/^(\d{4})-(\d\d)-(\d\d)$/.exec(s||"");return m?new Date(+m[1],+m[2]-1,+m[3]):null}
/* 初めの泊まる日：1日だけの催しはその日。期間の催しは、期間の中の次の土曜（なければ今日）。 */
function first(c){var t=today(),s=pd(c&&c.dataset.s),e=pd(c&&c.dataset.e);
if(s&&e&&+s===+e&&s>=t)return s;
var a=s&&s>t?s:t,sat=new Date(a);sat.setDate(a.getDate()+((6-a.getDay()+7)%7));
if(!e||sat<=e)return sat;return a}
function cardOf(u){if(u._c)return u._c;var p=u.previousElementSibling;for(var i=0;p&&i<3;i++,p=p.previousElementSibling){if(p._c)return p._c;if(p.matches&&p.matches("a.card"))return p;var q=p.querySelector&&p.querySelector("a.card");if(q)return q;}return null}
function plan(fno,d,n){var o=new Date(d);o.setDate(o.getDate()+1);
return "https://hotel.travel.rakuten.co.jp/hotelinfo/plan/"+fno+"?f_nen1="+d.getFullYear()+"&f_tuki1="+(d.getMonth()+1)+"&f_hi1="+d.getDate()+"&f_nen2="+o.getFullYear()+"&f_tuki2="+(o.getMonth()+1)+"&f_hi2="+o.getDate()+"&f_otona_su="+n+"&f_heya_su=1"}
function fix(u){var d=pd(u._yd.value),n=+u._yn.value||2;if(!d)return;
u.querySelectorAll('a[href*="hb.afl.rakuten.co.jp"]').forEach(function(a){
if(!a.dataset.o)a.dataset.o=a.href;var o=a.dataset.o,m=/[?&]pc=([^&]+)/.exec(o);if(!m)return;
var pc=decodeURIComponent(m[1]),f=/f_no=(\d+)/.exec(pc);if(!f)return;
a.href=o.replace(m[1],encodeURIComponent(plan(f[1],d,n)));});}
function add(u){if(u._yd||!u.querySelector('a[href*="hb.afl.rakuten.co.jp"]'))return;
var c=cardOf(u),d=first(c),li=document.createElement("li");li.className="yd";
var l1=document.createElement("label");l1.textContent="泊まる日";var i=document.createElement("input");i.type="date";i.value=iso(d);i.min=iso(today());l1.appendChild(i);
var l2=document.createElement("label");l2.textContent="大人";var s=document.createElement("select");[1,2,3,4].forEach(function(k){var o=document.createElement("option");o.value=k;o.textContent=k+"人";if(k===2)o.selected=true;s.appendChild(o);});l2.appendChild(s);
var nt=document.createElement("span");nt.className="nt";nt.textContent="押すと、楽天トラベルでこの日の空室と料金が出ます。〜円は参考の最安料金で、この日の料金ではありません。";
li.appendChild(l1);li.appendChild(l2);li.appendChild(nt);
li.addEventListener("click",function(e){e.stopPropagation();});
u.insertBefore(li,u.firstChild);u._yd=i;u._yn=s;
i.addEventListener("change",function(){fix(u)});s.addEventListener("change",function(){fix(u)});fix(u);}
function scan(){document.querySelectorAll("ul.ykl").forEach(add)}
document.addEventListener("click",function(){setTimeout(scan,150)},true);
window.addEventListener("load",function(){setTimeout(scan,1200)});
})();
