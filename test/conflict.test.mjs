import test from 'node:test'
import assert from 'node:assert/strict'
import { createTools } from '../lib/plugin/tools.js'

class T { map = new Map(); get(k){return this.map.get(k)}; entries(){return this.map.entries()}; get size(){return this.map.size}; async put(k,v){this.map.set(k,v)} }
const tools = Object.fromEntries(createTools({ requests: new T(), baseDir: '/tmp/legal-conflict' }).map((t) => [t.name, t]))
const exec = { callId: 'conflict' }

test('a party adverse in an existing matter conflicts with a new client', async () => {
  const r = await tools['legal.conflict_check'].execute({
    new_parties: [{ name: 'Acme  Trading', role: 'client' }],
    existing: [{ matter_id: 'M-1', parties: [{ name: 'acme trading', role: 'adverse' }] }],
  }, exec)
  assert.equal(r.conflicts.length, 1)
  assert.equal(r.conflicts[0].matter_id, 'M-1')
  assert.equal(r.conflicts[0].reason, 'opposing_sides')
})

test('the same side is not a conflict', async () => {
  const r = await tools['legal.conflict_check'].execute({
    new_parties: [{ name: 'Acme', role: 'client' }],
    existing: [{ matter_id: 'M-2', parties: [{ name: 'ACME', role: 'client' }] }],
  }, exec)
  assert.deepEqual(r.conflicts, [])
})

test('a party listed on both sides of the new matter is an issue', async () => {
  const r = await tools['legal.conflict_check'].execute({
    new_parties: [{ name: 'Beta Ltd', role: 'client' }, { name: 'Beta Ltd', role: 'adverse' }],
    existing: [],
  }, exec)
  assert.ok(r.issues.some((i) => i.startsWith('E_LEGAL_PARTY_BOTH_SIDES')))
})

test('unrelated existing matters produce no conflicts', async () => {
  const r = await tools['legal.conflict_check'].execute({
    new_parties: [{ name: 'Gamma', role: 'adverse' }],
    existing: [{ matter_id: 'M-3', parties: [{ name: 'Delta', role: 'client' }] }],
  }, exec)
  assert.equal(r.conflicts.length, 0)
})
