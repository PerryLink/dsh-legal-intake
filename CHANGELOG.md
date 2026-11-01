# Changelog

## [0.1.0-alpha.8] — 2026-11-01

### Added

- `legal.conflict_check`: conflicts pre-check between a new matter and existing matters — normalised party names, opposing-side detection and same-party-on-both-sides issues. Read-only; not a substitute for a formal conflicts search. Verified by `node --test test/*.test.mjs` (11/11).

## [Unreleased]

### Added

- `legal.intake_doctor`: pre-intake QA for EML batches — header parse failures, duplicate Message-ID, repeated thread, duplicate/empty attachment names and zero-byte attachments, reported as stable codes instead of throwing. Read-only. Verified by `node --test test/*.test.mjs` (7/7).

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
