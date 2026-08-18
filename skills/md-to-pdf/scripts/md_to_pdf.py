#!/usr/bin/env python3
"""
Convert a Markdown file to a clean, print-ready PDF.

Deterministic, no LLM involved — same input always produces the same output.
Designed to be called by the md-to-pdf skill; see SKILL.md for how Claude
resolves human-language colors ("burgundy", "UZH blue") to a hex value
before calling this script.

Usage:
    python3 md_to_pdf.py INPUT.md [OUTPUT.pdf] [--accent "#0028A5"] [--title "Custom Title"]

Behavior:
- No --accent given -> pure black/grayscale document (headings, table
  headers, blockquote rule, code borders all render in black/gray).
- --accent given     -> that hex color is used for headings, table header
  background/text, and blockquote rule. A lighter tint (auto-derived by
  blending with white) is used for zebra-striping and header backgrounds.
- Table rows never split across a page break (page-break-inside: avoid).
- Every page gets a centered footer: "N / total".
- Trailing "\" line breaks (common in hand-written docs, e.g. "Text\") are
  normalized to proper Markdown hard breaks before conversion, since
  python-markdown's core parser does not recognize a bare trailing
  backslash and would otherwise render it as a literal character.
"""

import argparse
import re
import sys
from pathlib import Path

import markdown
from weasyprint import CSS, HTML


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*(max(0, min(255, round(c))) for c in rgb))


def lighten(hex_color, amount):
    """Blend a color toward white. amount=0 -> unchanged, amount=1 -> white."""
    r, g, b = hex_to_rgb(hex_color)
    r = r + (255 - r) * amount
    g = g + (255 - g) * amount
    b = b + (255 - b) * amount
    return rgb_to_hex((r, g, b))


def build_css(accent):
    if accent:
        heading_color = accent
        rule_color = accent
        header_bg = lighten(accent, 0.90)
        zebra_bg = lighten(accent, 0.96)
    else:
        heading_color = "#111111"
        rule_color = "#111111"
        header_bg = "#eeeeee"
        zebra_bg = "#fafafa"

    return CSS(string=f"""
@page {{
  size: A4;
  margin: 2.2cm 2cm 2.4cm 2cm;
  @bottom-center {{
    content: counter(page) " / " counter(pages);
    font-family: "Helvetica Neue", Arial, sans-serif;
    font-size: 9px;
    color: #888;
  }}
}}

html, body {{
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 10.5px;
  line-height: 1.5;
  color: #222;
}}

h1 {{
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 14px;
  padding-bottom: 8px;
  border-bottom: 2px solid {rule_color};
  color: {heading_color};
}}

h2 {{
  font-size: 14px;
  font-weight: 700;
  margin: 22px 0 8px;
  padding-top: 4px;
  color: {heading_color};
  break-after: avoid;
}}

h3 {{
  font-size: 11.5px;
  font-weight: 700;
  margin: 16px 0 6px;
  color: #111;
  break-after: avoid;
}}

p {{
  margin: 0 0 8px;
}}

hr {{
  border: none;
  border-top: 1px solid #ddd;
  margin: 18px 0;
}}

ul, ol {{
  margin: 0 0 8px;
  padding-left: 20px;
}}

li {{
  margin: 0 0 3px;
}}

code {{
  font-family: "SFMono-Regular", Menlo, Consolas, monospace;
  font-size: 9.5px;
  background: #f2f2f2;
  padding: 1px 4px;
  border-radius: 2px;
}}

pre {{
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  padding: 10px 12px;
  font-size: 9px;
  line-height: 1.45;
  overflow-wrap: break-word;
  white-space: pre-wrap;
  break-inside: avoid;
  margin: 0 0 10px;
}}

pre code {{
  background: none;
  padding: 0;
}}

blockquote {{
  margin: 0 0 10px;
  padding: 6px 12px;
  border-left: 3px solid {rule_color};
  background: {zebra_bg};
  color: #333;
  break-inside: avoid;
}}

strong {{
  font-weight: 700;
}}

table {{
  width: 100%;
  border-collapse: collapse;
  margin: 6px 0 14px;
  font-size: 9.5px;
}}

thead {{
  display: table-header-group;
}}

tr {{
  break-inside: avoid;
  page-break-inside: avoid;
}}

th, td {{
  border: 1px solid #d6d6d6;
  padding: 5px 8px;
  text-align: left;
  vertical-align: top;
}}

th {{
  background: {header_bg};
  font-weight: 700;
  color: {heading_color};
}}

tbody tr:nth-child(even) {{
  background: {zebra_bg};
}}
""")


def _normalize_hard_breaks(md_text):
    """Turn trailing-backslash line breaks into Markdown hard breaks.

    python-markdown's core parser doesn't recognize a bare trailing "\\" and
    would print it literally, so it becomes the standard two-trailing-spaces
    syntax instead.

    Fenced code blocks are deliberately skipped: a trailing "\\" there is a
    shell line continuation, and rewriting it silently corrupts the command
    for anyone copying it out of the PDF.
    """
    fence_open = re.compile(r"(`{3,}|~{3,})")
    out, fence = [], None

    for line in md_text.split("\n"):
        stripped = line.lstrip()

        if fence is None:
            opening = fence_open.match(stripped)
            if opening:
                fence = opening.group(1)
                out.append(line)
            else:
                out.append(re.sub(r"\\$", "  ", line))
            continue

        closing = re.match(r"(`{3,}|~{3,})[ \t]*$", stripped)
        if closing and closing.group(1)[0] == fence[0] and len(closing.group(1)) >= len(fence):
            fence = None
        out.append(line)

    return "\n".join(out)


def convert(input_path, output_path, accent=None, title=None):
    md_text = Path(input_path).read_text(encoding="utf-8")

    md_text = _normalize_hard_breaks(md_text)

    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "sane_lists"],
    )

    doc_title = title or Path(input_path).stem
    html_doc = f"""<!doctype html>
<html lang="de">
<head><meta charset="utf-8"><title>{doc_title}</title></head>
<body>
{html_body}
</body>
</html>
"""

    HTML(string=html_doc, base_url=str(Path(input_path).parent)).write_pdf(
        output_path, stylesheets=[build_css(accent)]
    )


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to a print-ready PDF.")
    parser.add_argument("input", help="Path to the source .md file")
    parser.add_argument("output", nargs="?", help="Path to the output .pdf file (default: same name as input)")
    parser.add_argument("--accent", help="Hex accent color, e.g. '#0028A5'. Omit for a black/grayscale document.")
    parser.add_argument("--title", help="Override the HTML <title> (defaults to the input filename)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else input_path.with_suffix(".pdf")

    if args.accent and not re.match(r"^#?[0-9a-fA-F]{3}([0-9a-fA-F]{3})?$", args.accent):
        print(f"Error: --accent must be a hex color like '#0028A5', got: {args.accent}", file=sys.stderr)
        sys.exit(1)
    accent = args.accent if not args.accent or args.accent.startswith("#") else f"#{args.accent}"

    convert(input_path, output_path, accent=accent, title=args.title)
    print(f"PDF written to {output_path}")


if __name__ == "__main__":
    main()
