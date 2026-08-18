#!/usr/bin/env bash
# Ensures a working Python venv with weasyprint + markdown exists, and that
# weasyprint's native dependencies (pango/cairo/glib) are installed.
# Idempotent: safe to run before every conversion, does nothing if already set up.
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$SKILL_DIR/.venv"

# macOS's system /usr/bin/python3 is SIP-protected and strips DYLD_LIBRARY_PATH,
# which breaks weasyprint's ability to find pango/cairo even if installed via
# Homebrew. A Homebrew-built Python avoids this entirely.
PYBIN="/opt/homebrew/bin/python3"
if [ ! -x "$PYBIN" ]; then
  PYBIN="/usr/local/bin/python3"  # Intel Homebrew prefix
fi
if [ ! -x "$PYBIN" ]; then
  PYBIN="python3"  # last resort, may hit the SIP issue on macOS
fi

if [ ! -x "$VENV/bin/python3" ]; then
  "$PYBIN" -m venv "$VENV"
  "$VENV/bin/pip" install --quiet --upgrade pip
  "$VENV/bin/pip" install --quiet weasyprint markdown
fi

# Verify weasyprint can actually load (catches missing native libs early
# instead of failing deep inside the conversion script).
if ! "$VENV/bin/python3" -c "import weasyprint" >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then
    echo "weasyprint's native dependencies are missing — installing via Homebrew (pango, cairo, glib)..." >&2
    brew install --quiet pango cairo glib >&2
  else
    echo "Error: weasyprint failed to load and Homebrew is not available to install pango/cairo/glib." >&2
    echo "Install them manually, then re-run." >&2
    exit 1
  fi
  if ! "$VENV/bin/python3" -c "import weasyprint" >/dev/null 2>&1; then
    echo "Error: weasyprint still fails to load after installing native dependencies." >&2
    exit 1
  fi
fi

echo "$VENV/bin/python3"
