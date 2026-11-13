#!/usr/bin/env node
/**
 * dsh-legal-intake quickstart — runs the built tools over the bundled synthetic EML
 * batch. `expected/result.json` is the stdout of `node samples/quickstart/run.mjs --json`,
 * so it is a real run over the shipped sample, not hand-written output.
 *
 *   node samples/quickstart/run.mjs            # human-readable summary
 *   node samples/quickstart/run.mjs --json     # the golden result on stdout
 *   node samples/quickstart/run.mjs --check    # recompute and diff against the golden file
 *
 * Everything is local and synthetic: no mailbox, no network, no real person or customer.
 */
import assert from 'node:assert/strict'
import { mkdtemp, readFile, readdir, rm } from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { createTools } from '../../lib/plugin/tools.js'

const here = path.dirname(fileURLToPath(import.meta.url))
const inputDir = path.join(here, 'input')
const expectedPath = path.join(here, 'expected', 'result.json')
const mode = process.argv.includes('--check') ? 'check' : process.argv.includes('--json') ? 'json' : 'summary'

class MemoryTable {
  map = new Map()
  get(key) { return this.map.get(key) }
  entries() { return this.map.entries() }
  get size() { return this.map.size }
  async put(key, value) { this.map.set(key, value) }
}

async function run() {
  const entries = await readdir(inputDir, { withFileTypes: true })
  const emlFiles = entries.filter((entry) => entry.isFile() && entry.name.endsWith('.eml')).map((entry) => entry.name).sort()
  const manifest = JSON.parse(await readFile(path.join(inputDir, 'attachments.json'), 'utf8'))
  const messages = []
  for (const file of emlFiles) {
    messages.push({
      eml_text: await readFile(path.join(inputDir, file), 'utf8'),
      attachments: manifest.messages[file] ?? [],
    })
  }

  const baseDir = await mkdtemp(path.join(os.tmpdir(), 'dsh-legal-intake-quickstart-'))
  try {
    const tools = Object.fromEntries(createTools({ requests: new MemoryTable(), baseDir }).map((tool) => [tool.name, tool]))
    const call = (name, args) => tools[name].execute(args, { callId: 'quickstart' })

    const doctor = await call('legal_intake_doctor', { messages })
    const intake = await call('legal_intake', { messages })
    const ledger = await call('legal_export_ledger', {})

    return {
      sample: 'samples/quickstart/input',
      synthetic: true,
      messages_read: messages.length,
      new_requests: intake.requests.length,
      duplicates: intake.duplicates.length,
      request_types: Object.fromEntries(Object.entries(intake.types).sort(([a], [b]) => a.localeCompare(b))),
      doctor_issue_codes: doctor.issues.map((issue) => issue.code),
      ledger: { rows: ledger.rows, file: path.basename(ledger.path) },
      request_ids: intake.requests,
    }
  } finally {
    await rm(baseDir, { recursive: true, force: true })
  }
}

const result = await run()

if (mode === 'json') {
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`)
} else if (mode === 'check') {
  const expected = JSON.parse(await readFile(expectedPath, 'utf8'))
  assert.deepEqual(result, expected)
  console.log('dsh-legal-intake quickstart - synthetic EML batch (not a real mailbox)')
  console.log(`messages ${result.messages_read}: ${result.new_requests} new requests, ${result.duplicates} duplicate suppressed`)
  console.log(`request types: ${Object.entries(result.request_types).map(([type, count]) => `${type}=${count}`).join(', ')}`)
  console.log(`doctor issues: ${result.doctor_issue_codes.length}`)
  for (const code of result.doctor_issue_codes) console.log(`  - ${code}`)
  console.log(`ledger ${result.ledger.file}: ${result.ledger.rows} rows`)
  console.log('golden samples/quickstart/expected/result.json matches')
  console.log('quickstart ok')
} else {
  console.log('dsh-legal-intake quickstart - synthetic EML batch (not a real mailbox)')
  console.log(`messages ${result.messages_read}: ${result.new_requests} new requests, ${result.duplicates} duplicate suppressed`)
  console.log(`request types: ${Object.entries(result.request_types).map(([type, count]) => `${type}=${count}`).join(', ')}`)
  console.log(`doctor issues: ${result.doctor_issue_codes.length}`)
  for (const code of result.doctor_issue_codes) console.log(`  - ${code}`)
  console.log(`ledger ${result.ledger.file}: ${result.ledger.rows} rows`)
}
