import{createHash}from'node:crypto';import{mkdtemp,readFile,rm}from'node:fs/promises';import{mkdirSync,writeFileSync}from'node:fs';import os from'node:os';import path from'node:path';import * as XLSX from'xlsx';import{createTools}from'../lib/plugin/tools.js'
class T{map=new Map();get(k){return this.map.get(k)};entries(){return this.map.entries()};get size(){return this.map.size};async put(k,v){this.map.set(k,v)}}
const eml=(n)=>`Subject: ${n%11===0?'MSA':'NDA'} request ${n}\nFrom: user${n}@example.com\nDate: 2026-01-01\nMessage-ID: <m${n}@x>\n\nPlease review ${n}.`
const d=await mkdtemp(path.join(os.tmpdir(),'legal-acc-')),root=process.cwd(),run=`sku09-${Date.now()}`,ev=path.join(root,'evidence',run);mkdirSync(ev,{recursive:true});let newRows=0,dups=0,ledger=0,sheets=0
try{const ts=createTools({requests:new T(),baseDir:path.join(d,'s')});const b=Object.fromEntries(ts.map(t=>[t.name,t]));const msgs=Array.from({length:50},(_,i)=>({eml_text:eml(i)}));const r=await b['legal.intake'].execute({messages:[...msgs,...msgs.slice(0,5)]},{callId:'a'});newRows=r.requests.length;dups=r.duplicates.length;const l=await b['legal.export_ledger'].execute({},{callId:'a'});ledger=l.rows;sheets=XLSX.read(await readFile(l.path),{type:'buffer'}).SheetNames.length}finally{await rm(d,{recursive:true,force:true})}
const docTools=createTools({requests:new T(),baseDir:'/tmp/legal-doctor-acc'});const db=Object.fromEntries(docTools.map(t=>[t.name,t]));const doc=await db['legal.intake_doctor'].execute({messages:[{eml_text:'Subject: NDA\r\nFrom: a@example.test\r\nMessage-ID: <m1>\r\nThread-Id: <t1>\r\n\r\nBody',attachments:[{name:'nda.pdf',sha256:'a'.repeat(64),size:10},{name:'nda.pdf',sha256:'b'.repeat(64),size:0}]}]},{callId:'a'});const conf=await db['legal.conflict_check'].execute({new_parties:[{name:'Acme',role:'client'}],existing:[{matter_id:'M-9',parties:[{name:'acme',role:'adverse'}]}]},{callId:'a'});const ms=[{i:'SKU-09-A01',m:'邮件入库（50）',t:'50/50',a:newRows,p:newRows===50},{i:'SKU-09-A02',m:'线程/Message-ID 去重',t:'5/5',a:dups,p:dups===5},{i:'SKU-09-A03',m:'台账行',t:'50',a:ledger,p:ledger===50},{i:'SKU-09-A04',m:'台账 sheet',t:'1',a:sheets,p:sheets===1},{i:'SKU-09-A05',m:'入库前 EML 体检',t:'2',a:doc.issues.length,p:doc.issues.some(x=>x.code==='E_LEGAL_ATTACHMENT_DUPLICATE')&&doc.issues.some(x=>x.code==='E_LEGAL_ATTACHMENT_EMPTY')},{i:'SKU-09-A06',m:'冲突预检',t:'1',a:conf.conflicts.length,p:conf.conflicts.length===1&&conf.conflicts[0].reason==='opposing_sides'}];const r={run_id:run,scope:'SKU-09-S1',status:'partial',counted:false,note:'synthetic EML; user-approved public/synthetic; 0 real mailboxes',metrics:ms,pass:ms.every(x=>x.p)};const s=JSON.stringify(r,null,2)+'\n';writeFileSync(path.join(ev,'result.json'),s);const h=createHash('sha256').update(s).digest('hex');writeFileSync(path.join(root,'ACCEPTANCE.csv'),'req_id,metric,threshold,actual,script,evidence_sha256,pass\n'+ms.map(x=>`${x.i},${x.m},${x.t},${x.a},scripts/acceptance.mjs,${h},${x.p}`).join('\n')+'\n');if(!r.pass)process.exit(1);console.log('acceptance ok',run)


// Normalize the public-only acceptance schema: source + counted=false.
{
  const fs = await import('node:fs')
  const file = 'ACCEPTANCE.csv'
  const lines = fs.readFileSync(file, 'utf8').trim().split('\n')
  if (!lines[0].includes('source,counted')) {
    lines[0] += ',source,counted'
    for (let i = 1; i < lines.length; i += 1) lines[i] += ',public/synthetic,false'
    fs.writeFileSync(file, lines.join('\n') + '\n')
  }
}
