// みんなの数：KV の1つのキー（agg）に集める。KVの書き込みは無料で1日1,000回をアカウント全体で分け合うので、ここは1日150回で止める
export const CAP=150;
export const AIS=['ChatGPT','Claude','Gemini','Copilot','Perplexity','Grok','その他','自分'];
export const empty=()=>({n:0,t:Array(12).fill(0),tk:Array(60).fill(0),rk:Array(7).fill(0),hist:Array(101).fill(0),ai:{},day:'',dn:0});
export const jst=()=>new Date(Date.now()+9*3600e3).toISOString().slice(0,10);
export async function load(env){if(!env.AIZ)return null;try{const v=await env.AIZ.get('agg',{type:'json'});return v&&typeof v.n==='number'?v:empty()}catch{return empty()}}
export const pub=a=>({n:a.n,t:a.t,tk:a.tk,rk:a.rk,hist:a.hist,ai:a.ai});
export const json=(o,s=200,h={})=>new Response(JSON.stringify(o),{status:s,headers:{'content-type':'application/json; charset=utf-8',...h}});
