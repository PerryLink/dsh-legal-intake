# Changelog

## [0.2.0] — 2026-11-13

### Breaking

- **Tool names no longer contain a dot.** The four tools are now `legal_intake`, `legal_export_ledger`, `legal_intake_doctor` and `legal_conflict_check`. The previous spelling joined the `legal` namespace to each tool suffix with a dot; providers validate `tools[].name` against `^[a-zA-Z0-9_-]+$`, so a dotted name made the provider reject the whole `tools` array with `Invalid 'tools[N].name'`. The plugin still registered, but every request that carried its tools failed. Update prompts, saved calls and permission rules that still use the old dotted spelling. Minor rather than patch bump because tool names are covered by the 0.1.0 compatibility promise.
- `test/tool-name-wire.test.mjs` pins the wire pattern: every registered tool name must match `^[a-zA-Z0-9_-]+$`, must not contain a dot, and must be unique.
- Earlier changelog entries use the new spelling, so a repository-wide search no longer finds a dotted tool name.

### Added

- `legal_intake_doctor`: pre-intake QA for EML batches — header parse failures, duplicate Message-ID, repeated thread, duplicate/empty attachment names and zero-byte attachments, reported as stable codes instead of throwing. Read-only. Verified by `node --test test/*.test.mjs`.

## [0.1.0] — 2026-11-03

### Stable

- First non-alpha release: tool names and the CLI surface are covered by a
  compatibility promise (breaking changes require a minor bump).
- Ships a quickstart sample, a one-line prompt, a permission block and real captures.

## [0.1.0] — 2026-11-01

### Security / Fixes

- Release configuration hardening: wider host peer range and a build step before publish.


### Added

- `legal_conflict_check`: conflicts pre-check between a new matter and existing matters — normalised party names, opposing-side detection and same-party-on-both-sides issues. Read-only; not a substitute for a formal conflicts search. Verified by `node --test test/*.test.mjs` (11/11).

## [0.1.0-alpha.6] — 2026-11-01

### Changed

- Documentation: five-language fixture/acceptance links now resolve on npm; added specific related-checker/tool links.
- Marketplace metadata: taxonomy category, archetype, domains and status; docs page now shows the same.
- Added a real terminal hero (and GIF for the active docs set) plus `TROUBLESHOOTING.md`.

All notable changes to `dsh-legal-intake` are documented here. The format follows Keep a Changelog; this project uses alpha versions.

## [0.1.0-alpha.5] — 2026-11-01

### Added

- Five-language READMEs: English, 简体中文, Español, Português, हिन्दी.
- Local workflow SVG at `docs/assets/dsh-legal-intake-flow.svg`.
- Family cross-links (domain index, checker family, `dsh-kit`), compatibility, permissions, and related-work sections.
- Standard repository files: `SECURITY.md`, `PRIVACY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, and `icon.svg`.

### Changed

- README aligned with the PerryLink DSH checker/plugin family style; package remains public/synthetic, alpha, not GA.

## [Earlier]

Earlier alpha builds are available from npm and GitHub Releases; this file starts at the family-standard documentation wave.
