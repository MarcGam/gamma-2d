import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import base64
import mimetypes
import pathlib
import sys


# --- FUNZIONE PER GESTIRE I PERCORSI IN PYTHON E PYINSTALLER ---
def get_base_dir():
    """Restituisce la directory base dell'applicazione (script o eseguibile)."""
    if getattr(sys, 'frozen', False):
        return pathlib.Path(sys.executable).parent
    return pathlib.Path(__file__).parent


# --- CONFIGURAZIONE ---
CURRENT_DIR = get_base_dir()


def find_minilib():
    """Cerca la libreria gamma-2d, preferendo la versione minificata."""
    candidates = ['gamma-2d.min.js', 'gamma-2d.js']
    for name in candidates:
        path = CURRENT_DIR / name
        if path.exists():
            return path
    # Fallback per il messaggio d'errore
    return CURRENT_DIR / 'gamma-2d.js'


MINILIB_FILE = find_minilib()
ASSETS_DIR = CURRENT_DIR / 'assets'

# Estensioni supportate (allineate con la libreria gamma-2d)
IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg')
AUDIO_EXTS = ('.mp3', '.wav', '.ogg', '.m4a', '.aac')
ALL_EXTS = IMAGE_EXTS + AUDIO_EXTS


class BundlerApp:
    def __init__(self, master):
        self.master = master
        master.title("gamma-2d Bundler GUI")
        master.resizable(False, False)

        self.game_file_path = ""
        self.minilib_path = MINILIB_FILE
        self.assets_dir = ASSETS_DIR

        # --- Stili ---
        style = ttk.Style()
        style.configure('TFrame', padding=10)
        style.configure('TLabel', padding=5)
        style.configure('TButton', padding=10)
        style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'))

        main_frame = ttk.Frame(master, padding="15 15 15 15")
        main_frame.pack()

        # --- Titolo ---
        ttk.Label(
            main_frame,
            text="gamma-2d Standalone Creator",
            style='Header.TLabel'
        ).grid(row=0, column=0, columnspan=3, pady=10)

        # --- 1. File JS del gioco ---
        ttk.Label(main_frame, text="File JavaScript del Gioco (.js):").grid(row=1, column=0, sticky="w")
        self.game_path_entry = ttk.Entry(main_frame, width=40)
        self.game_path_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Sfoglia", command=self.select_game_file).grid(row=1, column=2)

        # --- 2. Nome output HTML ---
        ttk.Label(main_frame, text="Nome File Standalone (.html):").grid(row=2, column=0, sticky="w")
        self.output_name_entry = ttk.Entry(main_frame, width=40)
        self.output_name_entry.insert(0, "gioco_standalone.html")
        self.output_name_entry.grid(row=2, column=1, padx=5, pady=5)

        # --- 3. Libreria (display con indicatore) ---
        ttk.Label(main_frame, text="Libreria gamma-2d:").grid(row=3, column=0, sticky="w")
        lib_status = "✅" if self.minilib_path.exists() else "❌ (non trovata)"
        ttk.Label(
            main_frame,
            text=f"{lib_status}  {self.minilib_path.name}"
        ).grid(row=3, column=1, sticky="w")
        ttk.Label(
            main_frame,
            text=f"in: {self.minilib_path.parent.name}/",
            foreground="gray"
        ).grid(row=3, column=2, sticky="w")

        # --- 4. Assets (display con conteggio) ---
        ttk.Label(main_frame, text="Cartella Assets:").grid(row=4, column=0, sticky="w")
        ttk.Label(
            main_frame,
            text=f"📁 {self.assets_dir.name}/"
        ).grid(row=4, column=1, sticky="w")
        self.assets_count_label = ttk.Label(main_frame, text=self._get_assets_summary())
        self.assets_count_label.grid(row=4, column=2, sticky="w")

        # --- 5. Bottone principale ---
        self.bundle_button = ttk.Button(
            main_frame,
            text="🚀 Crea File Standalone",
            command=self.run_bundling
        )
        self.bundle_button.grid(row=5, column=0, columnspan=3, pady=20)

        # --- 6. Status ---
        self.status_label = ttk.Label(main_frame, text="", foreground="blue")
        self.status_label.grid(row=6, column=0, columnspan=3, pady=5)

    # ------------------------------------------------------------
    # HELPERS UI
    # ------------------------------------------------------------
    def _get_assets_summary(self):
        """Ritorna una stringa con il conteggio degli asset trovati."""
        if not self.assets_dir.exists():
            return "(cartella non trovata)"
        count = sum(
            1 for f in self.assets_dir.iterdir()
            if f.is_file() and f.suffix.lower() in ALL_EXTS
        )
        return f"({count} file trovati)" if count > 0 else "(vuota)"

    def select_game_file(self):
        """Dialog per selezionare il file JS del gioco."""
        filetypes = (
            ('JavaScript files', '*.js'),
            ('All files', '*.*')
        )
        self.game_file_path = filedialog.askopenfilename(
            initialdir=CURRENT_DIR,
            title="Seleziona il codice del gioco",
            filetypes=filetypes
        )
        if self.game_file_path:
            self.game_path_entry.delete(0, tk.END)
            self.game_path_entry.insert(0, self.game_file_path)

    # ------------------------------------------------------------
    # CONVERSIONE ASSET IN BASE64
    # ------------------------------------------------------------
    def file_to_base64(self, file_path):
        """Converte un file in stringa Base64 con MIME type corretto."""
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            ext = pathlib.Path(file_path).suffix.lower()
            fallbacks = {
                '.mp3': 'audio/mpeg',
                '.wav': 'audio/wav',
                '.ogg': 'audio/ogg',
                '.m4a': 'audio/mp4',
                '.aac': 'audio/aac',
                '.svg': 'image/svg+xml',
                '.webp': 'image/webp',
            }
            mime_type = fallbacks.get(ext, 'application/octet-stream')

        with open(file_path, 'rb') as f:
            data = base64.b64encode(f.read()).decode('utf-8')

        return f'data:{mime_type};base64,{data}'

    # ------------------------------------------------------------
    # BUNDLING
    # ------------------------------------------------------------
    def run_bundling(self):
        """Esegue il bundling al click del bottone."""
        game_file_path = self.game_path_entry.get().strip()
        output_file_name = self.output_name_entry.get().strip()

        # --- Validazione ---
        if not game_file_path or not os.path.exists(game_file_path):
            messagebox.showerror("Errore", "Seleziona un file JavaScript valido.")
            return

        if not output_file_name:
            messagebox.showerror("Errore", "Inserisci un nome per il file di output.")
            return

        if not output_file_name.lower().endswith('.html'):
            messagebox.showerror("Errore", "Il nome del file di output deve terminare con .html")
            return

        if not self.minilib_path.exists():
            messagebox.showerror(
                "Errore",
                f"Libreria gamma-2d non trovata!\n\n"
                f"Cartella cercata:\n{self.minilib_path.parent}\n\n"
                f"Nomi accettati:\n"
                f"  • gamma-2d.js\n"
                f"  • gamma-2d.min.js\n\n"
                f"Assicurati che uno dei due file sia presente nella stessa cartella del bundler."
            )
            return

        self.status_label.config(text="⏳ Creazione in corso...", foreground="orange")
        self.bundle_button.config(state='disabled')
        self.master.update()

        try:
            # --- 1. Carica libreria e codice gioco ---
            minilib_code = self.minilib_path.read_text(encoding='utf-8')
            game_code = pathlib.Path(game_file_path).read_text(encoding='utf-8')

            # --- 2. Processa assets ---
            base64_definitions = 'const ASSETS = {};\n'
            asset_count = 0

            if self.assets_dir.exists():
                asset_files = sorted(
                    [f for f in self.assets_dir.iterdir()
                     if f.is_file() and f.suffix.lower() in ALL_EXTS],
                    key=lambda f: f.name.lower()
                )

                for asset_path in asset_files:
                    base64_string = self.file_to_base64(asset_path)
                    # Chiave = nome file (es. 'player.png')
                    base64_definitions += f"ASSETS['{asset_path.name}'] = '{base64_string}';\n"
                    asset_count += 1

            # --- 3. Template HTML ---
            # Ordine: ASSETS → LIBRERIA → CODICE GIOCO
            # (così Sprite/Sound/eSprite sono definiti anche a livello top del game code)
            html_template = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{output_file_name[:-5]}</title>
    <style>
        body {{
            margin: 0;
            background: #1a1a1a;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: sans-serif;
        }}
        canvas {{
            box-shadow: 0 0 24px rgba(0,0,0,0.6);
            border-radius: 4px;
        }}
    </style>
</head>
<body>
<script>
// ============================================================
// 1) ASSETS EMBEDDED (Base64)
// ============================================================
// Ogni file è disponibile come ASSETS['nomefile.ext']
//
// Esempi d'uso nel codice del gioco:
//   new Sprite(ASSETS['player.png'], 100, 100, 32, 32)
//   new Sound(ASSETS['boom.wav'])
//   background(ASSETS['sfondo.png'])
//
// Oppure usa l'helper getAsset() che tollera path tipo 'assets/player.png':
//   new Sprite(getAsset('assets/player.png'), 100, 100, 32, 32)
{base64_definitions}

function getAsset(path) {{
    if (!path || typeof path !== 'string') return path;
    if (path.startsWith('data:')) return path;
    const name = path.split('/').pop();
    return ASSETS[name] || path;
}}

// ============================================================
// 2) GAMMA-2D LIBRARY
// ============================================================
{minilib_code}

// ============================================================
// 3) CODICE DEL GIOCO
// ============================================================
{game_code}
</script>
</body>
</html>
"""

            # --- 4. Scrivi file ---
            output_path = CURRENT_DIR / output_file_name
            output_path.write_text(html_template.strip(), encoding='utf-8')

            size_kb = output_path.stat().st_size / 1024
            self.assets_count_label.config(text=self._get_assets_summary())

            self.status_label.config(
                text=f"✅ Creato: {output_file_name}  •  {asset_count} asset  •  {size_kb:.1f} KB",
                foreground="green"
            )

            messagebox.showinfo(
                "Successo!",
                f"File standalone creato con successo!\n\n"
                f"📁 Percorso:\n{output_path}\n\n"
                f"📦 Asset incorporati: {asset_count}\n"
                f"💾 Dimensione: {size_kb:.1f} KB"
            )

        except Exception as e:
            self.status_label.config(
                text="❌ ERRORE: controlla il messaggio",
                foreground="red"
            )
            messagebox.showerror(
                "Errore Bundling",
                f"Si è verificato un errore durante l'elaborazione:\n\n{e}"
            )
        finally:
            self.bundle_button.config(state='normal')


# --- Avvio ---
if __name__ == "__main__":
    root = tk.Tk()
    app = BundlerApp(root)
    root.mainloop()