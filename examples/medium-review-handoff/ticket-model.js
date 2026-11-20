/* Shared local simulator, not a production service or persistence contract.
   Both product and review pages call this one implementation. */
(function(global){
"use strict";
function readStored(storage,key,initial){
 const raw=storage.getItem(key);
 if(raw===null)return initial();
 const data=JSON.parse(raw);
 if(!data||!Array.isArray(data.orders)||!Array.isArray(data.audit)||data.orders.length!==2||new Set(data.orders.map(x=>x.id)).size!==2||!data.orders.every(x=>['001','002'].includes(x.id)&&['pending','assigned','closed'].includes(x.status)&&Number.isInteger(x.version)))throw new Error('本地工单数据不可读取');
 return data;
}
function request(database,cmd,saveDatabase){
 const action=cmd.action;
 const candidate=JSON.parse(JSON.stringify(database));
 const row=candidate.orders.find(x=>x.id===cmd.id);
 const reject=message=>({ok:false,message});
 if(!row)return reject('工单不存在');
 if(action==='assign'){
  if(cmd.actor!=='dispatcher')return reject('仅调度员可指派');
  if(row.status!=='pending')return reject('当前状态不能指派');
 }else if(action==='complete'){
  if(cmd.actor!==row.assignee)return reject('仅被指派维修员可完成');
  if(row.status!=='assigned')return reject('当前状态不能完成');
 }else return reject('未支持的业务动作');
 if(cmd.version!==row.version)return reject('工单已更新，请刷新后重试');
 const note=String(cmd.note||'').trim();
 if(action==='complete'&&(!note||[...note].length>100))return reject(!note?'请填写完成说明':'完成说明不能超过 100 个字符');
 // All guards precede all mutations. This local mock is not an atomic
 // transaction across tabs; production must supply real concurrency control.
 if(action==='assign'){row.assignee='lin';row.status='assigned'}else{row.note=note;row.status='closed'}
 row.version++;candidate.audit.push({order:row.id,actor:cmd.actor,action,time:new Date().toISOString(),version:row.version});
 if(!saveDatabase(candidate))return reject('保存失败，未提交本次变更；输入已保留，请恢复存储后重试。');
 return {ok:true,message:action==='assign'?'指派成功':'工单已完成'};
}
 global.RepairExample=Object.freeze({request,readStored});
})(globalThis);
