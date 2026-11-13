import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { createTools } from '../lib/plugin/tools.js'

class T {
  map = new Map()
  get(key) { return this.map.get(key) }
  entries() { return this.map.entries() }
  get size() { return this.map.size }
  async put(key, value) { this.map.set(key, value) }
}

test('public MIT NDA file in an EML envelope', async () => {
  const body = readFileSync('fixtures/public/mit/sample_nda.txt', 'utf8')
  const eml = `Subject: NDA review request\nFrom: sample@example.com\nDate: 2026-03-01\nMessage-ID: <public-nda@example.com>\n\n${body}`
  const tools = createTools({ requests: new T(), baseDir: '/tmp/legal-public' })
  const intake = tools.find((tool) => tool.name === 'legal_intake')
  const result = await intake.execute({ messages: [{ eml_text: eml }] }, { callId: 'public-nda' })
  assert.equal(result.requests.length, 1)
  assert.equal(result.types.NDA, 1)
})
