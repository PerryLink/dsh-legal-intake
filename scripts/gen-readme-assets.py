#!/usr/bin/env python3
"""README visuals for dsh-legal-intake, drawn from what this package ships.

Outputs (docs/assets/, idempotent overwrite):

  dsh-legal-intake-hero-{zh,en}-{light,dark}.webp   1440x576
  dsh-legal-intake-flow-v5-{light,dark}.svg          1100x660

Every number and label in both figures is taken from this repository, not
invented:

  * `src/core/intake.ts` - `parseEml()` reads Subject / From (both required,
    otherwise `E_LEGAL_EML_INVALID` is thrown), Date (optional), Message-ID
    (fallback `mid-<djb2 hash>`), Thread-Id (fallback = Message-ID);
    `classify()` tests a fixed keyword order NDA -> MSA -> CONTRACT_REVIEW ->
    DISPUTE -> COMPLIANCE -> OTHER and stops at the first hit.
  * `src/plugin/tools.ts` - `legal.intake` seeds its seen-set from the stored
    `requests` table, dedupes by Message-ID (`duplicates[]`, no new row),
    derives `request_id = req_ + sha256(message_id)[:12]`, writes a record
    with status `new`; `legal.intake_doctor` is read-only and returns stable
    codes (`E_LEGAL_MESSAGE_DUPLICATE`, `E_LEGAL_THREAD_REPEATED`,
    `E_LEGAL_ATTACHMENT_DUPLICATE`, `E_LEGAL_ATTACHMENT_EMPTY`);
    `legal.export_ledger` writes `exports/intake-ledger.xlsx`, sheet
    `Requests`; `legal.conflict_check` normalises party names and reports
    `opposing_sides` plus `E_LEGAL_PARTY_BOTH_SIDES`.
  * `src/plugin/storage.ts` - `legal` domain v1, one `requests` table, ten
    record fields, status `new` | `triaged`.
  * `samples/quickstart/input/` + `samples/quickstart/expected/result.json` -
    a real run of the shipped synthetic batch: 3 EML, 2 new requests, 1
    duplicate suppressed, types `{MSA: 1, NDA: 1}`, four doctor codes,
    ledger 2 rows, request ids `req_455da4f6c27e` and `req_f07404d28828`.

Hero - left column is copy (kicker / two-line title / two value lines / two
subtitle lines / two meta lines / footer). The right side is this plugin's own
artefact, not a generic dashboard: the 3-message inbox, a Message-ID sieve
plate that stops the resent copy (`3 -> 2 new / 1 dup`), the two ledger rows
the export actually contains, and the doctor's four issue codes underneath.
It is the same batch at two distances: what came in, and what was written out.

Flow - grammar = SPLIT GATE (dual channel) + SIEVE + ORDERED CLASSIFIER
STAIRCASE, not a row of nodes. Band 01 is the shared input batch and the one
`parseEml()` result (with both fallbacks). A fork feeds two gates: 02, the
read-only side that holds `legal.intake_doctor` (the four codes this sample
really raises) and `legal.conflict_check` (a separate parties input, marked as
such); 03, the local-write side that dedupes against `seen(Message-ID)`,
classifies through the six ordered types, stores two records in
`legal.requests`, and exports `intake-ledger.xlsx`. The footer keeps the
boundary visible: source read-only, no network/model, writes limited to
`exports/` and `legal.requests`.

Old single-skin assets (`...-flow.svg`, `...-flow-{light,dark}.svg`,
`...-hero.png`, `...-demo.gif`, `quickstart.png`) stay on disk so external
links keep resolving; the READMEs reference only the new hero set and the
flow-v5 pair.

Text is measured with the exact fonts the figures name before drawing;
anything that would overflow aborts the run instead of shipping clipped text.
Hero title 84px, value lines 28px, subtitles 25px, meta 20px, footer 16px.
Flow: figure title 28px, gate titles and type names 13px, annotations >= 11px.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow + Windows fonts msyh.ttc / msyhbd.ttc / consola.ttf /
           consolab.ttf.
"""
from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")
NAME = "dsh-legal-intake"

FONT_FILES = {
    "cjk": r"C:\Windows\Fonts\msyh.ttc",
    "cjk_bold": r"C:\Windows\Fonts\msyhbd.ttc",
    "mono": r"C:\Windows\Fonts\consola.ttf",
    "mono_bold": r"C:\Windows\Fonts\consolab.ttf",
}
for _kind, _path in FONT_FILES.items():
    if not os.path.exists(_path):
        raise SystemExit(f"FATAL: font missing: {_path}")

os.makedirs(OUT, exist_ok=True)

FONT_CSS_SANS = ("'Microsoft YaHei','Segoe UI','PingFang SC',"
                 "'Noto Sans CJK SC',sans-serif")
FONT_CSS_MONO = "Consolas,'Microsoft YaHei',ui-monospace,monospace"

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", panel="#fbfaff", edge="#e6e2ef",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", accent_soft="#ece7f9", tint="#f7f5fb",
        rule="#e7e4f0", warn="#b45309", warn_bg="#fbf1e4",
        shadow=(43, 35, 80), shadow_hex="#2b2440", shadow_alpha=46,
        dot="#cfc8e2", dot_alpha=72,
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1b2231", panel="#151d2c", edge="#2e374b",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", accent_soft="#242d42", tint="#202839",
        rule="#2b3348", warn="#d9a441", warn_bg="#292217",
        shadow=(0, 0, 0), shadow_hex="#000000", shadow_alpha=150,
        dot="#2a3346", dot_alpha=66,
    ),
}

# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------
_font_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}
_MEASURE = ImageDraw.Draw(Image.new("RGB", (8, 8)))

_ANCHOR = {"la": "ls", "ra": "rs", "ma": "ms", "mm": "mm", "lm": "lm",
           "rm": "rm"}


def font(size: float, kind: str = "cjk") -> ImageFont.FreeTypeFont:
    key = (kind, max(1, int(round(size))))
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(FONT_FILES[kind], key[1])
    return _font_cache[key]


def measure(text: str, size: float, kind: str = "cjk") -> float:
    return _MEASURE.textlength(text, font=font(size, kind))


def hx(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def rgba(color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    return hx(color) + (alpha,)


def require_w(text: str, size: float, kind: str, max_w: float,
              what: str) -> None:
    got = measure(text, size, kind)
    if got > max_w + 0.4:
        raise SystemExit(f"FATAL: {what} overflows: {text!r} needs "
                         f"{got:.1f}px > {max_w:.0f}px")


def fit(text: str, kind: str, max_w: float, start: float,
        minimum: float) -> float:
    size = float(start)
    while size > minimum:
        if measure(text, size, kind) <= max_w:
            return size
        size -= 1
    if measure(text, size, kind) > max_w:
        raise SystemExit(f"FATAL: text does not fit {max_w:.0f}px at >= "
                         f"{minimum}px: {text!r}")
    return size


def ellipsize(text: str, size: float, kind: str, max_w: float) -> str:
    if measure(text, size, kind) <= max_w:
        return text
    while text and measure(text + "…", size, kind) > max_w:
        text = text[:-1]
    return text.rstrip() + "…"


def gradient(w: int, h: int, top: str, bottom: str) -> Image.Image:
    base = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(base)
    a, b = hx(top), hx(bottom)
    for y in range(h):
        t = 0.10 * (y / h) + 0.90 * (y / h) ** 1.35
        draw.line([(0, y), (w, y)],
                  fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return base.convert("RGBA")


def add_glow(img: Image.Image, cx: int, cy: int, radius: int, color: str,
             alpha: int) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    rgb = hx(color)
    for i in range(12, 0, -1):
        r = radius * i / 12
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     fill=rgb + (int(alpha * (1 - i / 13)),))
    layer = layer.filter(ImageFilter.GaussianBlur(42))
    return Image.alpha_composite(img, layer)


def add_dots(img: Image.Image, color: str, alpha: int, step: int = 30,
             radius: float = 1.15) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    fill = rgba(color, alpha)
    for y in range(18, img.height, step):
        for x in range(18, img.width, step):
            draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                         fill=fill)
    return Image.alpha_composite(img, layer)


def shadow_card(img: Image.Image, box: tuple[int, int, int, int], radius: int,
                fill: str, edge: str, s: dict, width: int = 1,
                shadow: int = 18, spread: int = 7) -> Image.Image:
    x0, y0, x1, y1 = box
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle([x0 + 1, y0 + spread, x1 + 1, y1 + spread],
                           radius=radius,
                           fill=rgba("#000000", 0) if s["shadow_alpha"] == 0
                           else s["shadow"] + (s["shadow_alpha"],))
    img = Image.alpha_composite(img, layer.filter(
        ImageFilter.GaussianBlur(shadow / 2)))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(box, radius=radius, fill=rgba(fill),
                           outline=rgba(edge), width=width)
    return img


def rounded(img: Image.Image, box: tuple[int, int, int, int], radius: int,
            fill: str | None = None, edge: str | None = None,
            width: float = 1) -> Image.Image:
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(box, radius=radius,
                           fill=rgba(fill) if fill else None,
                           outline=rgba(edge) if edge else None,
                           width=max(1, int(round(width))))
    return img


def dashed_line(img: Image.Image, start: tuple[float, float],
                end: tuple[float, float], color: str, width: int = 1,
                dash: int = 5, gap: int = 4) -> None:
    draw = ImageDraw.Draw(img)
    x0, y0 = start
    x1, y1 = end
    length = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
    if length == 0:
        return
    dx, dy = (x1 - x0) / length, (y1 - y0) / length
    pos = 0.0
    while pos < length:
        end_pos = min(pos + dash, length)
        draw.line([(x0 + dx * pos, y0 + dy * pos),
                   (x0 + dx * end_pos, y0 + dy * end_pos)],
                  fill=rgba(color), width=width)
        pos = end_pos + gap


def dashed_rect(img: Image.Image, box: tuple[int, int, int, int], color: str,
                width: int = 1, dash: int = 5, gap: int = 4) -> None:
    x0, y0, x1, y1 = box
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                 ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        dashed_line(img, a, b, color, width, dash, gap)


def txt(img: Image.Image, xy: tuple[float, float], text: str, size: float,
        fill: str, kind: str = "cjk", anchor: str = "la",
        alpha: int = 255) -> None:
    draw = ImageDraw.Draw(img)
    draw.text(xy, text, font=font(size, kind), fill=rgba(fill, alpha),
              anchor=_ANCHOR.get(anchor, anchor))


def tracked(img: Image.Image, xy: tuple[float, float], text: str, size: float,
            fill: str, kind: str = "mono_bold", spacing: float = 1.8,
            alpha: int = 255) -> None:
    draw = ImageDraw.Draw(img)
    x, y = xy
    f = font(size, kind)
    for ch in text:
        draw.text((x, y), ch, font=f, fill=rgba(fill, alpha), anchor="ls")
        x += draw.textlength(ch, font=f) + spacing


def envelope(img: Image.Image, x: float, y: float, w: float, h: float,
             color: str, width: int = 2) -> None:
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([x, y, x + w, y + h], radius=2,
                           outline=rgba(color), width=width)
    draw.line([(x + 1, y + 1), (x + w / 2, y + h * 0.62), (x + w - 1, y + 1)],
              fill=rgba(color), width=width, joint="curve")


def funnel(img: Image.Image, cx: float, cy: float, color: str,
           width: int = 2) -> None:
    draw = ImageDraw.Draw(img)
    draw.polygon([(cx - 9, cy - 10), (cx + 9, cy - 10), (cx + 2, cy + 2),
                  (cx + 2, cy + 10), (cx - 2, cy + 10), (cx - 2, cy + 2)],
                 outline=rgba(color), width=width)


def pill_img(img: Image.Image, x: float, y: float, text: str, size: float,
             fg: str, bg: str, kind: str = "mono_bold",
             padx: float = 9) -> tuple[float, float]:
    w = measure(text, size, kind) + padx * 2
    h = size + 8
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h / 2, fill=rgba(bg))
    txt(img, (x + w / 2, y + h / 2), text, size, fg, kind, "mm")
    return w, h


# ---------------------------------------------------------------------------
# 1. hero - Pillow, 1440x576, zh/en x light/dark
# ---------------------------------------------------------------------------
COPY = {
    "zh": dict(
        kicker="DSH 插件 · 本地法务需求收件",
        title=[[("EML 进来，", "text")], [("台账出去", "accent")]],
        values=["按 Message-ID 去重，按关键词分成六类。",
                "台账写成 xlsx，原件一字不改。"],
        subs=["入库前体检：缺头、重发、同名与空附件都有错误码。",
              "不连邮箱、不联网、不调用模型，结果只留在本机。"],
        meta=["legal.intake · legal.export_ledger · R1",
              "legal.intake_doctor · legal.conflict_check · R0"],
        footer="原件只读 · Apache-2.0 · PerryLink DSH plugin family",
        title_ys=[172, 272],
        value_ys=[340, 378],
        sub_ys=[422, 450],
        meta_ys=[496, 520],
        footer_y=556,
        divider_y=536,
        dup_tag="重发",
    ),
    "en": dict(
        kicker="DSH PLUGIN · LOCAL LEGAL INTAKE",
        title=[[("EML in,", "text")], [("a ledger out", "accent")]],
        values=["Dedupe by Message-ID, sort into six types.",
                "One xlsx out; the original is never edited."],
        subs=["Read-only doctor flags resends and bad attachments.",
              "Results stay on this machine; nothing is uploaded."],
        meta=["legal.intake · legal.export_ledger · R1",
              "legal.intake_doctor · legal.conflict_check · R0"],
        footer="Local files only · original read-only · Apache-2.0",
        title_ys=[168, 268],
        value_ys=[336, 374],
        sub_ys=[418, 446],
        meta_ys=[494, 518],
        footer_y=554,
        divider_y=534,
        dup_tag="dup",
    ),
}

INBOX = [
    dict(subject="NDA review request - Project Atlas", who="Dana Li · 09:12",
         mid="<syn-atlas-nda-001@example.test>", dup=False),
    dict(subject="MSA request - Project Atlas rollout", who="Sam Wu · 11:40",
         mid="<syn-atlas-msa-002@example.test>", dup=False),
    dict(subject="NDA review request - Project Atlas", who="Dana Li · 15:05",
         mid="<syn-atlas-nda-001@example.test>", dup=True),
]
LEDGER = [
    dict(subject="MSA request - Project Atlas rollout",
         rid="req_455da4f6c27e", kind="MSA", att=1),
    dict(subject="NDA review request - Project Atlas",
         rid="req_f07404d28828", kind="NDA", att=2),
]
DOCTOR_CODES = ["E_LEGAL_MESSAGE_DUPLICATE", "E_LEGAL_THREAD_REPEATED",
                "E_LEGAL_ATTACHMENT_DUPLICATE", "E_LEGAL_ATTACHMENT_EMPTY"]


def hero(lang: str, skin: str) -> None:
    s = SKIN[skin]
    c = COPY[lang]
    W, H = 1440, 576
    img = gradient(W, H, s["bg_from"], s["bg_to"])
    img = add_glow(img, 1040, 150, 430, s["accent"],
                   34 if skin == "light" else 22)
    img = add_glow(img, 250, 500, 380,
                   "#8b7ad8" if skin == "light" else "#32406b",
                   30 if skin == "light" else 18)
    img = add_dots(img, s["dot"], s["dot_alpha"])

    # editorial rail
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([54, 86, 58, 546], radius=2, fill=rgba(s["accent"]))
    draw.ellipse([50, 80, 62, 92], fill=rgba(s["accent"]))
    draw.ellipse([50, 540, 62, 552], fill=rgba(s["accent"]))

    # left copy
    tracked(img, (84, 92), c["kicker"], 17, s["accent"], "cjk_bold", 1.4)
    title_size = 84.0
    for line in c["title"]:
        require_w("".join(part for part, _ in line), title_size, "cjk_bold",
                  650, f"{lang} title")
    for line, y in zip(c["title"], c["title_ys"]):
        x = 84.0
        for part, color in line:
            txt(img, (x, y), part, title_size, s[color], "cjk_bold")
            x += measure(part, title_size, "cjk_bold")

    for text, y in zip(c["values"], c["value_ys"]):
        require_w(text, 28, "cjk", 650, f"{lang} value line")
        txt(img, (84, y), text, 28, s["text"], "cjk")

    for text, y in zip(c["subs"], c["sub_ys"]):
        require_w(text, 25, "cjk", 650, f"{lang} subtitle line")
        txt(img, (84, y), text, 25, s["sub"], "cjk")

    for text, y in zip(c["meta"], c["meta_ys"]):
        require_w(text, 20, "mono", 650, f"{lang} meta line")
        txt(img, (84, y), text, 20, s["sub"], "mono")

    draw = ImageDraw.Draw(img)
    draw.line([84, c["divider_y"], 700, c["divider_y"]],
              fill=rgba(s["edge"]), width=1)
    require_w(c["footer"], 16, "cjk", 650, f"{lang} footer")
    txt(img, (84, c["footer_y"]), c["footer"], 16, s["faint"], "cjk")

    # ------------------------------------------------------------------
    # right-hand artefact: inbox -> Message-ID sieve -> ledger
    # ------------------------------------------------------------------
    img = shadow_card(img, (740, 56, 1400, 520), 22, s["card"], s["edge"], s,
                      width=1, shadow=26, spread=10)
    tracked(img, (760, 90), "INTAKE · LOCAL BATCH", 10.5, s["accent"],
            "mono_bold", 1.6)
    txt(img, (1380, 90), "3 EML · 1 manifest", 10.5, s["faint"], "mono", "ra")
    draw = ImageDraw.Draw(img)
    draw.line([760, 102, 1380, 102], fill=rgba(s["rule"]), width=1)

    # inbox
    img = rounded(img, (760, 112, 1016, 392), 14, s["tint"], s["edge"], 1)
    tracked(img, (776, 132), "INBOX", 10.5, s["accent"], "mono_bold", 1.4)
    txt(img, (1000, 132), "read-only", 10, s["faint"], "mono", "ra")
    for row, y in zip(INBOX, (142, 208, 274)):
        if row["dup"]:
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle([776, y, 1000, y + 58], radius=10,
                                   fill=rgba(s["card"]), outline=rgba(s["warn"]),
                                   width=1)
        else:
            img = rounded(img, (776, y, 1000, y + 58), 10, s["card"],
                          s["edge"], 1)
        envelope(img, 790, y + 13, 16, 12,
                 s["warn"] if row["dup"] else s["accent"], 2)
        txt(img, (818, y + 22),
            ellipsize(row["subject"], 10.8, "cjk", 168), 10.8, s["text"], "cjk")
        txt(img, (818, y + 37), row["who"], 9.6, s["faint"], "cjk")
        txt(img, (818, y + 51), row["mid"], 9.2, s["faint"], "mono")
        if row["dup"]:
            txt(img, (990, y + 34), c["dup_tag"], 9.6, s["warn"], "cjk_bold",
                "ra")
    txt(img, (776, 352), "attachments.json", 9.6, s["sub"], "mono")
    txt(img, (776, 369), "name / sha256 / size", 9.2, s["faint"], "mono")

    # sieve plate
    img = rounded(img, (1032, 156, 1084, 344), 12, s["accent_soft"],
                  s["accent"], 1.2)
    funnel(img, 1058, 190, s["accent"])
    txt(img, (1058, 222), "msg-id", 9.4, s["accent"], "mono", "ma")
    txt(img, (1058, 254), "2/3", 15, s["accent"], "mono_bold", "ma")
    txt(img, (1058, 268), "new", 9.4, s["faint"], "mono", "ma")
    draw = ImageDraw.Draw(img)
    draw.line([1044, 286, 1072, 286], fill=rgba(s["accent"]), width=1)
    txt(img, (1058, 310), "1", 13, s["warn"], "mono_bold", "ma")
    txt(img, (1058, 324), "dup", 9.4, s["warn"], "mono", "ma")

    # ledger
    img = rounded(img, (1100, 112, 1380, 392), 14, s["card"], s["edge"], 1)
    tracked(img, (1116, 132), "LEDGER · Requests", 10.5, s["accent"],
            "mono_bold", 1.3)
    txt(img, (1364, 132), "2 rows", 10, s["faint"], "mono", "ra")
    for rec, y in zip(LEDGER, (142, 230)):
        img = rounded(img, (1116, y, 1364, y + 80), 10, s["tint"],
                      s["edge"], 1)
        txt(img, (1128, y + 21),
            ellipsize(rec["subject"], 10.8, "cjk", 212), 10.8, s["text"], "cjk")
        txt(img, (1128, y + 37), rec["rid"], 9.6, s["faint"], "mono")
        pill_img(img, 1128, y + 48, rec["kind"], 9.2, s["accent"],
                 s["accent_soft"], "mono_bold", 8)
        txt(img, (1160, y + 61),
            f"new · {rec['att']} att", 9.4, s["faint"], "cjk")
    txt(img, (1116, 334), "intake-ledger.xlsx", 10, s["sub"], "mono")
    txt(img, (1116, 350), "sheet Requests · sha256", 9.2, s["faint"], "mono")
    txt(img, (1116, 366), "$DSH_LEGAL_HOME/exports/", 9.2, s["faint"], "mono")

    # arrows between the three parts
    draw = ImageDraw.Draw(img)
    for x0, x1 in ((1016, 1030), (1084, 1098)):
        draw.line([x0, 220, x1 - 3, 220], fill=rgba(s["accent"]), width=1)
        draw.polygon([(x1 - 4, 216), (x1 + 2, 220), (x1 - 4, 224)],
                     fill=rgba(s["accent"]))

    # doctor strip
    tracked(img, (760, 420), "doctor", 10.5, s["accent"], "mono_bold", 1.4)
    txt(img, (818, 420), "· 4 issues", 10.5, s["accent"], "cjk")
    txt(img, (1380, 420), "read-only · no writes", 10, s["faint"], "cjk", "ra")
    txt(img, (760, 442), " · ".join(DOCTOR_CODES[:2]), 10, s["sub"], "mono")
    txt(img, (760, 458), " · ".join(DOCTOR_CODES[2:]), 10, s["sub"], "mono")
    txt(img, (760, 476), "synthetic sample · samples/quickstart",
        9.2, s["faint"], "mono")
    txt(img, (760, 494), "no network · no model call · original untouched",
        9.6, s["faint"], "cjk")

    path = os.path.join(OUT, f"{NAME}-hero-{lang}-{skin}.webp")
    img.convert("RGB").save(path, "WEBP", quality=90, method=6)
    print(f"wrote {os.path.basename(path)}")


# ---------------------------------------------------------------------------
# 2. flow - hand-written SVG, 1100x660, light/dark
# ---------------------------------------------------------------------------
def flow_svg(skin: str) -> str:
    s = SKIN[skin]
    W, H = 1100, 660
    accent = s["accent"]
    parts: list[str] = []

    def kind_for(kind: str, weight: int) -> str:
        base = "cjk" if kind == "sans" else "mono"
        return f"{base}_bold" if weight >= 700 else base

    def require_svg(text: str, size: float, kind: str, max_w: float,
                    what: str, weight: int = 400) -> None:
        got = measure(text, size, kind_for(kind, weight))
        if got > max_w + 0.6:
            raise SystemExit(f"FATAL: flow {what} overflows: {text!r} needs "
                             f"{got:.1f}px > {max_w:.0f}px")

    def trunc_svg(text: str, size: float, kind: str, max_w: float) -> str:
        k = kind_for(kind, 400)
        if measure(text, size, k) <= max_w:
            return text
        while text and measure(text + "…", size, k) > max_w:
            text = text[:-1]
        return text.rstrip() + "…"

    def t(x: float, y: float, text: str, size: float, fill: str,
          kind: str = "sans", weight: int = 400, anchor: str = "start",
          opacity: float | None = None, tracking: float | None = None) -> str:
        family = FONT_CSS_MONO if kind == "mono" else FONT_CSS_SANS
        attrs = [f'x="{x}"', f'y="{y}"', f'fill="{fill}"',
                 f'font-family="{family}"', f'font-size="{size}"',
                 'xml:space="preserve"']
        if weight:
            attrs.append(f'font-weight="{weight}"')
        if anchor != "start":
            attrs.append(f'text-anchor="{anchor}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        if tracking is not None:
            attrs.append(f'letter-spacing="{tracking}"')
        return f"<text {' '.join(attrs)}>{escape(text)}</text>"

    def r(x: float, y: float, w: float, h: float, fill: str,
          stroke: str | None = None, sw: float = 1.3, rx: float = 0,
          dash: str | None = None, shadow: bool = False,
          opacity: float | None = None) -> str:
        attrs = [f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"',
                 f'rx="{rx}"', f'fill="{fill}"']
        if stroke:
            attrs += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        if shadow:
            attrs.append('filter="url(#soft)"')
        return f"<rect {' '.join(attrs)}/>"

    def line(x1: float, y1: float, x2: float, y2: float, stroke: str,
             sw: float = 1.2, dash: str | None = None,
             opacity: float | None = None) -> str:
        attrs = [f'x1="{x1}"', f'y1="{y1}"', f'x2="{x2}"', f'y2="{y2}"',
                 f'stroke="{stroke}"', f'stroke-width="{sw}"',
                 'stroke-linecap="round"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        return f"<line {' '.join(attrs)}/>"

    def env_icon(x: float, y: float, w: float, h: float, stroke: str) -> str:
        flap = f"M{x + 1} {y + 1}L{x + w / 2} {y + h * 0.6}L{x + w - 1} {y + 1}"
        return (r(x, y, w, h, "none", stroke, 1.4, 2)
                + f'<path d="{flap}" fill="none" stroke="{stroke}" '
                  'stroke-width="1.4" stroke-linejoin="round"/>')

    def pill(x: float, y: float, text: str, size: float, fg: str, bg: str,
             edge: str | None = None, dash: str | None = None,
             kind: str = "mono", weight: int = 700,
             pad: float = 16) -> tuple[str, float, float]:
        k = kind_for(kind, weight)
        w = measure(text, size, k) + pad
        h = size + 9
        body = r(x, y, w, h, bg, edge or "none", 1, h / 2, dash)
        body += t(x + w / 2, y + h / 2 + size * 0.34, text, size, fg,
                  kind, weight, "middle")
        return body, w, h

    def pill_w(text: str, size: float, kind: str = "mono",
               weight: int = 700, pad: float = 16) -> float:
        return measure(text, size, kind_for(kind, weight)) + pad

    # ---- background ------------------------------------------------------
    desc = (
        "A batch of three synthetic EML messages is parsed once by "
        "parseEml(). Band 01 shows the input files together with the parse "
        "result: Subject and From are required, Date is optional, a missing "
        "Message-ID falls back to mid-<content hash> and a missing Thread-Id "
        "falls back to the Message-ID. A fork then feeds two gates. Gate 02 "
        "is read-only and never throws: legal.intake_doctor reports four "
        "codes for this sample (E_LEGAL_MESSAGE_DUPLICATE, "
        "E_LEGAL_THREAD_REPEATED, E_LEGAL_ATTACHMENT_DUPLICATE, "
        "E_LEGAL_ATTACHMENT_EMPTY); legal.conflict_check takes a separate "
        "parties input, normalises names and reports opposing sides. Gate 03 "
        "is the local write path: legal.intake dedupes against seen "
        "Message-IDs (3 messages become 2 new requests and 1 duplicate that "
        "is counted but not stored), classifies in the fixed order NDA, MSA, "
        "CONTRACT_REVIEW, DISPUTE, COMPLIANCE, OTHER (this sample: NDA 1, MSA "
        "1), stores two records in the legal domain requests table "
        "(request_id = req_ + sha256(Message-ID)[:12], status new), and "
        "legal.export_ledger writes exports/intake-ledger.xlsx with sheet "
        "Requests and 2 rows. The footer keeps the boundary visible: the "
        "source is read-only, there is no network and no model call, and "
        "writes go only to exports/ and legal.requests."
    )
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" '
        'aria-labelledby="fig-title fig-desc">\n'
        f'<title id="fig-title">{NAME}: one batch, one parse, two gates - '
        'read-only doctor vs. dedupe-classify-export write path</title>\n'
        f'<desc id="fig-desc">{escape(desc)}</desc>\n'
        '<defs>\n'
        '  <linearGradient id="bg" x1="0" y1="0" x2="0.18" y2="1">\n'
        f'    <stop offset="0" stop-color="{s["bg_from"]}"/>'
        f'<stop offset="1" stop-color="{s["bg_to"]}"/>\n'
        '  </linearGradient>\n'
        '  <filter id="soft" x="-30%" y="-30%" width="160%" height="180%">\n'
        f'    <feDropShadow dx="0" dy="7" stdDeviation="9" '
        f'flood-color="{s["shadow_hex"]}" '
        f'flood-opacity="{0.14 if skin == "light" else 0.52}"/>\n'
        '  </filter>\n'
        '  <pattern id="dots" width="24" height="24" '
        'patternUnits="userSpaceOnUse">\n'
        f'    <circle cx="1.2" cy="1.2" r="1.2" fill="{s["dot"]}"/>\n'
        '  </pattern>\n'
        '</defs>\n'
        f'<rect x="0" y="0" width="{W}" height="{H}" rx="22" '
        'fill="url(#bg)"/>\n'
        f'<rect x="0" y="0" width="{W}" height="{H}" rx="22" '
        'fill="url(#dots)" opacity="0.5"/>\n'
    )

    # ---- header ----------------------------------------------------------
    parts.append(t(44, 52, NAME, 28, s["text"], "mono", 700))
    subtitle = ("One batch, two gates: a read-only doctor on one side, "
                "dedupe → classify → export on the other.")
    require_svg(subtitle, 14.5, "sans", 690, "subtitle")
    parts.append(t(44, 78, subtitle, 14.5, s["sub"], "sans"))

    pill_text = "quickstart · 3 EML · synthetic"
    pw = pill_w(pill_text, 11, "mono")
    body, _, _ = pill(1056 - pw, 24, pill_text, 11, accent, s["accent_soft"],
                      None, None, "mono")
    parts.append(body)
    parts.append(t(1056, 64, "no network · no model call", 11, s["faint"],
                   "mono", 400, "end"))

    in_line = ("IN  ·  messages[] { eml_text, attachments[name · sha256 · "
               "size] }  ·  UTF-8  ·  local files")
    out_line = "OUT  ·  issues[] · requests · intake-ledger.xlsx"
    require_svg(in_line, 11, "mono", 660, "IN line")
    require_svg(out_line, 11, "mono", 330, "OUT line")
    parts.append(t(44, 106, in_line, 11, s["faint"], "mono"))
    parts.append(t(1056, 106, out_line, 11, s["faint"], "mono", 400, "end"))
    parts.append(line(44, 118, 1056, 118, s["rule"], 1))

    # ---- 01 input + parse ------------------------------------------------
    parts.append(t(44, 142, "01", 12, accent, "mono", 700))
    parts.append(t(70, 142, "INPUT → PARSE", 12.5, accent, "sans", 700,
                   tracking=1.2))
    parse_note = "parseEml() · one parse, both gates read the same batch"
    require_svg(parse_note, 11, "sans", 360, "parse note")
    parts.append(t(1056, 142, parse_note, 11, s["faint"], "sans", 400, "end"))
    parts.append(r(44, 152, 1012, 138, s["card"], s["edge"], 1.4, 18,
                   shadow=True))
    parts.append(r(45, 153, 4, 136, accent, None, 0, 2))
    parts.append(t(60, 172, "local inputs · read-only", 11, s["faint"], "mono"))

    files = [
        ("synthetic-nda-request.eml", "2 att · 09:12", False),
        ("synthetic-msa-request.eml", "1 att · 11:40", False),
        ("synthetic-nda-resent.eml", "0 att · 15:05 · resend", True),
        ("attachments.json", "name / sha256 / size", False),
    ]
    for i, (fname, meta, resent) in enumerate(files):
        y = 192 + i * 21
        parts.append(env_icon(60, y - 10, 14, 11,
                              accent if i < 3 else s["faint"]))
        parts.append(t(82, y, fname, 12.5, s["text"], "mono"))
        require_svg(meta, 11, "mono", 160, f"file meta {fname}")
        parts.append(t(430, y, meta, 11,
                       s["warn"] if resent else s["faint"], "mono", 400, "end"))

    parts.append(line(452, 168, 452, 258, s["rule"], 1))
    parts.append(line(748, 168, 748, 258, s["rule"], 1))
    parts.append(t(472, 172, "Eml · parsed", 11, s["faint"], "mono"))

    grid = [
        (472, 194, "Subject", "NDA review request - Project Atlas", 748),
        (472, 220, "From", "Dana Li <dana.li@example.test>", 748),
        (472, 246, "Date", "Tue, 20 Oct 2026 09:12:00 +0000", 748),
        (762, 194, "Message-ID", "<syn-atlas-nda-001@example.test>", 1040),
        (762, 220, "Thread-Id", "<thread-atlas-001@example.test>", 1040),
        (762, 246, "attachments[]", "2 · 1 · 0 (metadata)", 1040),
    ]
    for gx, gy, label, value, end in grid:
        value_x = gx + measure(label, 11, "cjk") + 12
        require_svg(value, 11, "mono", end - value_x,
                    f"parse value {label}")
        parts.append(t(gx, gy, label, 11, s["faint"], "sans"))
        parts.append(t(value_x, gy, value, 11, s["text"], "mono"))

    fallback = ("no Subject / From → E_LEGAL_EML_INVALID (throws)   ·   "
                "no Message-ID → mid-<content hash>   ·   no Thread-Id → "
                "= Message-ID   ·   attachment content is never read")
    require_svg(fallback, 11, "mono", 976, "fallback note")
    parts.append(line(60, 264, 1040, 264, s["rule"], 1))
    parts.append(t(60, 282, fallback, 11, s["faint"], "mono"))

    # ---- fork bus --------------------------------------------------------
    parts.append(line(550, 290, 550, 301, accent, 1.4, opacity=0.55))
    parts.append(line(284, 301, 802, 301, accent, 1.4, opacity=0.55))
    parts.append(line(284, 301, 284, 308, accent, 1.4, opacity=0.55))
    parts.append(line(802, 301, 802, 308, accent, 1.4, opacity=0.55))
    for bx in (284, 802):
        parts.append(f'<path d="M{bx - 4} 306L{bx + 4} 306L{bx} 314Z" '
                     f'fill="{accent}"/>')

    # ---- 02 read-only gate ----------------------------------------------
    parts.append(r(44, 314, 480, 264, s["card"], s["edge"], 1.6, 18,
                   shadow=True))
    parts.append(t(60, 344, "02", 12, accent, "mono", 700))
    parts.append(t(86, 344, "R0 · READ-ONLY", 13, accent, "sans", 700,
                   tracking=0.6))
    parts.append(t(508, 344, "no writes · never throws", 11, s["faint"],
                   "sans", 400, "end"))
    parts.append(line(60, 356, 508, 356, s["rule"], 1))

    parts.append(t(60, 376, "legal.intake_doctor", 13, s["text"], "mono", 700))
    parts.append(t(508, 376, "3 messages → 4 issues", 11.5, accent, "mono",
                   700, "end"))
    doctor = [
        ("E_LEGAL_MESSAGE_DUPLICATE", "same Message-ID"),
        ("E_LEGAL_THREAD_REPEATED", "same Thread-Id"),
        ("E_LEGAL_ATTACHMENT_DUPLICATE", "same file name"),
        ("E_LEGAL_ATTACHMENT_EMPTY", "0-byte attachment"),
    ]
    for i, (code, reason) in enumerate(doctor):
        y = 400 + i * 21
        parts.append(f'<rect x="60" y="{y - 9}" width="4" height="4" '
                     f'rx="1" fill="{accent}"/>')
        require_svg(code, 13, "mono", 232, f"doctor code {code}", weight=400)
        require_svg(reason, 11.5, "sans", 120, f"doctor reason {reason}")
        parts.append(t(76, y, code, 13, s["text"], "mono"))
        parts.append(t(508, y, reason, 11.5, s["faint"], "sans", 400, "end"))

    parts.append(line(60, 476, 508, 476, s["rule"], 1))
    parts.append(t(60, 492, "legal.conflict_check", 13, s["text"], "mono",
                   700))
    parts.append(t(508, 492, "separate parties input · R0", 11, s["faint"],
                   "sans", 400, "end"))
    conflict_lines = [
        "new_parties[] × existing[ matter_id, parties[] ]",
        "same name, opposite sides → conflicts[]",
        "one name as client + adverse → E_LEGAL_PARTY_BOTH_SIDES",
    ]
    for i, cline in enumerate(conflict_lines):
        require_svg(cline, 11.5, "sans", 448, f"conflict line {i}")
        parts.append(t(60, 510 + i * 18, cline, 11.5, s["sub"], "sans"))
    conflict_note = "names normalised: trim · lowercase · spaces collapsed"
    require_svg(conflict_note, 11, "sans", 448, "conflict note")
    parts.append(t(60, 562, conflict_note, 11, s["faint"], "sans"))

    # ---- 03 write gate ---------------------------------------------------
    parts.append(r(548, 314, 508, 264, s["card"], accent, 1.8, 18,
                   shadow=True))
    parts.append(t(564, 344, "03", 12, accent, "mono", 700))
    parts.append(t(590, 344, "R1 · LOCAL WRITE", 13, accent, "sans", 700,
                   tracking=0.6))
    parts.append(t(1040, 344, "legal.intake → legal.export_ledger", 11,
                   s["faint"], "sans", 400, "end"))
    parts.append(line(564, 356, 1040, 356, s["rule"], 1))

    # dedupe
    parts.append(t(564, 376, "DEDUPE", 11, accent, "sans", 700,
                   tracking=1.2))
    parts.append(t(792, 376, "seen(Message-ID)", 11, s["faint"], "mono", 400,
                   "end"))
    parts.append(t(564, 404, "3", 22, s["text"], "mono", 700))
    parts.append(t(584, 404, "→", 13, s["faint"], "mono"))
    parts.append(t(604, 404, "2", 24, accent, "mono", 700))
    parts.append(t(632, 404, "new", 11.5, s["sub"], "sans", 700))
    dedupe_note = "1 duplicate · counted, never stored"
    require_svg(dedupe_note, 11.5, "sans", 222, "dedupe note")
    parts.append(t(564, 426, dedupe_note, 11.5, s["sub"], "sans"))

    parts.append(line(564, 442, 792, 442, s["rule"], 1))
    parts.append(t(564, 462, "CLASSIFY", 11, accent, "sans", 700,
                   tracking=1.2))
    parts.append(t(792, 462, "first match wins", 11, s["faint"], "sans", 400,
                   "end"))
    types = [("NDA", "1"), ("MSA", "1"), ("CONTRACT_REVIEW", "0"),
             ("DISPUTE", "0"), ("COMPLIANCE", "0"), ("OTHER", "0")]
    for i, (tname, count) in enumerate(types):
        y = 482 + i * 16.4
        require_svg(tname, 13, "mono", 180, f"type {tname}")
        parts.append(t(564, y, str(i + 1), 11, s["faint"], "mono"))
        parts.append(t(580, y, tname, 13, s["text"], "mono"))
        parts.append(t(792, y, count, 11.5,
                       accent if count == "1" else s["faint"], "mono",
                       700 if count == "1" else 400, "end"))

    # store + export
    parts.append(t(816, 376, "REQUESTS", 11, accent, "sans", 700,
                   tracking=1.2))
    parts.append(t(1040, 376, "legal domain v1 · 10 fields", 11, s["faint"],
                   "sans", 400, "end"))
    records = [
        ("MSA request - Project Atlas rollout", "req_455da4f6c27e",
         "MSA · new · 1 att", 386),
        ("NDA review request - Project Atlas", "req_f07404d28828",
         "NDA · new · 2 att", 446),
    ]
    for subject, rid, meta, y in records:
        parts.append(r(816, y, 224, 52, s["tint"], s["edge"], 1.2, 12))
        parts.append(t(828, y + 16, trunc_svg(subject, 11, "sans", 196),
                       11, s["text"], "sans"))
        parts.append(t(828, y + 31, rid, 11, s["faint"], "mono"))
        parts.append(t(828, y + 45, meta, 11, s["sub"], "sans"))

    parts.append(line(794, 398, 808, 398, accent, 1.2, "3 3", 0.7))
    parts.append(f'<path d="M806 394L812 398L806 402Z" fill="{accent}"/>')

    parts.append(r(816, 510, 224, 60, s["accent_soft"], accent, 1.2, 12))
    parts.append(t(828, 532, "intake-ledger.xlsx", 11.5, accent, "mono", 700))
    parts.append(t(828, 548, "sheet Requests · 2 rows", 11, s["sub"], "sans"))
    parts.append(t(828, 562, "$DSH_LEGAL_HOME/exports/", 11, s["faint"],
                   "mono"))

    # ---- footer ----------------------------------------------------------
    parts.append(line(44, 588, 1056, 588, accent, 1.2, "4 6", 0.35))
    facts = [
        ("source read-only", "EML and manifest never modified", 44),
        ("no network", "no model call", 452),
        ("writes only", "exports/ + legal.requests", 760),
    ]
    for label, detail, fx in facts:
        parts.append(f'<circle cx="{fx + 4}" cy="602" r="3" fill="{accent}"/>')
        parts.append(t(fx + 14, 606, label, 11.5, s["text"], "sans", 700))
        lw = measure(label, 11.5, "cjk_bold")
        parts.append(t(fx + 14 + lw + 6, 606, detail, 11, s["faint"], "sans"))

    tools_line = ("R0 legal.intake_doctor · legal.conflict_check      "
                  "R1 legal.intake · legal.export_ledger")
    require_svg(tools_line, 11, "mono", 700, "footer tools")
    parts.append(t(44, 630, tools_line, 11, s["faint"], "mono"))
    parts.append(t(1056, 630, "request_id = req_ + sha256(Message-ID)[:12]",
                   11, s["faint"], "mono", 400, "end"))
    parts.append(t(44, 650, "0.1.0 · Apache-2.0 · synthetic sample only",
                   11, s["faint"], "sans"))
    parts.append(t(1056, 650,
                   "samples/quickstart/expected/result.json · 3 EML → "
                   "2 rows", 11, s["faint"], "sans", 400, "end"))

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# 3. main
# ---------------------------------------------------------------------------
def main() -> None:
    for skin in ("light", "dark"):
        for lang in ("zh", "en"):
            hero(lang, skin)
        svg = flow_svg(skin)
        try:
            ET.fromstring(svg)
        except ET.ParseError as exc:
            raise SystemExit(f"FATAL: flow SVG is not well-formed: {exc}")
        path = os.path.join(OUT, f"{NAME}-flow-v5-{skin}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(svg)
        print(f"wrote {os.path.basename(path)}")
    print("wrote 4 hero webp + 2 flow svg to docs/assets/")


if __name__ == "__main__":
    main()
