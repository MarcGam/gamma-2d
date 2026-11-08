"""
gamma-2d Editor — versione con auto-rigenerazione dell'offuscato
================================================================
Novità rispetto alla versione precedente:
- Controllo "freschezza" di gamma-2d_ob.js vs gamma-2d.js
- Pulsante "🔒 Rigenera off" (Ctrl+B) e voce di menu
- All'export offuscato, propone di rigenerare se il file è vecchio
- Test post-rigenerazione: verifica presenza di GRAVITY, Sprite, Vector…
- Avviso se npx/javascript-obfuscator non sono disponibili
- Status bar mostra ⚠️ se l'offuscato è vecchio

Requisiti:
    python3 -m venv .venv
    source .venv/bin/activate
    pip install "pywebview[qt]"
    # per l'offuscamento serve Node + npx nel PATH
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pathlib, sys, base64, mimetypes, re, os, webbrowser, tempfile, subprocess, json, shutil

try:
    import webview
    HAS_PYWEBVIEW = True
except ImportError:
    HAS_PYWEBVIEW = False


# ============================================================
# CONFIGURAZIONE
# ============================================================
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return pathlib.Path(sys.executable).parent
    return pathlib.Path(__file__).parent


CURRENT_DIR = get_base_dir()
OBFUSCATED_FILE = 'gamma-2d_ob.js'
PLAIN_FILE      = 'gamma-2d.js'
MINIFIED_FILE   = 'gamma-2d.min.js'
ASSETS_DIR      = CURRENT_DIR / 'assets'

DOCS_HTML_CANDIDATES = [
    'DOCUMENTAZIONE.html', 'DOCUMENTATION.html',
    'DOCS.html', 'docs.html', 'documentation.html',
]
DOCS_MD_CANDIDATES = ['DOCUMENTATION.md', 'DOCS.md', 'README.md']

IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg')
AUDIO_EXTS = ('.mp3', '.wav', '.ogg', '.m4a', '.aac')
ALL_EXTS   = IMAGE_EXTS + AUDIO_EXTS

WEBVIEW_HOST_FILENAME = '_webview_host.py'
CONFIG_FILE = pathlib.Path.home() / '.gamma2d_editor.json'
AUTOSAVE_INTERVAL_MS = 60_000

# Simboli che DEVONO esistere in gamma-2d_ob.js dopo la rigenerazione.
# Se ne manca anche uno solo, avvisiamo l'utente che qualcosa è andato storto.
OBF_SANITY_SYMBOLS = ['GRAVITY', 'Gravity', 'Vector', 'Sprite', 'eSprite', 'Rect']

# Opzioni passate a javascript-obfuscator (versione minimale e affidabile)
OBFUSCATOR_ARGS = [
    'javascript-obfuscator',
    'gamma-2d.js',
    '--output', 'gamma-2d_ob.js',
    '--compact', 'true',
]


# ============================================================
# TEMI
# ============================================================
THEMES = {
    'dark': {
        'bg': '#1e1e1e', 'fg': '#d4d4d4', 'cursor': '#aeafad',
        'selection': '#264f78', 'linenum_bg': '#1e1e1e', 'linenum_fg': '#666666',
        'keyword': '#569cd6', 'builtin': '#4ec9b0', 'string': '#ce9178',
        'comment': '#6a9955', 'number': '#b5cea8', 'fn': '#dcdcaa',
        'match_bg': '#404040', 'current_match_bg': '#f4a742',
        'bracket_bg': '#44475a', 'menu_bg': '#252526', 'menu_fg': '#ffffff',
        'menu_active': '#094771', 'status_bg': '#007acc', 'status_fg': '#ffffff',
        'sidebar_bg': '#252526', 'sidebar_fg': '#cccccc', 'sidebar_sel': '#094771',
        'toolbar_bg': '#2d2d30',
    },
    'light': {
        'bg': '#ffffff', 'fg': '#1f1f1f', 'cursor': '#000000',
        'selection': '#b3d7ff', 'linenum_bg': '#f3f3f3', 'linenum_fg': '#999999',
        'keyword': '#0000ff', 'builtin': '#267f99', 'string': '#a31515',
        'comment': '#008000', 'number': '#098658', 'fn': '#795e26',
        'match_bg': '#fff3a0', 'current_match_bg': '#ffb347',
        'bracket_bg': '#c8e6ff', 'menu_bg': '#f5f5f5', 'menu_fg': '#000000',
        'menu_active': '#cce8ff', 'status_bg': '#007acc', 'status_fg': '#ffffff',
        'sidebar_bg': '#f3f3f3', 'sidebar_fg': '#1f1f1f', 'sidebar_sel': '#b3d7ff',
        'toolbar_bg': '#e8e8e8',
    },
}


# ============================================================
# STARTER / SNIPPET / AUTOCOMPLETE
# ============================================================
STARTER_CODE = """function setup() {
    createMiniCanvas(800, 600);
}

function draw() {
    background(30, 30, 40);
}
"""

SNIPPETS = {
    'for':     'for (let i = 0; i < 10; i++) {\n    \n}',
    'if':      'if (condizione) {\n    \n}',
    'while':   'while (condizione) {\n    \n}',
    'func':    'function nome() {\n    \n}',
    'sprite':  "const s = new Sprite(ASSETS['sprite.png'], 100, 100, 32, 32);",
    'rect':    'const r = new Rect(100, 100, 50, 50);',
    'ellipse': 'const e = new Ellipse(100, 100, 50, 50);',
    'button':  "const b = new Button(100, 100, 120, 40, 'Click');",
    'sound':   "const s = new Sound(ASSETS['sound.mp3']);",
    'vector':  'const v = new Vector(0, 0);',
}

AUTOCOMPLETE_WORDS = sorted(set([
    'break','case','catch','class','const','continue','default','delete',
    'do','else','export','extends','finally','for','function','if','import',
    'in','instanceof','let','new','return','static','super','switch','this',
    'throw','try','typeof','var','void','while','with','yield','async','await',
    'of','get','set','true','false','null','undefined',
    'Math','Object','Array','String','Number','Boolean','Date','JSON',
    'Promise','console','window','document','performance',
    'requestAnimationFrame','setTimeout','clearTimeout',
    'Vector','Gravity','GRAVITY','Sprite','Rect','Ellipse','Button','Sound','eSprite',
    'createMiniCanvas','background','fill','stroke','noStroke','strokeWeight',
    'clear','text','textSize','textAlign','textBaseline','textWidth',
    'keyIsDown','keyWasReleased','mouseX','mouseY','mousePressed',
    'map','constrain','randomInt','dist','shuffle','extractRandom',
    'getSpriteByName','getSpritesByTag','collidesWithGroup',
    'debugMode','frameRate','getFrameRate',
    'ASSETS','getAsset',
    'setup','draw','keyPressed','keyReleased','mouseClicked',
]))


# ============================================================
# HELPER: WEBVIEW HOST
# ============================================================
WEBVIEW_HOST_MARKER = "# GAMMA2D_HOST_V3"

WEBVIEW_HOST_CODE = WEBVIEW_HOST_MARKER + '''
"""_webview_host.py — Host per pywebview (backend Qt) — auto-generato."""
import sys, os, pathlib

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

title = "gamma-2d — Anteprima" + ("  (DevTools: F12)" if debug else "")
webview.create_window(title, url=file_uri, width=940, height=700, resizable=True)

try:
    webview.start(gui="qt", debug=debug)
except Exception as e:
    print(f"[webview_host] backend qt non disponibile ({e}); provo auto.", file=sys.stderr)
    webview.start(debug=debug)
'''


def ensure_webview_host():
    path = CURRENT_DIR / WEBVIEW_HOST_FILENAME
    needs_write = True
    if path.exists():
        try:
            if WEBVIEW_HOST_MARKER in path.read_text(encoding='utf-8', errors='ignore'):
                needs_write = False
        except Exception:
            pass
    if needs_write:
        path.write_text(WEBVIEW_HOST_CODE, encoding='utf-8')
    return path


# ============================================================
# HELPER: FILE / DOCS / ASSET
# ============================================================
def find_lib(name):
    p = CURRENT_DIR / name
    return p if p.exists() else None


def find_docs_html():
    for name in DOCS_HTML_CANDIDATES:
        p = CURRENT_DIR / name
        if p.exists():
            return p
    return None


def find_docs_md():
    for name in DOCS_MD_CANDIDATES:
        p = CURRENT_DIR / name
        if p.exists():
            return p
    return None


def file_to_base64(path):
    mime, _ = mimetypes.guess_type(str(path))
    if not mime:
        ext = path.suffix.lower()
        fb = {'.mp3':'audio/mpeg','.wav':'audio/wav','.ogg':'audio/ogg',
              '.m4a':'audio/mp4','.aac':'audio/aac','.svg':'image/svg+xml',
              '.webp':'image/webp'}
        mime = fb.get(ext, 'application/octet-stream')
    with open(path, 'rb') as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"


def build_html(game_code, lib_path):
    lib_code = lib_path.read_text(encoding='utf-8')
    assets_js = 'const ASSETS = {};\n'
    n = 0
    if ASSETS_DIR.exists():
        for f in sorted(ASSETS_DIR.iterdir(), key=lambda p: p.name.lower()):
            if f.is_file() and f.suffix.lower() in ALL_EXTS:
                assets_js += f"ASSETS['{f.name}'] = '{file_to_base64(f)}';\n"
                n += 1

    def safe(s):
        return s.replace('</script>', '<\\/script>').replace('</SCRIPT>', '<\\/SCRIPT>')

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>gamma-2d Preview</title>
<style>
    body {{ margin: 0; background: #1a1a1a; display: flex;
            justify-content: center; align-items: center;
            min-height: 100vh; font-family: sans-serif; }}
    canvas {{ box-shadow: 0 0 24px rgba(0,0,0,0.6); border-radius: 4px; }}
</style>
</head><body><script>
{safe(assets_js)}
function getAsset(p) {{
    if (!p || typeof p !== 'string') return p;
    if (p.startsWith('data:')) return p;
    const n = p.split('/').pop();
    return ASSETS[n] || p;
}}
{safe(lib_code)}
{safe(game_code)}
</script></body></html>"""
    return html, n


# ============================================================
# HELPER: OFFUSCAMENTO
# ============================================================
def check_obfuscator_available():
    """Ritorna (ok, tool_name)."""
    for tool in ('npx', 'javascript-obfuscator'):
        if shutil.which(tool):
            return True, tool
    return False, None


def obfuscated_freshness():
    """
    Ritorna un dict con lo stato di gamma-2d_ob.js rispetto a gamma-2d.js:
      {
        'ob_exists': bool,
        'src_exists': bool,
        'stale': bool,       # True se ob è più vecchio di src
        'missing': bool,     # True se ob non esiste
        'ob_age_h': float,
        'src_age_h': float,
        'ob_has_all_symbols': bool,  # controllo GRAVITY etc.
        'missing_symbols': [str],
      }
    """
    src = CURRENT_DIR / PLAIN_FILE
    ob = CURRENT_DIR / OBFUSCATED_FILE

    info = {
        'ob_exists': ob.exists(),
        'src_exists': src.exists(),
        'stale': False,
        'missing': not ob.exists(),
        'ob_age_h': None,
        'src_age_h': None,
        'ob_has_all_symbols': False,
        'missing_symbols': [],
    }

    if src.exists():
        info['src_age_h'] = (pathlib.Path().stat().st_mtime - src.stat().st_mtime) / 3600 if False else (
            __import__('time').time() - src.stat().st_mtime) / 3600

    if ob.exists():
        info['ob_age_h'] = (__import__('time').time() - ob.stat().st_mtime) / 3600

    # Stale se ob esiste ma è più vecchio di src (tolleranza 5 secondi)
    if src.exists() and ob.exists():
        if ob.stat().st_mtime < src.stat().st_mtime - 5:
            info['stale'] = True

    # Sanity check: l'offuscato contiene i simboli chiave?
    if ob.exists():
        try:
            content = ob.read_text(encoding='utf-8', errors='ignore')
            missing = [s for s in OBF_SANITY_SYMBOLS if s not in content]
            info['missing_symbols'] = missing
            info['ob_has_all_symbols'] = len(missing) == 0
        except Exception:
            info['missing_symbols'] = list(OBF_SANITY_SYMBOLS)

    return info


def regenerate_obfuscated(timeout=90):
    """
    Esegue npx javascript-obfuscator gamma-2d.js → gamma-2d_ob.js
    Ritorna (success: bool, message: str, stdout: str, stderr: str).
    """
    src = CURRENT_DIR / PLAIN_FILE
    if not src.exists():
        return False, f"File {PLAIN_FILE} non trovato.", '', ''

    ok, tool = check_obfuscator_available()
    if not ok:
        return False, (
            "Node.js / npx non trovati nel PATH.\n\n"
            "Installa Node.js (es. `sudo apt install nodejs npm`)\n"
            "oppure esporta in chiaro (Ctrl+E)."
        ), '', ''

    cmd = (['npx'] if tool == 'npx' else []) + OBFUSCATOR_ARGS

    try:
        result = subprocess.run(
            cmd,
            cwd=str(CURRENT_DIR),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, f"Timeout ({timeout}s) durante l'offuscamento.", '', ''
    except FileNotFoundError:
        return False, "Impossibile eseguire npx/javascript-obfuscator.", '', ''
    except Exception as e:
        return False, f"Errore durante l'esecuzione: {e}", '', ''

    stdout = result.stdout or ''
    stderr = result.stderr or ''

    if result.returncode != 0:
        return False, f"javascript-obfuscator è uscito con codice {result.returncode}.", stdout, stderr

    ob = CURRENT_DIR / OBFUSCATED_FILE
    if not ob.exists():
        return False, "Offuscamento terminato ma gamma-2d_ob.js non esiste.", stdout, stderr

    # Sanity check post-rigenerazione
    try:
        content = ob.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        return False, f"Impossibile leggere gamma-2d_ob.js: {e}", stdout, stderr

    missing = [s for s in OBF_SANITY_SYMBOLS if s not in content]
    if missing:
        return False, (
            f"Offuscamento eseguito ma mancano simboli: {', '.join(missing)}.\n\n"
            f"Probabilmente il file gamma-2d.js non è aggiornato o è corrotto."
        ), stdout, stderr

    return True, "Offuscamento completato con successo.", stdout, stderr


# ============================================================
# SYNTAX HIGHLIGHTER
# ============================================================
class JSHighlighter:
    KW = {'break','case','catch','class','const','continue','default','delete',
          'do','else','export','extends','finally','for','function','if','import',
          'in','instanceof','let','new','return','static','super','switch','this',
          'throw','try','typeof','var','void','while','with','yield','async','await',
          'of','get','set','true','false','null','undefined'}
    BI = {'Math','Object','Array','String','Number','Boolean','Date','JSON',
          'Promise','Vector','Gravity','GRAVITY','Sprite','Rect','Ellipse','Button','Sound','eSprite',
          'ASSETS','console','window','document','performance',
          'requestAnimationFrame'}

    def __init__(self, text_widget, theme):
        self.t = text_widget
        self._job = None
        self.apply_theme(theme)

    def apply_theme(self, theme):
        self.t.tag_configure('keyword', foreground=theme['keyword'],
                             font=('Consolas', 11, 'bold'))
        self.t.tag_configure('builtin', foreground=theme['builtin'])
        self.t.tag_configure('string',  foreground=theme['string'])
        self.t.tag_configure('comment', foreground=theme['comment'],
                             font=('Consolas', 11, 'italic'))
        self.t.tag_configure('number',  foreground=theme['number'])
        self.t.tag_configure('fn',      foreground=theme['fn'])
        for tag in ('builtin', 'fn', 'keyword', 'number', 'string', 'comment'):
            self.t.tag_raise(tag)

    def schedule(self):
        if self._job:
            self.t.after_cancel(self._job)
        self._job = self.t.after(180, self.highlight)

    def highlight(self):
        self._job = None
        c = self.t.get('1.0', 'end-1c')
        for tag in ('keyword','builtin','string','comment','number','fn'):
            self.t.tag_remove(tag, '1.0', 'end')
        for m in re.finditer(r'\b[A-Za-z_$][A-Za-z0-9_$]*\b', c):
            w = m.group(0)
            s, e = f'1.0 + {m.start()}c', f'1.0 + {m.end()}c'
            if w in self.KW:
                self.t.tag_add('keyword', s, e)
            elif w in self.BI:
                self.t.tag_add('builtin', s, e)
            elif c[m.end():m.end()+1] == '(':
                self.t.tag_add('fn', s, e)
        for m in re.finditer(r'\b\d+(?:\.\d+)?\b', c):
            self.t.tag_add('number', f'1.0 + {m.start()}c', f'1.0 + {m.end()}c')
        for pat in (r'"(?:[^"\\]|\\.)*"', r"'(?:[^'\\]|\\.)*'", r'`(?:[^`\\]|\\.)*`'):
            for m in re.finditer(pat, c):
                self.t.tag_add('string', f'1.0 + {m.start()}c', f'1.0 + {m.end()}c')
        for m in re.finditer(r'//[^\n]*', c):
            self.t.tag_add('comment', f'1.0 + {m.start()}c', f'1.0 + {m.end()}c')
        for m in re.finditer(r'/\*.*?\*/', c, re.DOTALL):
            self.t.tag_add('comment', f'1.0 + {m.start()}c', f'1.0 + {m.end()}c')


# ============================================================
# NUMERI DI RIGA
# ============================================================
class LineNumbers(tk.Canvas):
    def __init__(self, master, text, theme):
        super().__init__(master, width=48, highlightthickness=0, bg=theme['linenum_bg'])
        self.text = text
        self._sb = None
        self._theme = theme

    def attach(self, sb):
        self._sb = sb
        self.text.configure(yscrollcommand=self._scroll)
        sb.configure(command=self.text.yview)

    def _scroll(self, f, l):
        if self._sb:
            self._sb.set(f, l)
        self.redraw()

    def apply_theme(self, theme):
        self._theme = theme
        self.configure(bg=theme['linenum_bg'])
        self.redraw()

    def redraw(self, *_):
        self.delete('all')
        i = self.text.index('@0,0')
        while True:
            d = self.text.dlineinfo(i)
            if d is None:
                break
            self.create_text(self.winfo_width() - 6, d[1], anchor='ne',
                             text=i.split('.')[0],
                             fill=self._theme['linenum_fg'],
                             font=('Consolas', 10))
            i = self.text.index(f'{i}+1line')
            if self.text.compare(i, '>=', 'end'):
                break


# ============================================================
# AUTOCOMPLETE
# ============================================================
class AutocompletePopup:
    def __init__(self, editor):
        self.editor = editor
        self.win = None
        self.listbox = None
        self.filtered = []
        self.open_pos = None

    def is_open(self):
        return self.win is not None and self.win.winfo_exists()

    def show(self, x, y, prefix=''):
        if self.is_open():
            self.close()
        self.win = tk.Toplevel(self.editor.root)
        self.win.wm_overrideredirect(True)
        self.win.configure(bg=self.editor.theme['menu_bg'])
        self.win.attributes('-topmost', True)
        self.win.geometry(f'260x180+{x}+{y}')

        self.listbox = tk.Listbox(
            self.win, height=8, font=('Consolas', 10),
            bg=self.editor.theme['menu_bg'],
            fg=self.editor.theme['menu_fg'],
            selectbackground=self.editor.theme['menu_active'],
            selectforeground='white',
            relief='flat', highlightthickness=1,
            highlightbackground=self.editor.theme['menu_active'],
        )
        self.listbox.pack(fill='both', expand=True)
        self.listbox.bind('<Double-Button-1>', self._on_click)
        self.listbox.bind('<Button-1>', self._on_click)
        self.open_pos = self.editor.text.index('insert')
        self._refresh(prefix)

    def _refresh(self, prefix):
        p = prefix.lower()
        self.filtered = [w for w in AUTOCOMPLETE_WORDS if w.lower().startswith(p)]
        if not self.filtered:
            self.close()
            return
        self.listbox.delete(0, 'end')
        for w in self.filtered[:60]:
            self.listbox.insert('end', w)
        self.listbox.selection_clear(0, 'end')
        self.listbox.selection_set(0)
        self.listbox.activate(0)

    def update_filter(self, prefix):
        if not self.is_open():
            return
        self._refresh(prefix)

    def move(self, delta):
        if not self.is_open() or not self.filtered:
            return
        cur = self.listbox.curselection()
        idx = (cur[0] if cur else 0) + delta
        idx = max(0, min(len(self.filtered) - 1, idx))
        self.listbox.selection_clear(0, 'end')
        self.listbox.selection_set(idx)
        self.listbox.activate(idx)
        self.listbox.see(idx)

    def confirm(self):
        if not self.is_open() or not self.filtered:
            return
        cur = self.listbox.curselection()
        idx = cur[0] if cur else 0
        word = self.filtered[idx]
        start = self.open_pos
        end = self.editor.text.index('insert')
        self.editor.text.delete(start, end)
        self.editor.text.insert(start, word)
        self.editor.text.mark_set('insert', f'{start}+{len(word)}c')
        self.close()

    def _on_click(self, event=None):
        self.confirm()

    def close(self):
        if self.win is not None:
            try:
                self.win.destroy()
            except tk.TclError:
                pass
            self.win = None
            self.listbox = None
            self.open_pos = None


# ============================================================
# TROVA / SOSTITUISCI
# ============================================================
class FindReplaceDialog:
    def __init__(self, editor):
        self.editor = editor
        self.text = editor.text
        self.win = None
        self.find_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        self.case_var = tk.BooleanVar(value=False)
        self.word_var = tk.BooleanVar(value=False)
        self.regex_var = tk.BooleanVar(value=False)
        self._last_match = None

    def open(self, replace=False):
        if self.win and self.win.winfo_exists():
            self.win.deiconify()
            self.win.lift()
            if replace and not self.replace_frame.winfo_ismapped():
                self.replace_frame.pack(fill='x', pady=2, after=self.row1)
            return

        self.win = tk.Toplevel(self.editor.root)
        self.win.title("Trova" + (" e sostituisci" if replace else ""))
        self.win.geometry("460x260" if replace else "460x190")
        self.win.configure(bg=self.editor.theme['bg'])
        self.win.transient(self.editor.root)

        self.row1 = tk.Frame(self.win, bg=self.editor.theme['bg'])
        self.row1.pack(fill='x', padx=8, pady=(8, 2))
        tk.Label(self.row1, text="Trova:", bg=self.editor.theme['bg'],
                 fg=self.editor.theme['fg']).pack(side='left')
        self.find_entry = tk.Entry(self.row1, textvariable=self.find_var,
                                   bg=self.editor.theme['linenum_bg'],
                                   fg=self.editor.theme['fg'],
                                   insertbackground=self.editor.theme['fg'])
        self.find_entry.pack(side='left', fill='x', expand=True, padx=4)

        self.replace_frame = tk.Frame(self.win, bg=self.editor.theme['bg'])
        row2 = tk.Frame(self.replace_frame, bg=self.editor.theme['bg'])
        row2.pack(fill='x', padx=8, pady=2)
        tk.Label(row2, text="Con:", bg=self.editor.theme['bg'],
                 fg=self.editor.theme['fg']).pack(side='left')
        tk.Entry(row2, textvariable=self.replace_var,
                 bg=self.editor.theme['linenum_bg'], fg=self.editor.theme['fg'],
                 insertbackground=self.editor.theme['fg']
                 ).pack(side='left', fill='x', expand=True, padx=4)
        if replace:
            self.replace_frame.pack(fill='x', pady=2, after=self.row1)

        opts = tk.Frame(self.win, bg=self.editor.theme['bg'])
        opts.pack(fill='x', padx=8, pady=4)
        for var, label in [(self.case_var, 'Maiuscole/minuscole'),
                           (self.word_var, 'Parola intera'),
                           (self.regex_var, 'Regex')]:
            tk.Checkbutton(opts, text=label, variable=var,
                           bg=self.editor.theme['bg'],
                           fg=self.editor.theme['fg'],
                           selectcolor=self.editor.theme['linenum_bg'],
                           activebackground=self.editor.theme['bg'],
                           activeforeground=self.editor.theme['fg']
                           ).pack(side='left', padx=4)

        btns = tk.Frame(self.win, bg=self.editor.theme['bg'])
        btns.pack(fill='x', padx=8, pady=8)
        tk.Button(btns, text="◀ Precedente", command=self.find_prev).pack(side='left', padx=2)
        tk.Button(btns, text="Successivo ▶", command=self.find_next).pack(side='left', padx=2)
        if replace:
            tk.Button(btns, text="Sostituisci", command=self.replace_one).pack(side='left', padx=2)
            tk.Button(btns, text="Sostituisci tutto", command=self.replace_all).pack(side='left', padx=2)

        self.find_entry.focus_set()
        self.win.bind('<Return>', lambda e: self.find_next())
        self.win.bind('<Shift-Return>', lambda e: self.find_prev())
        self.win.bind('<Escape>', lambda e: self.close())

    def close(self):
        self.editor._clear_find_highlight()
        if self.win and self.win.winfo_exists():
            self.win.destroy()
        self.win = None

    def _build_pattern(self):
        pat = self.find_var.get()
        if not pat:
            return None
        flags = 0 if self.case_var.get() else re.IGNORECASE
        if not self.regex_var.get():
            pat = re.escape(pat)
        if self.word_var.get():
            pat = r'\b' + pat + r'\b'
        try:
            return re.compile(pat, flags)
        except re.error as e:
            messagebox.showerror("Regex non valida", str(e))
            return None

    def _all_matches(self):
        pat = self._build_pattern()
        if not pat:
            return []
        content = self.text.get('1.0', 'end-1c')
        return [m for m in pat.finditer(content)]

    def _highlight_matches(self, matches):
        self.editor._clear_find_highlight()
        for m in matches:
            self.text.tag_add('find_match',
                              f'1.0 + {m.start()}c', f'1.0 + {m.end()}c')

    def _goto_match(self, m):
        start = f'1.0 + {m.start()}c'
        end = f'1.0 + {m.end()}c'
        self.text.tag_remove('find_current', '1.0', 'end')
        self.text.tag_add('find_current', start, end)
        self.text.mark_set('insert', end)
        self.text.see(start)
        self._last_match = (start, end)

    def find_next(self):
        matches = self._all_matches()
        if not matches:
            return
        self._highlight_matches(matches)
        cur = self.text.index('insert')
        cur_off = len(self.text.get('1.0', cur))
        for m in matches:
            if m.start() >= cur_off:
                self._goto_match(m); return
        self._goto_match(matches[0])

    def find_prev(self):
        matches = self._all_matches()
        if not matches:
            return
        self._highlight_matches(matches)
        cur = self.text.index('insert')
        cur_off = len(self.text.get('1.0', cur))
        for m in reversed(matches):
            if m.end() <= cur_off:
                self._goto_match(m); return
        self._goto_match(matches[-1])

    def replace_one(self):
        if not self._last_match:
            self.find_next(); return
        start, end = self._last_match
        self.text.delete(start, end)
        self.text.insert(start, self.replace_var.get())
        self.find_next()

    def replace_all(self):
        matches = self._all_matches()
        if not matches:
            return
        content = self.text.get('1.0', 'end-1c')
        new = content
        for m in reversed(matches):
            new = new[:m.start()] + self.replace_var.get() + new[m.end():]
        self.text.delete('1.0', 'end')
        self.text.insert('1.0', new)
        self._highlight_matches(self._all_matches())


# ============================================================
# PANNELLO ASSET
# ============================================================
class AssetPanel:
    def __init__(self, master, editor):
        self.editor = editor
        self.frame = tk.Frame(master, width=220, bg=editor.theme['sidebar_bg'])
        self.frame.pack_propagate(False)
        self._preview_photo = None

        self.title = tk.Label(self.frame, text="📁 Assets",
                              bg=editor.theme['sidebar_bg'],
                              fg=editor.theme['sidebar_fg'],
                              font=('Helvetica', 11, 'bold'))
        self.title.pack(fill='x', pady=(8, 4))

        self.listbox = tk.Listbox(
            self.frame, font=('Consolas', 10),
            bg=editor.theme['linenum_bg'],
            fg=editor.theme['sidebar_fg'],
            selectbackground=editor.theme['sidebar_sel'],
            selectforeground='white',
            relief='flat', highlightthickness=0,
        )
        self.listbox.pack(fill='both', expand=True, padx=6, pady=2)
        self.listbox.bind('<<ListboxSelect>>', self._on_select)
        self.listbox.bind('<Double-Button-1>', self._on_double)

        self.preview_label = tk.Label(
            self.frame, text="(anteprima)",
            bg=editor.theme['linenum_bg'],
            fg=editor.theme['sidebar_fg'],
            width=20, height=6,
        )
        self.preview_label.pack(fill='x', padx=6, pady=6)

        self.info_label = tk.Label(
            self.frame, text="", bg=editor.theme['sidebar_bg'],
            fg=editor.theme['sidebar_fg'],
            font=('Consolas', 9),
        )
        self.info_label.pack(fill='x', padx=6)

        self.refresh()

    def refresh(self):
        self.listbox.delete(0, 'end')
        self._assets = []
        if not ASSETS_DIR.exists():
            self.listbox.insert('end', '(cartella assets non trovata)')
            return
        for f in sorted(ASSETS_DIR.iterdir(), key=lambda p: p.name.lower()):
            if f.is_file() and f.suffix.lower() in ALL_EXTS:
                icon = '🖼' if f.suffix.lower() in IMAGE_EXTS else '🔊'
                self.listbox.insert('end', f'{icon} {f.name}')
                self._assets.append(f)

    def _on_select(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(self._assets):
            return
        f = self._assets[idx]
        self.info_label.config(text=f"{f.name}\n{f.stat().st_size / 1024:.1f} KB")
        if f.suffix.lower() in IMAGE_EXTS:
            try:
                if f.suffix.lower() in ('.png', '.gif'):
                    photo = tk.PhotoImage(file=str(f))
                    w, h = photo.width(), photo.height()
                    if w > 200:
                        ratio = 200 / w
                        photo = photo.subsample(int(1 / ratio) or 1)
                    self._preview_photo = photo
                    self.preview_label.config(image=photo, text='')
                else:
                    self.preview_label.config(image='', text=f"({f.suffix} non anteprimizzabile)")
            except Exception:
                self.preview_label.config(image='', text='(errore anteprima)')
        else:
            self.preview_label.config(image='', text='🔊 Audio')

    def _on_double(self, event=None):
        sel = self.listbox.curselection()
        if not sel or sel[0] >= len(self._assets):
            return
        f = self._assets[sel[0]]
        self.editor.text.insert('insert', f"ASSETS['{f.name}']")
        self.editor.text.focus_set()

    def apply_theme(self, theme):
        self.frame.configure(bg=theme['sidebar_bg'])
        self.title.configure(bg=theme['sidebar_bg'], fg=theme['sidebar_fg'])
        self.listbox.configure(bg=theme['linenum_bg'], fg=theme['sidebar_fg'],
                               selectbackground=theme['sidebar_sel'])
        self.preview_label.configure(bg=theme['linenum_bg'], fg=theme['sidebar_fg'])
        self.info_label.configure(bg=theme['sidebar_bg'], fg=theme['sidebar_fg'])


# ============================================================
# DOCS (fallback MD)
# ============================================================
class DocsWindow:
    def __init__(self, parent, theme):
        w = tk.Toplevel(parent)
        w.title("📚 gamma-2d — Docs (Markdown)")
        w.geometry("950x750")
        w.configure(bg=theme['bg'])

        top = tk.Frame(w, bg=theme['bg'])
        top.pack(fill='x', padx=6, pady=6)
        tk.Label(top, text="Documentazione (fallback markdown)",
                 font=('Helvetica', 11, 'bold'),
                 bg=theme['bg'], fg=theme['fg']).pack(side='left')
        tk.Button(top, text="🔗 GitHub",
                  command=lambda: webbrowser.open('https://github.com/MarcGam/gamma-2d')
                  ).pack(side='right')

        txt = scrolledtext.ScrolledText(
            w, wrap='word', font=('Consolas', 11),
            bg=theme['bg'], fg=theme['fg'], insertbackground=theme['fg'],
            relief='flat', padx=10, pady=10,
        )
        txt.pack(fill='both', expand=True)

        md_path = find_docs_md()
        if md_path:
            content = md_path.read_text(encoding='utf-8')
        else:
            content = ("Documentazione non trovata.\n\n"
                       f"Metti uno di questi file nella cartella:\n"
                       f"  • HTML: {', '.join(DOCS_HTML_CANDIDATES)}\n"
                       f"  • MD:   {', '.join(DOCS_MD_CANDIDATES)}")

        txt.insert('1.0', content)
        txt.tag_configure('h1', font=('Consolas', 18, 'bold'),
                          foreground=theme['builtin'], spacing3=12)
        txt.tag_configure('h2', font=('Consolas', 15, 'bold'),
                          foreground=theme['builtin'], spacing3=10)
        txt.tag_configure('h3', font=('Consolas', 13, 'bold'),
                          foreground=theme['fn'], spacing3=6)
        txt.tag_configure('code', font=('Consolas', 10),
                          background=theme['linenum_bg'], foreground=theme['string'])

        for m in re.finditer(r'^# (.+)$', content, re.M):
            txt.tag_add('h1', f'1.0 + {m.start()}c', f'1.0 + {m.end()}c')
        for m in re.finditer(r'^## (.+)$', content, re.M):
            txt.tag_add('h2', f'1.0 + {m.start()}c', f'1.0 + {m.end()}c')
        for m in re.finditer(r'^### (.+)$', content, re.M):
            txt.tag_add('h3', f'1.0 + {m.start()}c', f'1.0 + {m.end()}c')
        for m in re.finditer(r'`([^`\n]+)`', content):
            txt.tag_add('code', f'1.0 + {m.start()}c', f'1.0 + {m.end()}c')

        txt.config(state='disabled')


# ============================================================
# EDITOR PRINCIPALE
# ============================================================
class Editor:
    def __init__(self, root):
        self.root = root
        self.current_file = None
        self.modified = False
        self._autosave_job = None

        self.config = self._load_config()
        self.theme_name = self.config.get('theme', 'dark')
        if self.theme_name not in THEMES:
            self.theme_name = 'dark'
        self.theme = THEMES[self.theme_name]

        self.ac = AutocompletePopup(self)
        self.find_dlg = None

        root.title("gamma-2d Editor — Untitled.js")
        root.geometry(self.config.get('geometry', '1500x850'))
        root.configure(bg=self.theme['bg'])

        self._build_menu()
        self._build_toolbar()
        self._build_layout()
        self._build_status()

        root.bind('<Control-n>',       lambda e: self.new_file())
        root.bind('<Control-o>',       lambda e: self.open_file())
        root.bind('<Control-s>',       lambda e: self.save_file())
        root.bind('<Control-Shift-S>', lambda e: self.save_file_as())
        root.bind('<Control-f>',       lambda e: self._open_find(False))
        root.bind('<Control-h>',       lambda e: self._open_find(True))
        root.bind('<Control-t>',       lambda e: self.toggle_theme())
        root.bind('<Control-z>',       lambda e: self._undo())
        root.bind('<Control-y>',       lambda e: self._redo())
        root.bind('<Control-b>',       lambda e: self.regenerate_obfuscated_ui())
        root.bind('<F5>',              lambda e: self.run_webview(debug=False))
        root.bind('<Shift-F5>',        lambda e: self.run_webview(debug=True))
        root.bind('<Control-p>',       lambda e: self.run_browser())
        root.bind('<F1>',              lambda e: self.open_docs())
        root.bind('<Control-e>',       lambda e: self.export(False))
        root.bind('<Control-Shift-E>', lambda e: self.export(True))

        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self._schedule_autosave()
        self.new_file(show_starter=True)
        self.root.after(200, self._check_autosave_recovery)

    # ---------------------------------------------------------
    # CONFIG
    # ---------------------------------------------------------
    def _load_config(self):
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            return {}

    def _save_config(self):
        try:
            CONFIG_FILE.write_text(json.dumps(self.config, indent=2))
        except Exception:
            pass

    # ---------------------------------------------------------
    # TEMA
    # ---------------------------------------------------------
    def toggle_theme(self):
        self.theme_name = 'light' if self.theme_name == 'dark' else 'dark'
        self.theme = THEMES[self.theme_name]
        self.config['theme'] = self.theme_name
        self._save_config()
        self._apply_theme()

    def _apply_theme(self):
        t = self.theme
        self.root.configure(bg=t['bg'])
        self.text.configure(bg=t['bg'], fg=t['fg'], insertbackground=t['cursor'],
                            selectbackground=t['selection'])
        self.hl.apply_theme(t)
        self.text.tag_configure('find_match', background=t['match_bg'])
        self.text.tag_configure('find_current', background=t['current_match_bg'],
                                foreground='black')
        self.text.tag_configure('bracket_match', background=t['bracket_bg'])
        self.ln.apply_theme(t)
        self.asset_panel.apply_theme(t)
        self.status_label.configure(bg=t['status_bg'], fg=t['status_fg'])
        try:
            self.menubar.configure(bg=t['menu_bg'], fg=t['menu_fg'],
                                   activebackground=t['menu_active'])
            for submenu in self._submenus:
                submenu.configure(bg=t['menu_bg'], fg=t['menu_fg'],
                                  activebackground=t['menu_active'])
        except tk.TclError:
            pass
        self._retheme_toolbar()
        self.hl.highlight()

    def _retheme_toolbar(self):
        t = self.theme
        for w in self.toolbar_frame.winfo_children():
            try:
                if isinstance(w, tk.Button):
                    w.configure(bg=t['toolbar_bg'], fg=t['menu_fg'],
                                activebackground=t['menu_active'],
                                activeforeground=t['menu_fg'],
                                relief='flat', bd=0, padx=10, pady=4)
            except tk.TclError:
                pass
        self.toolbar_frame.configure(bg=t['toolbar_bg'])

    # ---------------------------------------------------------
    # DOCS
    # ---------------------------------------------------------
    def open_docs(self):
        html_path = find_docs_html()
        if html_path is not None:
            try:
                webbrowser.open(html_path.as_uri())
                self._flash(f"📚 Docs: {html_path.name}")
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile aprire {html_path.name}:\n{e}")
            return
        DocsWindow(self.root, self.theme)

    # ---------------------------------------------------------
    # OFFUSCATO — controllo freschezza + rigenerazione
    # ---------------------------------------------------------
    def regenerate_obfuscated_ui(self, parent_check=False):
        """
        Rigenera gamma-2d_ob.js dal sorgente gamma-2d.js.
        Se parent_check=True, chiede conferma prima di procedere.
        Ritorna True se ok, False altrimenti.
        """
        if parent_check:
            r = messagebox.askyesno(
                "Rigenera offuscato",
                f"Rigenerare '{OBFUSCATED_FILE}' da '{PLAIN_FILE}'?\n\n"
                f"Verrà eseguito npx javascript-obfuscator nella cartella:\n{CURRENT_DIR}\n\n"
                f"Operazione: 5–30 secondi."
            )
            if not r:
                return False

        ok, tool = check_obfuscator_available()
        if not ok:
            messagebox.showerror(
                "Node.js mancante",
                "npx e javascript-obfuscator non sono nel PATH.\n\n"
                "Installa Node.js:\n"
                "    sudo apt install nodejs npm\n\n"
                "Oppure esporta in chiaro (Ctrl+E)."
            )
            return False

        self._flash("🔒 Rigenerazione offuscato in corso… (può richiedere ~30s)")
        self.root.update_idletasks()

        success, message, stdout, stderr = regenerate_obfuscated(timeout=90)

        if success:
            # Aggiorna la status bar
            self._update_status()
            self._flash(f"✅ {OBFUSCATED_FILE} rigenerato")
            messagebox.showinfo("Fatto", message)
            return True
        else:
            details = ""
            if stderr:
                details = "\n\n--- stderr ---\n" + stderr.strip()[-800:]
            elif stdout:
                details = "\n\n--- stdout ---\n" + stdout.strip()[-800:]
            messagebox.showerror("Errore offuscamento", message + details)
            self._flash("❌ Rigenerazione fallita")
            return False

    def _ensure_obfuscated_fresh(self):
        """
        All'export offuscato, verifica che gamma-2d_ob.js sia più recente di
        gamma-2d.js. Se non lo è, propone di rigenerarlo.
        Ritorna True se si può procedere, False per annullare.
        """
        info = obfuscated_freshness()

        if info['missing']:
            r = messagebox.askyesno(
                "File offuscato mancante",
                f"'{OBFUSCATED_FILE}' non esiste.\n\n"
                f"Vuoi generarlo adesso da '{PLAIN_FILE}'?\n\n"
                f"Richiede Node.js + npx nel PATH."
            )
            if not r:
                return False
            return self.regenerate_obfuscated_ui(parent_check=False)

        if info['stale'] or not info['ob_has_all_symbols']:
            reason = []
            if info['stale']:
                reason.append(
                    f"'{OBFUSCATED_FILE}' è più vecchio di '{PLAIN_FILE}'."
                )
            if not info['ob_has_all_symbols']:
                reason.append(
                    f"Mancano simboli: {', '.join(info['missing_symbols'])}"
                )
            msg = (
                "Il file offuscato non è aggiornato:\n\n"
                + "\n".join(f"• {r}" for r in reason)
                + "\n\nVuoi rigenerarlo prima di esportare?\n\n"
                "(Sì = rigenera ora  /  No = esporta comunque il file vecchio  /  Annulla = interrompi)"
            )
            res = messagebox.askyesnocancel("Offuscato non aggiornato", msg)
            if res is None:
                return False
            if res is True:
                return self.regenerate_obfuscated_ui(parent_check=False)
            # No: esporta comunque (l'utente accetta il rischio)
            return True

        return True  # tutto fresco

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def _build_menu(self):
        mb = tk.Menu(self.root, bg=self.theme['menu_bg'], fg=self.theme['menu_fg'],
                     activebackground=self.theme['menu_active'])
        self.menubar = mb
        self._submenus = []

        m = tk.Menu(mb, tearoff=0, bg=self.theme['menu_bg'], fg=self.theme['menu_fg'],
                    activebackground=self.theme['menu_active'])
        self._submenus.append(m)
        m.add_command(label="Nuovo", accelerator="Ctrl+N", command=self.new_file)
        m.add_command(label="Apri…", accelerator="Ctrl+O", command=self.open_file)
        m.add_command(label="Salva", accelerator="Ctrl+S", command=self.save_file)
        m.add_command(label="Salva con nome…", accelerator="Ctrl+Shift+S", command=self.save_file_as)
        m.add_separator()
        m.add_command(label="📄 Esporta chiaro", accelerator="Ctrl+E",
                      command=lambda: self.export(False))
        m.add_command(label="🔒 Esporta offuscato", accelerator="Ctrl+Shift+E",
                      command=lambda: self.export(True))
        m.add_separator()
        m.add_command(label="⚙ Rigenera offuscato", accelerator="Ctrl+B",
                      command=self.regenerate_obfuscated_ui)
        m.add_separator()
        m.add_command(label="Esci", command=self.on_close)
        mb.add_cascade(label="File", menu=m)

        e = tk.Menu(mb, tearoff=0, bg=self.theme['menu_bg'], fg=self.theme['menu_fg'],
                    activebackground=self.theme['menu_active'])
        self._submenus.append(e)
        e.add_command(label="Undo", accelerator="Ctrl+Z", command=self._undo)
        e.add_command(label="Redo", accelerator="Ctrl+Y", command=self._redo)
        e.add_separator()
        e.add_command(label="Trova…", accelerator="Ctrl+F",
                      command=lambda: self._open_find(False))
        e.add_command(label="Trova e sostituisci…", accelerator="Ctrl+H",
                      command=lambda: self._open_find(True))
        mb.add_cascade(label="Modifica", menu=e)

        r = tk.Menu(mb, tearoff=0, bg=self.theme['menu_bg'], fg=self.theme['menu_fg'],
                    activebackground=self.theme['menu_active'])
        self._submenus.append(r)
        r.add_command(label="🪟 Anteprima WebView (F5)",
                      command=lambda: self.run_webview(debug=False))
        r.add_command(label="🐞 Anteprima + DevTools (Shift+F5)",
                      command=lambda: self.run_webview(debug=True))
        r.add_separator()
        r.add_command(label="🌐 Apri in Browser (Ctrl+P)",
                      command=self.run_browser)
        mb.add_cascade(label="Esegui", menu=r)

        v = tk.Menu(mb, tearoff=0, bg=self.theme['menu_bg'], fg=self.theme['menu_fg'],
                    activebackground=self.theme['menu_active'])
        self._submenus.append(v)
        v.add_command(label="Cambia tema (Ctrl+T)", command=self.toggle_theme)
        mb.add_cascade(label="Visualizza", menu=v)

        h = tk.Menu(mb, tearoff=0, bg=self.theme['menu_bg'], fg=self.theme['menu_fg'],
                    activebackground=self.theme['menu_active'])
        self._submenus.append(h)
        h.add_command(label="📚 Documentazione HTML", accelerator="F1",
                      command=self.open_docs)
        mb.add_cascade(label="Aiuto", menu=h)

        self.root.config(menu=mb)

    def _build_toolbar(self):
        t = self.theme
        self.toolbar_frame = tk.Frame(self.root, bg=t['toolbar_bg'])
        self.toolbar_frame.pack(fill='x')

        def btn(label, cmd):
            b = tk.Button(self.toolbar_frame, text=label, command=cmd,
                          bg=t['toolbar_bg'], fg=t['menu_fg'],
                          activebackground=t['menu_active'],
                          activeforeground=t['menu_fg'],
                          relief='flat', bd=0, padx=10, pady=4,
                          font=('Helvetica', 10))
            b.pack(side='left', padx=1)
            return b

        btn("📄 Nuovo", self.new_file)
        btn("📂 Apri", self.open_file)
        btn("💾 Salva", self.save_file)
        tk.Frame(self.toolbar_frame, bg=t['toolbar_bg'], width=2).pack(side='left')
        btn("↶ Undo", self._undo)
        btn("↷ Redo", self._redo)
        tk.Frame(self.toolbar_frame, bg=t['toolbar_bg'], width=2).pack(side='left')
        btn("🔍 Trova", lambda: self._open_find(False))

        webview_label = "🪟 Anteprima (F5)" if HAS_PYWEBVIEW else "🪟 Anteprima ✗"
        btn(webview_label, lambda: self.run_webview(debug=False))
        if HAS_PYWEBVIEW:
            btn("🐞 +DevTools", lambda: self.run_webview(debug=True))
        btn("🌐 Browser", self.run_browser)

        tk.Frame(self.toolbar_frame, bg=t['toolbar_bg'], width=2).pack(side='left')
        btn("📄 Export chiaro", lambda: self.export(False))
        btn("🔒 Export offuscato", lambda: self.export(True))
        btn("⚙ Rigenera off", self.regenerate_obfuscated_ui)

        tk.Frame(self.toolbar_frame, bg=t['toolbar_bg'], width=2).pack(side='left')
        btn("🌓 Tema", self.toggle_theme)
        btn("📚 Docs", self.open_docs)

    def _build_layout(self):
        container = tk.Frame(self.root, bg=self.theme['bg'])
        container.pack(fill='both', expand=True)

        self.paned = tk.PanedWindow(container, orient='horizontal',
                                    bg=self.theme['bg'], sashwidth=4, bd=0)
        self.paned.pack(fill='both', expand=True)

        self.asset_panel = AssetPanel(self.paned, self)
        self.paned.add(self.asset_panel.frame, minsize=180)

        right = tk.Frame(self.paned, bg=self.theme['bg'])
        self.paned.add(right, stretch='always')

        editor_container = tk.Frame(right, bg=self.theme['bg'])
        editor_container.pack(fill='both', expand=True)

        self.text = tk.Text(
            editor_container, wrap='none', undo=True, maxundo=100,
            bg=self.theme['bg'], fg=self.theme['fg'],
            insertbackground=self.theme['cursor'],
            selectbackground=self.theme['selection'],
            font=('Consolas', 11), relief='flat', padx=8, pady=8,
        )
        self.text.pack(side='right', fill='both', expand=True)

        self.ln = LineNumbers(editor_container, self.text, self.theme)
        self.ln.pack(side='left', fill='y')

        vs = ttk.Scrollbar(editor_container, orient='vertical')
        vs.pack(side='right', fill='y')
        hs = ttk.Scrollbar(right, orient='horizontal')
        hs.pack(fill='x')

        self.ln.attach(vs)
        hs.configure(command=self.text.xview)
        self.text.configure(xscrollcommand=hs.set)

        self.hl = JSHighlighter(self.text, self.theme)

        self.text.bind('<KeyRelease>', self._on_keyrelease)
        self.text.bind('<KeyPress>', self._on_keypress)
        self.text.bind('<ButtonRelease-1>', self._on_click)
        self.text.bind('<<Paste>>', lambda e: self._on_keyrelease())
        self.text.bind('<Tab>', self._on_tab)
        self.text.bind('<Control-space>', self._show_autocomplete)
        self.text.bind('<Down>', self._ac_down)
        self.text.bind('<Up>', self._ac_up)
        self.text.bind('<Return>', self._ac_enter)
        self.text.bind('<Escape>', self._ac_esc)
        self.text.bind('<Control-z>', lambda e: self._undo())
        self.text.bind('<Control-y>', lambda e: self._redo())

        self.text.focus_set()

    def _build_status(self):
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(
            self.root, textvariable=self.status_var, anchor='w',
            bg=self.theme['status_bg'], fg=self.theme['status_fg'],
            padx=8, pady=4, font=('Helvetica', 9),
        )
        self.status_label.pack(fill='x', side='bottom')
        self._update_status()

    def _update_status(self):
        parts = []
        if find_lib(PLAIN_FILE):
            parts.append(f"📄 {PLAIN_FILE}")
        else:
            parts.append(f"❌ {PLAIN_FILE}")

        # Stato offuscato
        info = obfuscated_freshness()
        if info['missing']:
            parts.append(f"🔒 {OBFUSCATED_FILE} (mancante)")
        elif info['stale']:
            parts.append(f"⚠️ {OBFUSCATED_FILE} (vecchio)")
        elif not info['ob_has_all_symbols']:
            parts.append(f"⚠️ {OBFUSCATED_FILE} (incompleto)")
        else:
            parts.append(f"✅ {OBFUSCATED_FILE}")

        if ASSETS_DIR.exists():
            n = sum(1 for f in ASSETS_DIR.iterdir()
                    if f.is_file() and f.suffix.lower() in ALL_EXTS)
            parts.append(f"📁 {n} asset")

        docs_html = find_docs_html()
        docs_md = find_docs_md()
        if docs_html:
            parts.append(f"📚 {docs_html.name}")
        elif docs_md:
            parts.append(f"📚 {docs_md.name} (MD)")

        pywv = "🪟 pywebview ✓" if HAS_PYWEBVIEW else "🪟 pywebview ✗"
        parts.append(pywv)

        ok, tool = check_obfuscator_available()
        parts.append("🛠 npx ✓" if ok else "🛠 npx ✗")

        parts.append(f"🎨 {self.theme_name}")
        self.status_var.set("   |   ".join(parts))

    # ---------------------------------------------------------
    # EVENTI EDITOR
    # ---------------------------------------------------------
    def _on_keyrelease(self, e=None):
        self.hl.schedule()
        self.ln.redraw()
        if not self.modified:
            self.modified = True
            self._update_title()
        if self.ac.is_open() and e is not None:
            if e.keysym in ('Up', 'Down', 'Return', 'Escape', 'Tab'):
                return
            if e.keysym == 'space' and (e.state & 0x4):
                return
            prefix = self.text.get(self.ac.open_pos, 'insert')
            if not re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$]*', prefix or ''):
                self.ac.close()
            else:
                self.ac.update_filter(prefix)
        self._highlight_brackets()

    def _on_click(self, e=None):
        self._highlight_brackets()

    def _on_keypress(self, e=None):
        pairs = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'", '`': '`'}
        closers = {')', ']', '}', '"', "'", '`'}
        char = e.char if e is not None else ''

        if self.ac.is_open():
            if e.keysym in ('Return', 'Up', 'Down', 'Escape', 'Tab'):
                return

        if char in pairs and char != '\t':
            try:
                sel_start = self.text.index('sel.first')
                sel_end = self.text.index('sel.last')
                has_sel = True
            except tk.TclError:
                has_sel = False
            if has_sel:
                content = self.text.get(sel_start, sel_end)
                self.text.delete(sel_start, sel_end)
                self.text.insert(sel_start, char + content + pairs[char])
                self.text.mark_set('insert', f'{sel_start}+{1 + len(content)}c')
                return 'break'
            else:
                self.text.insert('insert', char + pairs[char])
                self.text.mark_set('insert', 'insert-1c')
                self._on_keyrelease()
                return 'break'

        if char in closers:
            nxt = self.text.get('insert', 'insert+1c')
            if nxt == char:
                self.text.mark_set('insert', 'insert+1c')
                self._on_keyrelease()
                return 'break'

        if e is not None and e.keysym == 'BackSpace':
            prev = self.text.get('insert-1c', 'insert')
            nxt = self.text.get('insert', 'insert+1c')
            if prev in pairs and nxt == pairs[prev]:
                self.text.delete('insert-1c', 'insert+1c')
                self._on_keyrelease()
                return 'break'

    def _on_tab(self, e):
        if self.ac.is_open():
            self.ac.confirm()
            return 'break'
        try:
            self.text.index('sel.first')
            self.text.insert('insert', '    ')
            return 'break'
        except tk.TclError:
            pass
        line = self.text.get('insert linestart', 'insert')
        m = re.search(r'([A-Za-z_$][A-Za-z0-9_$]*)$', line)
        if m and m.group(1) in SNIPPETS:
            word = m.group(1)
            start = f'insert - {len(word)}c'
            self.text.delete(start, 'insert')
            self.text.insert(start, SNIPPETS[word])
            self._on_keyrelease()
            return 'break'
        self.text.insert('insert', '    ')
        return 'break'

    def _highlight_brackets(self):
        self.text.tag_remove('bracket_match', '1.0', 'end')
        content = self.text.get('1.0', 'end-1c')
        cur = self.text.index('insert')
        off = len(self.text.get('1.0', cur))
        pairs = {'(': ')', '[': ']', '{': '}', ')': '(', ']': '[', '}': '{'}
        for offset in (off - 1, off):
            if offset < 0 or offset >= len(content):
                continue
            ch = content[offset]
            if ch not in pairs:
                continue
            target = pairs[ch]
            is_opener = ch in '([{'
            step = 1 if is_opener else -1
            count = 1
            i = offset + step
            while 0 <= i < len(content):
                c = content[i]
                if c == ch:
                    count += 1
                elif c == target:
                    count -= 1
                    if count == 0:
                        self.text.tag_add('bracket_match',
                                          f'1.0 + {offset}c', f'1.0 + {offset+1}c')
                        self.text.tag_add('bracket_match',
                                          f'1.0 + {i}c', f'1.0 + {i+1}c')
                        return
                i += step
            break

    def _show_autocomplete(self, e=None):
        self.ac.close()
        line = self.text.get('insert linestart', 'insert')
        m = re.search(r'([A-Za-z_$][A-Za-z0-9_$]*)$', line)
        prefix = m.group(1) if m else ''
        try:
            bbox = self.text.bbox('insert')
            if bbox is None:
                return
            x = self.text.winfo_rootx() + bbox[0]
            y = self.text.winfo_rooty() + bbox[1] + bbox[3]
        except Exception:
            return
        start_pos = self.text.index(f'insert - {len(prefix)}c') if m else self.text.index('insert')
        self.ac.show(x, y, prefix)
        if self.ac.is_open():
            self.ac.open_pos = start_pos

    def _ac_down(self, e):
        if self.ac.is_open():
            self.ac.move(1)
            return 'break'

    def _ac_up(self, e):
        if self.ac.is_open():
            self.ac.move(-1)
            return 'break'

    def _ac_enter(self, e):
        if self.ac.is_open():
            self.ac.confirm()
            return 'break'

    def _ac_esc(self, e):
        if self.ac.is_open():
            self.ac.close()
            return 'break'

    def _undo(self):
        try:
            self.text.edit_undo()
            self._on_keyrelease()
        except tk.TclError:
            pass

    def _redo(self):
        try:
            self.text.edit_redo()
            self._on_keyrelease()
        except tk.TclError:
            pass

    def _open_find(self, replace=False):
        if not self.find_dlg:
            self.find_dlg = FindReplaceDialog(self)
        self.find_dlg.open(replace)

    def _clear_find_highlight(self):
        self.text.tag_remove('find_match', '1.0', 'end')
        self.text.tag_remove('find_current', '1.0', 'end')

    # ---------------------------------------------------------
    # FILE
    # ---------------------------------------------------------
    def _update_title(self):
        n = pathlib.Path(self.current_file).name if self.current_file else "Untitled.js"
        self.root.title(f"gamma-2d Editor — {'*' if self.modified else ''}{n}")

    def _confirm(self):
        if not self.modified:
            return True
        r = messagebox.askyesnocancel("Modifiche non salvate", "Salvare prima di uscire?")
        if r is None:
            return False
        if r:
            return self.save_file()
        return True

    def new_file(self, show_starter=False):
        if not show_starter and not self._confirm():
            return
        self.text.delete('1.0', 'end')
        self.text.insert('1.0', STARTER_CODE)
        self.current_file = None
        self.modified = False
        self._update_title()
        self.hl.highlight()
        self.ln.redraw()
        self._remove_autosave()

    def open_file(self):
        if not self._confirm():
            return
        p = filedialog.askopenfilename(
            initialdir=CURRENT_DIR,
            filetypes=[('JavaScript', '*.js'), ('Tutti', '*.*')])
        if not p:
            return
        try:
            c = pathlib.Path(p).read_text(encoding='utf-8')
        except Exception as e:
            messagebox.showerror("Errore", str(e))
            return
        self.text.delete('1.0', 'end')
        self.text.insert('1.0', c)
        self.current_file = p
        self.modified = False
        self._update_title()
        self.hl.highlight()
        self.ln.redraw()
        self._remove_autosave()

    def save_file(self):
        if not self.current_file:
            return self.save_file_as()
        try:
            pathlib.Path(self.current_file).write_text(
                self.text.get('1.0', 'end-1c'), encoding='utf-8')
            self.modified = False
            self._update_title()
            self._flash("💾 Salvato")
            self._remove_autosave()
            return True
        except Exception as e:
            messagebox.showerror("Errore", str(e))
            return False

    def save_file_as(self):
        p = filedialog.asksaveasfilename(
            initialdir=CURRENT_DIR, defaultextension='.js',
            filetypes=[('JavaScript', '*.js')])
        if not p:
            return False
        self.current_file = p
        return self.save_file()

    # ---------------------------------------------------------
    # AUTOSAVE
    # ---------------------------------------------------------
    def _autosave_path(self):
        name = (pathlib.Path(self.current_file).stem if self.current_file else 'untitled')
        return CURRENT_DIR / f'.autosave_{name}.js'

    def _schedule_autosave(self):
        self._autosave_job = self.root.after(AUTOSAVE_INTERVAL_MS, self._autosave)

    def _autosave(self):
        try:
            if self.modified:
                self._autosave_path().write_text(
                    self.text.get('1.0', 'end-1c'), encoding='utf-8')
                self._flash("💾 Autosave")
        except Exception:
            pass
        finally:
            self._schedule_autosave()

    def _remove_autosave(self):
        try:
            p = self._autosave_path()
            if p.exists():
                p.unlink()
        except Exception:
            pass

    def _check_autosave_recovery(self):
        p = self._autosave_path()
        if p.exists():
            try:
                content = p.read_text(encoding='utf-8')
            except Exception:
                return
            if not content.strip() or content == STARTER_CODE:
                return
            r = messagebox.askyesno(
                "Recupero autosave",
                f"Trovato autosave di:\n{p.name}\n\nVuoi ripristinarlo?")
            if r:
                self.text.delete('1.0', 'end')
                self.text.insert('1.0', content)
                self.modified = True
                self._update_title()
                self.hl.highlight()
                self.ln.redraw()

    # ---------------------------------------------------------
    # PREVIEW
    # ---------------------------------------------------------
    def _build_html(self, use_obf):
        lib = find_lib(OBFUSCATED_FILE if use_obf else PLAIN_FILE)
        if not lib:
            messagebox.showerror(
                "Libreria mancante",
                f"'{OBFUSCATED_FILE if use_obf else PLAIN_FILE}' non trovato in:\n{CURRENT_DIR}")
            return None, 0
        return build_html(self.text.get('1.0', 'end-1c'), lib)

    def run_webview(self, debug=False):
        if not HAS_PYWEBVIEW:
            messagebox.showwarning(
                "pywebview non disponibile",
                'Installa con:\n    pip install "pywebview[qt]"\n\nUso il browser come fallback.')
            return self.run_browser()

        html, n = self._build_html(False)
        if html is None:
            return

        tmp = pathlib.Path(tempfile.gettempdir()) / 'gamma2d_preview.html'
        try:
            tmp.write_text(html, encoding='utf-8')
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile scrivere HTML:\n{e}")
            return

        host = ensure_webview_host()
        cmd = [sys.executable, str(host), str(tmp)]
        if debug:
            cmd.append('--debug')

        env = os.environ.copy()
        env['GAMMA2D_TITLE'] = "gamma-2d — Anteprima"

        try:
            subprocess.Popen(cmd, cwd=str(CURRENT_DIR), env=env)
            label = "con DevTools" if debug else "senza DevTools"
            self._flash(f"🪟 WebView ({label}, {n} asset)")
        except Exception as e:
            messagebox.showerror("Errore WebView",
                                 f"Impossibile avviare pywebview:\n{e}\n\nProvo con il browser…")
            self.run_browser()

    def run_browser(self):
        html, n = self._build_html(False)
        if html is None:
            return
        tmp = pathlib.Path(tempfile.gettempdir()) / 'gamma2d_preview.html'
        tmp.write_text(html, encoding='utf-8')
        webbrowser.open(tmp.as_uri())
        self._flash(f"🌐 Browser aperto ({n} asset)")

    # ---------------------------------------------------------
    # EXPORT
    # ---------------------------------------------------------
    def export(self, use_obf):
        # Se offuscato, verifica prima che sia aggiornato
        if use_obf:
            if not self._ensure_obfuscated_fresh():
                return

        lib = find_lib(OBFUSCATED_FILE if use_obf else PLAIN_FILE)
        if not lib:
            messagebox.showerror(
                "Libreria mancante",
                f"'{OBFUSCATED_FILE if use_obf else PLAIN_FILE}' non trovato.")
            return

        kind = "offuscata" if use_obf else "chiaro"
        default = ((pathlib.Path(self.current_file).stem
                    if self.current_file else 'gioco') + '_standalone.html')

        p = filedialog.asksaveasfilename(
            initialdir=CURRENT_DIR, initialfile=default,
            defaultextension='.html', filetypes=[('HTML', '*.html')])
        if not p:
            return

        html, n = self._build_html(use_obf)
        if html is None:
            return

        try:
            pathlib.Path(p).write_text(html, encoding='utf-8')
            size = os.path.getsize(p) / 1024
            messagebox.showinfo(
                "Export OK",
                f"📄 {pathlib.Path(p).name}\n"
                f"📚 {lib.name} ({kind})\n"
                f"📦 {n} asset\n"
                f"💾 {size:.1f} KB")
            self._flash(f"✅ Esportato ({kind}, {size:.1f} KB)")
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    # ---------------------------------------------------------
    # MISC
    # ---------------------------------------------------------
    def _flash(self, msg):
        old = self.status_var.get()
        self.status_var.set(msg)
        self.root.after(2500, lambda: self.status_var.set(old))

    def on_close(self):
        if not self._confirm():
            return
        try:
            self.config['geometry'] = self.root.geometry()
            self.config['theme'] = self.theme_name
            self._save_config()
        except Exception:
            pass
        if self._autosave_job:
            try:
                self.root.after_cancel(self._autosave_job)
            except Exception:
                pass
        self.root.destroy()


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    Editor(root)
    root.mainloop()