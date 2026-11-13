import test from 'node:test'
import assert from 'node:assert/strict'
import { createTools } from '../lib/plugin/tools.js'

class T { map = new Map(); get(k){return this.map.get(k)}; entries(){return this.map.entries()}; get size(){return this.map.size}; async put(k,v){this.map.set(k,v)} }
const tools = Object.fromEntries(createTools({ requests: new T(), baseDir: '/tmp/legal-doctor' }).map((t) => [t.name, t]))
const exec = { callId: 'doctor' }
const eml = (subject, mid, thread) => `Subject: ${subject}\r\nFrom: a@example.test\r\nMessage-ID: ${mid}\r\nThread-Id: ${thread}\r\n\r\nBody text.`

test('duplicate attachment name and zero-byte attachment are reported', async () => {
  const r = await tools['legal_intake_doctor'].execute({ messages: [{ eml_text: eml('NDA', '<m1>', '<t1>'), attachments: [{ name: 'nda.pdf', sha256: 'a'.repeat(64), size: 10 }, { name: 'nda.pdf', sha256: 'b'.repeat(64), size: 0 }] }] }, exec)
  assert.equal(r.messages, 1)
  assert.ok(r.issues.some((i) => i.code === 'E_LEGAL_ATTACHMENT_DUPLICATE'))
  assert.ok(r.issues.some((i) => i.code === 'E_LEGAL_ATTACHMENT_EMPTY'))
})

test('repeated Message-ID and repeated thread are reported', async () => {
  const r = await tools['legal_intake_doctor'].execute({ messages: [{ eml_text: eml('NDA', '<m1>', '<t1>') }, { eml_text: eml('NDA follow-up', '<m1>', '<t1>') }] }, exec)
  assert.ok(r.issues.some((i) => i.code === 'E_LEGAL_MESSAGE_DUPLICATE'))
  assert.ok(r.issues.some((i) => i.code === 'E_LEGAL_THREAD_REPEATED'))
})

test('a malformed message is reported instead of throwing', async () => {
  const r = await tools['legal_intake_doctor'].execute({ messages: [{ eml_text: 'no headers here' }] }, exec)
  assert.equal(r.messages, 1)
  assert.ok(r.issues.some((i) => i.code === 'E_LEGAL_EML_INVALID'))
})

test('a clean batch has no issues', async () => {
  const r = await tools['legal_intake_doctor'].execute({ messages: [{ eml_text: eml('NDA', '<m1>', '<t1>'), attachments: [{ name: 'nda.pdf', sha256: 'c'.repeat(64), size: 12 }] }] }, exec)
  assert.equal(r.issues.length, 0)
})
