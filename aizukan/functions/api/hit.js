import {load,pub,json,jst,CAP,AIS} from '../../lib/stats.js';
const int=(v,lo,hi)=>Number.isInteger(v)&&v>=lo&&v<=hi;
export async function onRequestPost({request,env}){
  let b;try{b=await request.json()}catch{return json({ok:false},400)}
  if(!b||!int(b.t,0,11)||!int(b.k,0,4)||!(b.rk===-1||int(b.rk,0,6))||!(b.o===-1||int(b.o,0,100)))return json({ok:false},400);
  const ai=AIS.includes(b.ai)?b.ai:'その他';
  const a=await load(env);if(!a)return json({ok:false},503);
  const d=jst();if(a.day!==d){a.day=d;a.dn=0}
  if(a.dn>=CAP)return json({ok:true,capped:true});
  a.dn++;a.n++;a.t[b.t]++;a.tk[b.t*5+b.k]++;
  if(b.rk>=0)a.rk[b.rk]++;
  if(b.o>=0){a.hist[b.o]++;const x=a.ai[ai]||[0,0];x[0]+=b.o;x[1]++;a.ai[ai]=x}
  try{await env.AIZ.put('agg',JSON.stringify(a))}catch{return json({ok:false},503)}
  return json({ok:true,n:a.n});
}
export const onRequestGet=()=>json({ok:false},405);
