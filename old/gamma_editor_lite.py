"""
gamma-2d Editor (lite) - solo stdlib, nessuna dipendenza
Anteprima: apre il gioco nel browser di sistema con F5 o Ctrl+P
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pathlib, sys, base64, mimetypes, re, os, webbrowser, tempfile

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return pathlib.Path(sys.executable).parent
    return pathlib.Path(__file__).parent

CURRENT_DIR = get_base_dir()
OBFUSCATED_FILE = 'gamma-2d_ob.js'
PLAIN_FILE = 'gamma-2d.js'
ASSETS_DIR = CURRENT_DIR / 'assets'
DOCS_CANDIDATES = ['DOCUMENTATION.md', 'DOCS.md', 'README.md']

IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg')
AUDIO_EXTS = ('.mp3', '.wav', '.ogg', '.m4a', '.aac')
ALL_EXTS = IMAGE_EXTS + AUDIO_EXTS

# ============================================================
# STARTER CODE MINIMALE
# ============================================================
STARTER_CODE = """function setup() {
    createMiniCanvas(800, 600);
}

function draw() {
    background(30, 30, 40);
}
"""

def find_lib(name):
    p = CURRENT_DIR / name
    return p if p.exists() else None

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
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>gamma-2d Preview</title>
<style>body{{margin:0;background:#1a1a1a;display:flex;justify-content:center;
align-items:center;min-height:100vh}}canvas{{box-shadow:0 0 24px #000a;border-radius:4px}}</style>
</head><body><script>
{assets_js}
function getAsset(p){{if(!p||typeof p!=='string')return p;if(p.startsWith('data:'))return p;
const n=p.split('/').pop();return ASSETS[n]||p;}}
{lib_code}
{game_code}
</script></body></html>"""
    return html, n

class JSHighlighter:
    KW = {'break','case','catch','class','const','continue','default','delete',
          'do','else','export','extends','finally','for','function','if','import',
          'in','instanceof','let','new','return','static','super','switch','this',
          'throw','try','typeof','var','void','while','with','yield','async','await',
          'of','get','set','true','false','null','undefined'}
    BI = {'Math','Object','Array','String','Number','Boolean','Date','JSON',
          'Promise','Vector','Sprite','Rect','Ellipse','Button','Sound','eSprite',
          'ASSETS','console','window','document','performance','requestAnimationFrame'}
    def __init__(self, t):
        self.t = t; self._job = None
        for tag, kw in [('keyword',{'foreground':'#569cd6','font':('Consolas',11,'bold')}),
                        ('builtin',{'foreground':'#4ec9b0'}),
                        ('string',{'foreground':'#ce9178'}),
                        ('comment',{'foreground':'#6a9955','font':('Consolas',11,'italic')}),
                        ('number',{'foreground':'#b5cea8'}),
                        ('fn',{'foreground':'#dcdcaa'})]:
            t.tag_configure(tag, **kw)
    def schedule(self):
        if self._job: self.t.after_cancel(self._job)
        self._job = self.t.after(180, self.highlight)
    def highlight(self):
        self._job = None
        c = self.t.get('1.0','end-1c')
        for tag in ('keyword','builtin','string','comment','number','fn'):
            self.t.tag_remove(tag,'1.0','end')
        for m in re.finditer(r'\b[A-Za-z_$][A-Za-z0-9_$]*\b', c):
            w = m.group(0); s=f'1.0 + {m.start()}c'; e=f'1.0 + {m.end()}c'
            if w in self.KW: self.t.tag_add('keyword',s,e)
            elif w in self.BI: self.t.tag_add('builtin',s,e)
            elif c[m.end():m.end()+1]=='(': self.t.tag_add('fn',s,e)
        for m in re.finditer(r'\b\d+(?:\.\d+)?\b', c):
            self.t.tag_add('number',f'1.0 + {m.start()}c',f'1.0 + {m.end()}c')
        for pat in (r'"(?:[^"\\]|\\.)*"',r"'(?:[^'\\]|\\.)*'",r'`(?:[^`\\]|\\.)*`'):
            for m in re.finditer(pat, c):
                self.t.tag_add('string',f'1.0 + {m.start()}c',f'1.0 + {m.end()}c')
        for m in re.finditer(r'//[^\n]*', c):
            self.t.tag_add('comment',f'1.0 + {m.start()}c',f'1.0 + {m.end()}c')
        for m in re.finditer(r'/\*.*?\*/', c, re.DOTALL):
            self.t.tag_add('comment',f'1.0 + {m.start()}c',f'1.0 + {m.end()}c')

class LineNumbers(tk.Canvas):
    def __init__(self, master, text, **kw):
        super().__init__(master, width=48, highlightthickness=0, bg='#1e1e1e', **kw)
        self.text = text; self._sb = None
    def attach(self, sb):
        self._sb = sb
        self.text.configure(yscrollcommand=self._scroll)
        sb.configure(command=self.text.yview)
    def _scroll(self, f, l):
        if self._sb: self._sb.set(f, l)
        self.redraw()
    def redraw(self, *_):
        self.delete('all'); i = self.text.index('@0,0')
        while True:
            d = self.text.dlineinfo(i)
            if d is None: break
            self.create_text(self.winfo_width()-6, d[1], anchor='ne',
                             text=i.split('.')[0], fill='#666', font=('Consolas',10))
            i = self.text.index(f'{i}+1line')
            if self.text.compare(i,'>=','end'): break

class DocsWindow:
    def __init__(self, parent):
        w = tk.Toplevel(parent); w.title("📚 gamma-2d — Docs")
        w.geometry("950x750"); w.configure(bg='#1e1e1e')
        top = ttk.Frame(w, padding=6); top.pack(fill='x')
        ttk.Label(top, text="Documentazione", font=('Helvetica',11,'bold')).pack(side='left')
        ttk.Button(top, text="🔗 GitHub",
                   command=lambda: webbrowser.open('https://github.com/MarcGam/gamma-2d')
                   ).pack(side='right')
        txt = scrolledtext.ScrolledText(w, wrap='word', font=('Consolas',11),
                                        bg='#1e1e1e', fg='#d4d4d4', padx=10, pady=10,
                                        insertbackground='white', relief='flat')
        txt.pack(fill='both', expand=True)
        content = "Documentazione non trovata.\nMetti DOCUMENTATION.md o README.md qui."
        for name in DOCS_CANDIDATES:
            p = CURRENT_DIR / name
            if p.exists():
                content = p.read_text(encoding='utf-8'); break
        txt.insert('1.0', content)
        txt.tag_configure('h1', font=('Consolas',18,'bold'), foreground='#4ec9b0', spacing3=12)
        txt.tag_configure('h2', font=('Consolas',15,'bold'), foreground='#4ec9b0', spacing3=10)
        txt.tag_configure('h3', font=('Consolas',13,'bold'), foreground='#dcdcaa', spacing3=6)
        txt.tag_configure('code', font=('Consolas',10), background='#2d2d2d', foreground='#ce9178')
        for m in re.finditer(r'^# (.+)$', content, re.M):
            txt.tag_add('h1', f'1.0 + {m.start()}c', f'1.0 + {m.end()}c')
        for m in re.finditer(r'^## (.+)$', content, re.M):
            txt.tag_add('h2', f'1.0 + {m.start()}c', f'1.0 + {m.end()}c')
        for m in re.finditer(r'^### (.+)$', content, re.M):
            txt.tag_add('h3', f'1.0 + {m.start()}c', f'1.0 + {m.end()}c')
        for m in re.finditer(r'`([^`\n]+)`', content):
            txt.tag_add('code', f'1.0 + {m.start()}c', f'1.0 + {m.end()}c')
        txt.config(state='disabled')

class Editor:
    def __init__(self, root):
        self.root = root
        root.title("gamma-2d Editor — Untitled.js")
        root.geometry("1400x850"); root.configure(bg='#1e1e1e')
        self.current_file = None; self.modified = False
        self._build_menu(); self._build_toolbar(); self._build_layout(); self._build_status()
        root.bind('<Control-n>', lambda e: self.new_file())
        root.bind('<Control-o>', lambda e: self.open_file())
        root.bind('<Control-s>', lambda e: self.save_file())
        root.bind('<F5>', lambda e: self.run_browser())
        root.bind('<Control-p>', lambda e: self.run_browser())
        root.bind('<F1>', lambda e: DocsWindow(root))
        root.bind('<Control-e>', lambda e: self.export(False))
        root.bind('<Control-Shift-E>', lambda e: self.export(True))
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.new_file(show_starter=True)
    def _build_menu(self):
        mb = tk.Menu(self.root, bg='#252526', fg='white', activebackground='#094771')
        m = tk.Menu(mb, tearoff=0)
        m.add_command(label="Nuovo", accelerator="Ctrl+N", command=self.new_file)
        m.add_command(label="Apri…", accelerator="Ctrl+O", command=self.open_file)
        m.add_command(label="Salva", accelerator="Ctrl+S", command=self.save_file)
        m.add_separator()
        m.add_command(label="📄 Esporta chiaro", accelerator="Ctrl+E", command=lambda: self.export(False))
        m.add_command(label="🔒 Esporta offuscato", accelerator="Ctrl+Shift+E", command=lambda: self.export(True))
        m.add_separator(); m.add_command(label="Esci", command=self.on_close)
        mb.add_cascade(label="File", menu=m)
        r = tk.Menu(mb, tearoff=0)
        r.add_command(label="🌐 Apri in Browser", accelerator="F5", command=self.run_browser)
        mb.add_cascade(label="Esegui", menu=r)
        h = tk.Menu(mb, tearoff=0)
        h.add_command(label="📚 Documentazione", accelerator="F1", command=lambda: DocsWindow(self.root))
        mb.add_cascade(label="Aiuto", menu=h)
        self.root.config(menu=mb)
    def _build_toolbar(self):
        b = ttk.Frame(self.root, padding=6); b.pack(fill='x')
        for lbl, cmd in [("📄 Nuovo", self.new_file), ("📂 Apri", self.open_file), ("💾 Salva", self.save_file)]:
            ttk.Button(b, text=lbl, command=cmd).pack(side='left', padx=2)
        ttk.Separator(b, orient='vertical').pack(side='left', fill='y', padx=8)
        ttk.Button(b, text="🌐 Esegui in Browser (F5)", command=self.run_browser).pack(side='left', padx=2)
        ttk.Separator(b, orient='vertical').pack(side='left', fill='y', padx=8)
        ttk.Button(b, text="📄 Esporta chiaro", command=lambda: self.export(False)).pack(side='left', padx=2)
        ttk.Button(b, text="🔒 Esporta offuscato", command=lambda: self.export(True)).pack(side='left', padx=2)
        ttk.Separator(b, orient='vertical').pack(side='left', fill='y', padx=8)
        ttk.Button(b, text="📚 Docs (F1)", command=lambda: DocsWindow(self.root)).pack(side='left', padx=2)
    def _build_layout(self):
        container = tk.Frame(self.root, bg='#1e1e1e'); container.pack(fill='both', expand=True, padx=4, pady=4)
        self.text = tk.Text(container, wrap='none', undo=True, bg='#1e1e1e', fg='#d4d4d4',
                            insertbackground='#aeafad', selectbackground='#264f78',
                            font=('Consolas', 11), relief='flat', padx=8, pady=8)
        self.text.pack(side='right', fill='both', expand=True)
        self.ln = LineNumbers(container, self.text); self.ln.pack(side='left', fill='y')
        vs = ttk.Scrollbar(container, orient='vertical'); vs.pack(side='right', fill='y')
        hs = ttk.Scrollbar(self.root, orient='horizontal'); hs.pack(fill='x')
        self.ln.attach(vs); hs.configure(command=self.text.xview)
        self.text.configure(xscrollcommand=hs.set)
        self.hl = JSHighlighter(self.text)
        self.text.bind('<KeyRelease>', self._on_key)
        self.text.bind('<<Paste>>', self._on_key)
    def _build_status(self):
        self.status_var = tk.StringVar(); self._update_status()
        ttk.Label(self.root, textvariable=self.status_var, anchor='w', padding=(8, 4)).pack(fill='x', side='bottom')
    def _update_status(self):
        parts = []
        if find_lib(PLAIN_FILE): parts.append(f"📄 {PLAIN_FILE}")
        if find_lib(OBFUSCATED_FILE): parts.append(f"🔒 {OBFUSCATED_FILE}")
        if not parts: parts.append("❌ libreria mancante")
        if ASSETS_DIR.exists():
            n = sum(1 for f in ASSETS_DIR.iterdir() if f.is_file() and f.suffix.lower() in ALL_EXTS)
            parts.append(f"📁 {n} asset")
        self.status_var.set("   |   ".join(parts))
    def _on_key(self, e=None):
        self.hl.schedule(); self.ln.redraw()
        if not self.modified:
            self.modified = True; self._update_title()
    def _update_title(self):
        n = pathlib.Path(self.current_file).name if self.current_file else "Untitled.js"
        self.root.title(f"gamma-2d Editor — {'*' if self.modified else ''}{n}")
    def _confirm(self):
        if not self.modified: return True
        r = messagebox.askyesnocancel("Modifiche non salvate", "Salvare prima di uscire?")
        if r is None: return False
        if r: return self.save_file()
        return True
    def new_file(self, show_starter=False):
        if not show_starter and not self._confirm(): return
        self.text.delete('1.0','end'); self.text.insert('1.0', STARTER_CODE)
        self.current_file = None; self.modified = False
        self._update_title(); self.hl.highlight(); self.ln.redraw()
    def open_file(self):
        if not self._confirm(): return
        p = filedialog.askopenfilename(initialdir=CURRENT_DIR,
            filetypes=[('JavaScript','*.js'),('Tutti','*.*')])
        if not p: return
        try:
            c = pathlib.Path(p).read_text(encoding='utf-8')
        except Exception as e:
            messagebox.showerror("Errore", str(e)); return
        self.text.delete('1.0','end'); self.text.insert('1.0', c)
        self.current_file = p; self.modified = False
        self._update_title(); self.hl.highlight(); self.ln.redraw()
    def save_file(self):
        if not self.current_file:
            p = filedialog.asksaveasfilename(initialdir=CURRENT_DIR, defaultextension='.js',
                filetypes=[('JavaScript','*.js')])
            if not p: return False
            self.current_file = p
        try:
            pathlib.Path(self.current_file).write_text(self.text.get('1.0','end-1c'), encoding='utf-8')
            self.modified = False; self._update_title()
            self._flash("💾 Salvato"); return True
        except Exception as e:
            messagebox.showerror("Errore", str(e)); return False
    def _build_html(self, use_obf):
        lib = find_lib(OBFUSCATED_FILE if use_obf else PLAIN_FILE)
        if not lib:
            messagebox.showerror("Libreria mancante",
                f"'{OBFUSCATED_FILE if use_obf else PLAIN_FILE}' non trovato in:\n{CURRENT_DIR}")
            return None, 0
        return build_html(self.text.get('1.0','end-1c'), lib)
    def run_browser(self):
        html, n = self._build_html(False)
        if html is None: return
        tmp = pathlib.Path(tempfile.gettempdir()) / 'gamma2d_preview.html'
        tmp.write_text(html, encoding='utf-8')
        webbrowser.open(tmp.as_uri())
        self._flash(f"🌐 Browser aperto ({n} asset)")
    def export(self, use_obf):
        lib = find_lib(OBFUSCATED_FILE if use_obf else PLAIN_FILE)
        if not lib:
            messagebox.showerror("Libreria mancante",
                f"'{OBFUSCATED_FILE if use_obf else PLAIN_FILE}' non trovato.")
            return
        kind = "offuscata" if use_obf else "chiaro"
        default = ((pathlib.Path(self.current_file).stem if self.current_file else 'gioco')
                   + '_standalone.html')
        p = filedialog.asksaveasfilename(initialdir=CURRENT_DIR, initialfile=default,
            defaultextension='.html', filetypes=[('HTML','*.html')])
        if not p: return
        html, n = self._build_html(use_obf)
        if html is None: return
        try:
            pathlib.Path(p).write_text(html, encoding='utf-8')
            size = os.path.getsize(p)/1024
            messagebox.showinfo("Export OK",
                f"📄 {pathlib.Path(p).name}\n📚 {lib.name} ({kind})\n"
                f"📦 {n} asset\n💾 {size:.1f} KB")
            self._flash(f"✅ Esportato ({kind}, {size:.1f} KB)")
        except Exception as e:
            messagebox.showerror("Errore", str(e))
    def _flash(self, msg):
        old = self.status_var.get(); self.status_var.set(msg)
        self.root.after(2500, lambda: self.status_var.set(old))
    def on_close(self):
        if self._confirm(): self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk(); Editor(root); root.mainloop()