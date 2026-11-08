# GAMMA2D_HOST_V3
"""
_webview_host.py — Host per pywebview (backend Qt)
Generato automaticamente da gamma_editor.py.

Uso:
    python _webview_host.py <percorso_file.html> [--debug]

Variabili d'ambiente:
    GAMMA2D_TITLE  Titolo finestra (default: "gamma-2d — Anteprima")
"""
import sys
import os
import pathlib

try:
    import webview
except ImportError:
    print("ERRORE: pywebview non installato. Esegui:", file=sys.stderr)
    print('    pip install "pywebview[qt]"', file=sys.stderr)
    sys.exit(1)

if len(sys.argv) < 2:
    print("Uso: python _webview_host.py <file.html> [--debug]", file=sys.stderr)
    sys.exit(1)

html_path = pathlib.Path(sys.argv[1]).resolve()
debug = "--debug" in sys.argv

if not html_path.exists():
    print(f"ERRORE: file HTML non trovato: {html_path}", file=sys.stderr)
    sys.exit(1)
if html_path.stat().st_size < 200:
    print("ERRORE: file HTML sospetto (troppo piccolo).", file=sys.stderr)
    sys.exit(1)

try:
    head = html_path.read_text(encoding="utf-8", errors="replace")[:500]
except OSError as e:
    print(f"ERRORE lettura HTML: {e}", file=sys.stderr)
    sys.exit(1)

if "<!DOCTYPE" not in head and "<html" not in head.lower():
    print("ERRORE: il file non sembra HTML valido.", file=sys.stderr)
    sys.exit(1)

file_uri = html_path.as_uri()
print(f"[webview_host] carico: {file_uri} debug={debug}", file=sys.stderr)

base_title = os.environ.get("GAMMA2D_TITLE", "gamma-2d — Anteprima")
title = base_title
if debug and "DevTools" not in title:
    title += "  (DevTools: F12)"

webview.create_window(title, url=file_uri, width=940, height=700, resizable=True)

try:
    webview.start(gui="qt", debug=debug)
except Exception as e:
    print(f"[webview_host] backend qt non disponibile ({e}); provo auto.", file=sys.stderr)
    webview.start(debug=debug)
