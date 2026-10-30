import{defineDomain,domainTable}from'@deepseek-ai/dsh-storage-domain';import type{Context}from'@deepseek-ai/cordis';import{z}from'zod'
const request=z.object({request_id:z.string(),message_id:z.string(),thread_id:z.string(),subject:z.string(),from:z.string(),received_at:z.string(),request_type:z.string(),status:z.enum(['new','triaged']),attachment_count:z.number(),created_at:z.string()})
export type RequestRecord=z.infer<typeof request>;export type Table<T>={get(k:string):T|undefined;entries():IterableIterator<[string,T]>;size:number;put(k:string,v:T):Promise<void>}
export const legalSpec=defineDomain({name:'legal',version:1,tables:{requests:domainTable<string,RequestRecord>(request)}})
export async function openLegal(ctx:Context){const d=await ctx.storageDomain.open(legalSpec);ctx.effect(()=>()=>d.close(),'dsh-legal-intake.domainClose');return d.table('requests') as Table<RequestRecord>}
