<div align="center">

# dsh-legal-intake

> **Repositório oficial.** O único repositório oficial deste pacote, mantido por PerryLink. Repositórios com o mesmo nome em outras contas não são afiliados. Apache-2.0.

[![npm](https://img.shields.io/npm/v/dsh-legal-intake)](https://www.npmjs.com/package/dsh-legal-intake)
[![CI](https://github.com/PerryLink/dsh-legal-intake/actions/workflows/ci.yml/badge.svg)](https://github.com/PerryLink/dsh-legal-intake/actions)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![dsh-plugin](https://img.shields.io/badge/dsh--plugin-%E2%9C%93-green)](https://github.com/topics/dsh-plugin)
[![docs](https://img.shields.io/badge/docs-domain%20index-0b5fff)](https://perrylink.github.io/dsh-plugins/)
[![Gitee](https://img.shields.io/badge/Gitee-aggregate-c71d23?logo=gitee)](https://gitee.com/perrylink/dsh-plugins)
[![dshfind](https://dshfind.com/api/badge/PerryLink/dsh-legal-intake?metric=downloads)](https://dshfind.com/plugins/PerryLink/dsh-legal-intake?ref=badge)
[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)
[![Node](https://img.shields.io/badge/node-24.9%2B-brightgreen)](#)
[![npm downloads](https://img.shields.io/npm/dm/dsh-legal-intake)](https://www.npmjs.com/package/dsh-legal-intake)

**Recepção de solicitações jurídicas de EML, deduplicação de threads e exportação de registro.**

> **Status: alpha / sintético público / parcial / não contabilizado / não GA.** Sem evidência de clientes, dados de clientes ou promessa de produção.

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

```sh
dsh plugin --profile <profile> add dsh-legal-intake
```

</div>

> ⭐ Se isso ajudar, uma estrela facilita a próxima pessoa encontrar. Nada fica bloqueado por ela.

![Workflow diagram for dsh-legal-intake: local input, plugin, local output.](docs/assets/dsh-legal-intake-flow.svg)

*Fluxo: entrada local → plugin → saída local. Não exige chamada a modelo.*

## Instalação

Instalar e verificar:

```sh
dsh plugin --profile <profile> add dsh-legal-intake
dsh --profile <profile> --dump-config | grep dsh-legal-intake
```

Desinstalar:

```sh
dsh plugin --profile <profile> remove dsh-legal-intake
```

## O que faz

Recepção de solicitações jurídicas de EML, deduplicação de threads e exportação de registro. Executa localmente no DeepSeek Harness. A tabela abaixo é a superfície exata de ferramentas; os exemplos usam a interface real.

Entrada e saída permanecem locais; nada é enviado.

## Ferramentas

Nomes e descrições de ferramentas ficam em inglês para corresponder à saída runtime.

| Ferramenta | Finalidade (em inglês) | Risco |
|---|---|---|
| `legal.intake` | Parse an EML request, classify request type, dedupe by Message-ID/thread | R1 local write |
| `legal.export_ledger` | Export the request ledger as xlsx | R1 local write |

## Início rápido

```sh
dsh plugin --profile <profile> add dsh-legal-intake
dsh --profile <profile> --dump-config | grep dsh-legal-intake
```

## Limites

- Apenas público/sintético; sem dados ou evidência de clientes.
- Alpha/parcial, não contabilizado, sem GA ou promessa de produção.
- Sem modelo ou rede, a menos que uma ferramenta indique.
- Os limites exatos estão na tabela e em `ACCEPTANCE.csv`.

## Amostra pública

As fixtures públicas/sintéticas ficam em `test/fixtures/`; `ACCEPTANCE.csv` registra as verificações com `counted=false`.

## Desenvolvimento

```sh
pnpm install --frozen-lockfile
pnpm build && pnpm lint && pnpm typecheck && pnpm test
```

## Compatibilidade

| Superfície | Status |
|---|---|
| Harness | `dsh >=0.2.1-rc.3 <0.3.0` |
| Node | `>=24.9.0 <25` |
| Platforms | All; local files only |
| Dados | No network, no model call, no upload |

## Permissões e dados

- Executa localmente; sem rede, sem modelo, sem upload.
- Apenas fixtures públicas/sintéticas; sem dados ou evidência de clientes.
- Alpha/parcial; não contabilizado, sem GA ou promessa de produção.
- Pacotes congelados continuam instaláveis; sem novos recursos, apenas falhas reais.

## Trabalho relacionado

Pacotes irmãos e índices da família: [dsh-legal-clause](https://github.com/PerryLink/dsh-legal-clause) · [dsh-contract-suite](https://github.com/PerryLink/dsh-contract-suite)

- [Índice de domínio](https://perrylink.github.io/dsh-plugins/)
- [Família de checkers](https://perrylink.github.io/zh/checkers/)
- [Família principal](https://github.com/PerryLink/dsh-kit)

## Família

<details>
<summary>Família de plugins DSH (15 pacotes + 2 suites)</summary>

| Package | npm |
|---|---|
| **[dsh-einvoice](https://github.com/PerryLink/dsh-einvoice)** | [npm](https://www.npmjs.com/package/dsh-einvoice) |
| **[dsh-docx-redline](https://github.com/PerryLink/dsh-docx-redline)** | [npm](https://www.npmjs.com/package/dsh-docx-redline) |
| **[dsh-policy-ledger](https://github.com/PerryLink/dsh-policy-ledger)** | [npm](https://www.npmjs.com/package/dsh-policy-ledger) |
| **[dsh-ghg](https://github.com/PerryLink/dsh-ghg)** | [npm](https://www.npmjs.com/package/dsh-ghg) |
| **[dsh-bankrec](https://github.com/PerryLink/dsh-bankrec)** | [npm](https://www.npmjs.com/package/dsh-bankrec) |
| **[dsh-ap-three-way](https://github.com/PerryLink/dsh-ap-three-way)** | [npm](https://www.npmjs.com/package/dsh-ap-three-way) |
| **[dsh-ifc-qto](https://github.com/PerryLink/dsh-ifc-qto)** | [npm](https://www.npmjs.com/package/dsh-ifc-qto) |
| **[dsh-qms-capa](https://github.com/PerryLink/dsh-qms-capa)** | [npm](https://www.npmjs.com/package/dsh-qms-capa) |
| **[dsh-legal-intake](https://github.com/PerryLink/dsh-legal-intake)** | [npm](https://www.npmjs.com/package/dsh-legal-intake) |
| **[dsh-legal-clause](https://github.com/PerryLink/dsh-legal-clause)** | [npm](https://www.npmjs.com/package/dsh-legal-clause) |
| **[dsh-freight-audit](https://github.com/PerryLink/dsh-freight-audit)** | [npm](https://www.npmjs.com/package/dsh-freight-audit) |
| **[dsh-hs-candidate](https://github.com/PerryLink/dsh-hs-candidate)** | [npm](https://www.npmjs.com/package/dsh-hs-candidate) |
| **[dsh-travel-recon](https://github.com/PerryLink/dsh-travel-recon)** | [npm](https://www.npmjs.com/package/dsh-travel-recon) |
| **[dsh-pim-lint](https://github.com/PerryLink/dsh-pim-lint)** | [npm](https://www.npmjs.com/package/dsh-pim-lint) |
| **[dsh-eval-pack](https://github.com/PerryLink/dsh-eval-pack)** | [npm](https://www.npmjs.com/package/dsh-eval-pack) |
| **[dsh-finops-suite](https://github.com/PerryLink/dsh-finops-suite)** | [npm](https://www.npmjs.com/package/dsh-finops-suite) |
| **[dsh-contract-suite](https://github.com/PerryLink/dsh-contract-suite)** | [npm](https://www.npmjs.com/package/dsh-contract-suite) |

</details>

## Licença

Apache-2.0. See `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES`.
