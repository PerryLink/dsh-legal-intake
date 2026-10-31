# dsh-legal-intake

Legal request intake from EML, Message-ID/thread dedupe and ledger export for DeepSeek Harness.

> **Status: alpha / public-synthetic / partial / not counted / not GA.** No customer evidence, customer data, or production-readiness claim. All acceptance rows are `counted=false`.

## Install

```sh
dsh plugin --profile <profile> add dsh-legal-intake
dsh --profile <profile> --dump-config | grep dsh-legal-intake
```

Requires DSH `>=0.2.1-rc.3 <0.3.0` and Node `>=24.9 <25`.

<details>
<summary>中文摘要</summary>

法务需求 EML 收件、线程去重与台账导出。 安装：`dsh plugin --profile <profile> add dsh-legal-intake`。公开/合成、alpha、非 GA。

</details>

## Tools

| Tool | What it does | Risk |
|---|---|---|
| `legal.intake` | Parse an EML request, classify request type, dedupe by Message-ID/thread | R1 local write |
| `legal.export_ledger` | Export the request ledger as xlsx | R1 local write |

## Input / output

**Input:** an EML request file. **Output:** a classified request record and an xlsx ledger. Dedupe uses Message-ID/thread; it does not read a live mailbox.

## Configuration

| Env | Default | Meaning |
|---|---|---|
| `DSH_LEGAL_HOME` | `$DSH_HOME/storages/dsh-legal-intake` | local domain and exports |

## Limits / non-claims

- No Graph/mailbox connection, OCR, assignment workflow, CLM integration, or Client surface.
- No live mailbox sync; intake is file-level EML only.
- MIT NDA EML sample only; no customer mailbox or privileged material.
- No customer evidence, customer data, or production-readiness claim; all fixtures are public/synthetic.

## Public sample

MIT NDA EML envelope; `ACCEPTANCE.csv` lists 4 public checks.

## Development

```sh
pnpm install --frozen-lockfile
pnpm build && pnpm lint && pnpm typecheck && pnpm test && pnpm gate:sku09
```

## License

Apache-2.0. See `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES`.
