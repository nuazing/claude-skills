---
name: md-to-pdf
description: Converts a Markdown (.md) file into a clean, print-ready PDF with consistent styling — table rows never split across a page break, and every page gets a "N / total" footer. Use this skill whenever the user wants a Markdown file, README, or written documentation turned into a PDF, exported as PDF, or "als PDF" — even if they don't explicitly say "convert" or name this skill. Supports an optional accent color (hex code like "#0028A5" or a descriptive name like "burgundy" / "UZH blue") used for headings, table headers, and rules; without a color the PDF renders in black/grayscale only. Runs via a bundled Python script for fast, deterministic, low-token conversions — do not hand-roll a new markdown-to-PDF pipeline when this skill is available.
---

# Markdown → PDF

Converts a `.md` file to a PDF using a bundled script (`scripts/md_to_pdf.py`). The script is fully deterministic and handles all styling — **do not** re-derive the HTML/CSS conversion approach from scratch, and do not read the script's full source unless something breaks. Just call it.

## Why a script instead of writing HTML/CSS each time

A markdown-to-PDF conversion built from scratch tends to eyeball table-row splitting and footer page numbers freshly every time, burning tokens on trial-and-error PNG-rendered QA passes. The script already gets this right (`page-break-inside: avoid` on table rows, a `@bottom-center` page-number footer, A4 margins, consistent typography) — reuse it and skip the iteration.

## Usage

### 1. Ensure the environment is ready (first run only, cheap after that)

```bash
PYTHON=$(bash ~/.claude/skills/md-to-pdf/scripts/setup_env.sh)
```

This creates a persistent venv at `~/.claude/skills/md-to-pdf/.venv` with `weasyprint` + `markdown` installed, using Homebrew's Python (not macOS's SIP-protected system Python, which silently breaks weasyprint's ability to find its native pango/cairo libraries). Installs Homebrew's `pango`/`cairo`/`glib` too if missing. Idempotent — on every run after the first, this is a near-instant no-op that just prints the venv's python path.

### 2. Run the conversion

```bash
"$PYTHON" ~/.claude/skills/md-to-pdf/scripts/md_to_pdf.py INPUT.md [OUTPUT.pdf] [--accent "#0028A5"] [--title "Custom Title"]
```

- `OUTPUT.pdf` is optional — defaults to `INPUT.pdf` next to the source file.
- Omit `--accent` entirely unless the user actually asked for a color — the default is a plain black/grayscale document.

### Resolving the accent color

The script only accepts a hex code. If the user names a color in words instead of giving a hex code (e.g. "burgundy", "UZH blue", "forest green", "in Firmenrot"), **you** pick a sensible, reasonably saturated hex value for it and pass that — don't ask the user to look up a hex code themselves unless their description is genuinely ambiguous. If they give you a hex code directly, pass it through unchanged. If they don't mention color at all, don't pass `--accent`.

The accent tints headings, the h1 rule, table headers, and blockquote rules; a lighter auto-derived tint (blended toward white) is used for table zebra-striping. You don't need to compute the tint yourself — the script does that.

### After conversion

Report the output path and page count back to the user; you generally do **not** need to render the PDF to PNG and visually inspect it (that's the expensive part this skill exists to skip). Only fall back to a visual check (`pdftoppm -r 130 -png file.pdf preview` then read the PNGs) if the source Markdown has something unusual the CSS might not handle well — e.g. very wide tables, deeply nested lists, or the user reports something looks wrong.

## Known source-formatting quirk handled automatically

Docs that use a trailing `\` for a manual line break (e.g. `Dokumentation zu\` on its own line) get normalized automatically by the script — python-markdown's core parser doesn't recognize a bare trailing backslash and would otherwise print it as a literal character. No action needed on your end.

**Fenced code blocks are exempt from this.** A trailing `\` inside ``` or ~~~ fences is a shell line continuation, so the script leaves it alone — multi-line commands survive into the PDF and still work when copied out.

The one gap: **indented** code blocks (four leading spaces instead of a fence) are *not* exempt — their trailing backslashes still get rewritten. Telling them apart from list-continuation lines needs real block parsing, and guessing wrong would break hard breaks inside lists. If a doc shows a multi-line shell command, put it in a fence.

## Example

```bash
PYTHON=$(bash ~/.claude/skills/md-to-pdf/scripts/setup_env.sh)
"$PYTHON" ~/.claude/skills/md-to-pdf/scripts/md_to_pdf.py \
  ./docs/Steckbrief_doc.md \
  --accent "#0028A5"
```
