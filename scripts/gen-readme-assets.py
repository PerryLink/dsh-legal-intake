#!/usr/bin/env python3
"""Generate README image assets for dsh-legal-intake (docs/assets/).

Outputs (idempotent overwrite):
  dsh-legal-intake-flow-light.svg / dsh-legal-intake-flow-dark.svg
      Hero data-flow diagram. Two hand-written SVG files (vector — never
      rasterized to webp). Text inside is command-surface tokens only
      (legal.intake, Message-ID, DSH_LEGAL_HOME, E_LEGAL_*, ...), so all
      five README languages share the same pair.

This plugin is pure host-side tooling with no UI and the repo ships no
benchmark dataset, so there is no raster evidence chart here. The CJK font
probe below is kept from the family skeleton as a guard: the moment a
Pillow-rendered (raster) asset with Chinese text is added, the script must
abort loudly instead of rendering tofu boxes.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow (bundled DSH runtime Python already ships it)
"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFont  # noqa: F401  (raster assets later)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

# --- palette: PerryLink family (accent) + GitHub page backgrounds ----------
FAMILY = "#4B67B4"   # family accent (badges labelColor family uses #2B3245)
GREEN = {"light": "#16a34a", "dark": "#3fb950"}
SKIN = {
    "light": dict(bg="#ffffff", box="#f6f8fa", border="#d0d7de",
                  text="#1f2328", sub="#57606a"),
    "dark": dict(bg="#0d1117", box="#161b22", border="#30363d",
                 text="#f0f6fc", sub="#8b949e"),
}

# --- CJK font probe: Chinese must never render as tofu boxes ----------------
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",      # Microsoft YaHei
    r"C:\Windows\Fonts\simhei.ttf",    # SimHei
    r"C:\Windows\Fonts\Deng.ttf",      # DengXian
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
if FONT_PATH is None:
    sys.exit("FATAL: no CJK font found (looked for msyh.ttc, simhei.ttf, "
             "Deng.ttf, Noto Sans CJK, PingFang). Refusing to render Chinese "
             "as tofu boxes; install one of the probed fonts and re-run.")


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


# ---------------------------------------------------------------------------
# 1. Hero data-flow SVG (light + dark)
# ---------------------------------------------------------------------------
FLOW = [
    ("EML + manifest", "UTF-8 · local input"),
    ("legal.intake_doctor", "R0 · E_LEGAL_*"),
    ("legal.intake", "parse · classify · dedupe"),
    ("legal.export_ledger", "R1 · xlsx · exports/"),
    ("intake-ledger.xlsx", "local · no upload"),
]


def flow_svg(skin: str) -> str:
    s = SKIN[skin]
    w, h = 1200, 440
    nw, nh, gap = 190, 92, 42
    x0, y0 = 41, 140
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="dsh-legal-intake data flow">',
        '<title>dsh-legal-intake data flow</title>',
        f'<rect width="{w}" height="{h}" rx="18" fill="{s["bg"]}"/>',
        f'<text x="60" y="60" fill="{s["text"]}" font-family="ui-sans-serif,'
        f'system-ui,sans-serif" font-size="30" font-weight="700">'
        f'dsh-legal-intake</text>',
        f'<text x="60" y="92" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="16">EML → thread dedupe → xlsx ledger · '
        f'local files · no model call</text>',
        f'<line x1="60" y1="114" x2="1140" y2="114" stroke="{s["border"]}"/>',
    ]
    for i, (label, sub) in enumerate(FLOW):
        x = x0 + i * (nw + gap)
        accent = GREEN[skin] if i == len(FLOW) - 1 else (
            FAMILY if i in (2, 3) else s["border"])
        parts.append(
            f'<rect x="{x}" y="{y0}" width="{nw}" height="{nh}" rx="14" '
            f'fill="{s["box"]}" stroke="{accent}" stroke-width="2"/>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 38}" fill="{s["text"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="15" font-weight="700">{label}</text>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 66}" fill="{s["sub"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="11.5">{sub}</text>')
        if i < len(FLOW) - 1:
            ax = x + nw + 4
            ay = y0 + nh // 2
            parts.append(
                f'<path d="M{ax} {ay}h{gap - 12}" stroke="{s["sub"]}" '
                f'stroke-width="3"/>')
            parts.append(
                f'<path d="M{ax + gap - 14} {ay - 7}l10 7-10 7" fill="none" '
                f'stroke="{s["sub"]}" stroke-width="3" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')
    # storage-domain bar under intake / ledger export
    by, bh = 283, 54
    for idx in (2, 3):
        cx = x0 + idx * (nw + gap) + nw // 2
        parts.append(
            f'<path d="M{cx} {y0 + nh}v{by - y0 - nh}" stroke="{FAMILY}" '
            f'stroke-width="2" stroke-dasharray="5 5"/>')
    parts.append(
        f'<rect x="60" y="{by}" width="1080" height="{bh}" rx="12" '
        f'fill="{s["box"]}" stroke="{FAMILY}" stroke-width="2"/>')
    parts.append(
        f'<text x="600" y="{by + 34}" fill="{s["text"]}" '
        f'text-anchor="middle" font-family="ui-monospace,monospace" '
        f'font-size="13">legal domain v1 · requests · dedupe by Message-ID '
        f'· $DSH_HOME/storages/dsh-legal-intake · no network</text>')
    parts.append(
        f'<text x="60" y="418" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="12.5">R0 legal.intake_doctor · '
        f'legal.conflict_check | R1 legal.intake · legal.export_ledger | '
        f'no network · no model call</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        with open(os.path.join(OUT, f"dsh-legal-intake-flow-{skin}.svg"),
                  "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin))
    print("wrote 2 SVG assets to docs/assets/ "
          "(no raster evidence chart: this repo ships no benchmark dataset)")


if __name__ == "__main__":
    main()
