import {load,pub,json} from '../../lib/stats.js';
export async function onRequestGet({env}){
  const a=await load(env);
  if(!a)return json({error:'no store'},503,{'cache-control':'no-store'});
  return json(pub(a),200,{'cache-control':'public, max-age=60'});
}
