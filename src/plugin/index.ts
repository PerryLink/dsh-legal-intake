import path from'node:path';import type{Context}from'@deepseek-ai/cordis';import{createTools}from'./tools.js';import{openLegal}from'./storage.js'
export const name='dsh-legal-intake';export const inject=['tools','storageDomain']
export async function apply(ctx:Context):Promise<void>{const baseDir=process.env.DSH_LEGAL_HOME??path.join(process.env.DSH_HOME??process.cwd(),'storages','dsh-legal-intake');const requests=await openLegal(ctx);for(const t of createTools({requests,baseDir}))ctx.tools.register(t)}
