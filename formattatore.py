#!/usr/bin/env python3
"""
Formattatore di Codice → PNG
Incolla codice, scegli linguaggio e tema, copia il PNG negli appunti.
"""

import tkinter as tk
from tkinter import ttk
import subprocess
import tempfile
import os
import sys


def _ensure_deps():
    needed = []
    try:
        from PIL import Image  # noqa
    except ImportError:
        needed.append("Pillow")
    try:
        import pygments  # noqa
    except ImportError:
        needed.append("Pygments")
    if needed:
        print(f"Installazione dipendenze: {', '.join(needed)} ...")
        ret = subprocess.call(
            [sys.executable, "-m", "pip", "install", "--quiet"] + needed
        )
        if ret != 0:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--quiet",
                 "--break-system-packages"] + needed
            )


_ensure_deps()

from PIL import ImageFont  # noqa
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
from pygments.formatters import ImageFormatter
from pygments.style import Style
from pygments.token import Token, Keyword, Name, Comment, String, Number, Operator, Punctuation


# ---------------------------------------------------------------------------
# Tema Scuro — Atom One Dark
# ---------------------------------------------------------------------------
class AtomOneDark(Style):
    background_color = "#282c34"
    default_style = "#abb2bf"
    styles = {
        Token:                   "#abb2bf",
        Token.Text:              "#abb2bf",
        Keyword:                 "#c678dd",
        Keyword.Declaration:     "#c678dd",
        Keyword.Namespace:       "#c678dd",
        Keyword.Reserved:        "#c678dd",
        Keyword.Type:            "#e5c07b",
        Name:                    "#abb2bf",
        Name.Class:              "#e5c07b",
        Name.Function:           "#61afef",
        Name.Builtin:            "#e5c07b",
        Name.Decorator:          "#61afef",
        Name.Attribute:          "#e06c75",
        Name.Namespace:          "#e5c07b",
        Name.Other:              "#abb2bf",
        String:                  "#98c379",
        String.Doc:              "#5c6370",
        Number:                  "#d19a66",
        Operator:                "#56b6c2",
        Operator.Word:           "#c678dd",
        Comment:                 "#5c6370",
        Comment.Single:          "#5c6370",
        Comment.Multiline:       "#5c6370",
        Punctuation:             "#abb2bf",
    }


# ---------------------------------------------------------------------------
# Tema Chiaro — Atom One Light
# ---------------------------------------------------------------------------
class AtomOneLight(Style):
    background_color = "#fafafa"
    default_style = "#383a42"
    styles = {
        Token:                   "#383a42",
        Token.Text:              "#383a42",
        Keyword:                 "#a626a4",
        Keyword.Declaration:     "#a626a4",
        Keyword.Namespace:       "#a626a4",
        Keyword.Reserved:        "#a626a4",
        Keyword.Type:            "#c18401",
        Name:                    "#383a42",
        Name.Class:              "#c18401",
        Name.Function:           "#4078f2",
        Name.Builtin:            "#c18401",
        Name.Decorator:          "#4078f2",
        Name.Attribute:          "#e45649",
        Name.Namespace:          "#c18401",
        Name.Other:              "#383a42",
        String:                  "#50a14f",
        String.Doc:              "#a0a1a7",
        Number:                  "#986801",
        Operator:                "#0184bc",
        Operator.Word:           "#a626a4",
        Comment:                 "#a0a1a7",
        Comment.Single:          "#a0a1a7",
        Comment.Multiline:       "#a0a1a7",
        Punctuation:             "#383a42",
    }


# ---------------------------------------------------------------------------
# Configurazione temi
# ---------------------------------------------------------------------------
THEMES = {
    "Scuro": {
        "pygments_style": AtomOneDark,
        # colori UI app
        "app_bg":         "#1e1e2e",
        "editor_bg":      "#282c34",
        "editor_fg":      "#abb2bf",
        "editor_sel":     "#3e4451",
        "editor_cursor":  "#abb2bf",
        "label_fg":       "#888888",
        "status_neutral": "#5c6370",
        "title_fg":       "#ffffff",
    },
    "Chiaro": {
        "pygments_style": AtomOneLight,
        "app_bg":         "#f0f0f5",
        "editor_bg":      "#fafafa",
        "editor_fg":      "#383a42",
        "editor_sel":     "#d0d0e0",
        "editor_cursor":  "#383a42",
        "label_fg":       "#666666",
        "status_neutral": "#a0a1a7",
        "title_fg":       "#1a1a2e",
    },
}


# ---------------------------------------------------------------------------
# Font discovery (macOS)
# ---------------------------------------------------------------------------
FONT_CANDIDATES = [
    os.path.expanduser("~/Library/Fonts/JetBrainsMono-Regular.ttf"),
    "/Library/Fonts/JetBrainsMono-Regular.ttf",
    "/System/Library/Fonts/SFMono-Regular.otf",
    "/Applications/Xcode.app/Contents/SharedFrameworks/DVTKit.framework/"
    "Versions/A/Resources/Fonts/SFMono-Regular.otf",
    "/System/Library/Fonts/Menlo.ttc",
    "/Library/Fonts/Courier New.ttf",
    "/System/Library/Fonts/Courier.dfont",
]

FONT_SIZE = 17
IMAGE_PAD = 28


# ---------------------------------------------------------------------------
# Linguaggi supportati
# ---------------------------------------------------------------------------
LANGUAGES = [
    ("Auto-detect", "auto"),
    ("Java",        "java"),
    ("Python",      "python"),
    ("JavaScript",  "javascript"),
    ("TypeScript",  "typescript"),
    ("Kotlin",      "kotlin"),
    ("Swift",       "swift"),
    ("C++",         "cpp"),
    ("C#",          "csharp"),
    ("Go",          "go"),
    ("Rust",        "rust"),
    ("SQL",         "sql"),
    ("JSON",        "json"),
    ("XML",         "xml"),
    ("Bash",        "bash"),
    ("HTML",        "html"),
    ("CSS",         "css"),
]

ACCENT = "#5865f2"

EXAMPLE_CODE = """\
List<Persona> amici = Arrays.asList(
    new Persona("Saro", 24), new Persona("Taro", 21),
    new Persona("Ian", 19), new Persona("Al", 16));

int somma = amici.stream()
                .map(Persona::getEta)
                .reduce(0, Integer::sum);"""


# ---------------------------------------------------------------------------
# Logica PNG
# ---------------------------------------------------------------------------
def generate_png(code: str, language: str, pygments_style) -> bytes:
    if language == "auto":
        try:
            lexer = guess_lexer(code)
        except Exception:
            lexer = TextLexer()
    else:
        try:
            lexer = get_lexer_by_name(language)
        except Exception:
            lexer = TextLexer()

    font_path = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)

    kwargs = dict(
        style=pygments_style,
        font_size=FONT_SIZE,
        image_pad=IMAGE_PAD,
        line_numbers=False,
        line_number_separator=False,
    )
    if font_path:
        kwargs["font_name"] = font_path

    return highlight(code, lexer, ImageFormatter(**kwargs))


def copy_png_to_clipboard(png_path: str) -> bool:
    script = (
        f'set the clipboard to '
        f'(read (POSIX file "{png_path}") as «class PNGf»)'
    )
    result = subprocess.run(["osascript", "-e", script], capture_output=True)
    return result.returncode == 0


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------
class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Code → PNG")
        root.geometry("760x540")
        root.resizable(True, True)

        self._current_theme = "Scuro"
        self._build_ui()
        self._apply_theme("Scuro")

    # ── Costruzione UI ──────────────────────────────────────────────────────
    def _build_ui(self):
        # Titolo
        self.hdr = tk.Frame(self.root, padx=18, pady=14)
        self.hdr.pack(fill="x")
        self.title_lbl = tk.Label(
            self.hdr, text="Code  →  PNG",
            font=("SF Pro Display", 20, "bold"),
        )
        self.title_lbl.pack(side="left")

        # Barra controlli
        self.ctrl = tk.Frame(self.root, padx=18, pady=4)
        self.ctrl.pack(fill="x")

        # — Linguaggio —
        self.lang_lbl = tk.Label(
            self.ctrl, text="Linguaggio:",
            font=("SF Pro Text", 13),
        )
        self.lang_lbl.pack(side="left", padx=(0, 8))

        self.lang_var = tk.StringVar(value="Auto-detect")
        self.lang_combo = ttk.Combobox(
            self.ctrl, textvariable=self.lang_var,
            values=[n for n, _ in LANGUAGES],
            state="readonly", width=16,
        )
        self.lang_combo.pack(side="left")

        # — Tema —
        self.theme_lbl = tk.Label(
            self.ctrl, text="Tema:",
            font=("SF Pro Text", 13),
        )
        self.theme_lbl.pack(side="left", padx=(18, 8))

        self.theme_var = tk.StringVar(value="Scuro")
        for label in ("Scuro", "Chiaro"):
            rb = tk.Radiobutton(
                self.ctrl, text=label,
                variable=self.theme_var, value=label,
                font=("SF Pro Text", 13),
                relief="flat", padx=4,
                cursor="hand2",
                command=lambda l=label: self._apply_theme(l),
            )
            rb.pack(side="left", padx=2)
            # teniamo riferimento per il re-theming
            if not hasattr(self, "_radio_btns"):
                self._radio_btns = []
            self._radio_btns.append(rb)

        # — Status + bottone (destra) —
        self.status_var = tk.StringVar()
        self.status_lbl = tk.Label(
            self.ctrl, textvariable=self.status_var,
            font=("SF Pro Text", 12),
        )
        self.status_lbl.pack(side="right", padx=(0, 14))

        self.copy_btn = tk.Button(
            self.ctrl,
            text="  Copia come PNG  ",
            bg=ACCENT, fg="white",
            font=("SF Pro Text", 13, "bold"),
            relief="flat", padx=14, pady=7,
            cursor="hand2",
            activebackground="#4752c4", activeforeground="white",
            command=self.copy_as_png,
        )
        self.copy_btn.pack(side="right")

        # Area testo
        self.editor_frame = tk.Frame(self.root, padx=12, pady=10)
        self.editor_frame.pack(fill="both", expand=True, padx=18, pady=(10, 18))

        self.text = tk.Text(
            self.editor_frame,
            font=self._editor_font(),
            relief="flat",
            padx=10, pady=8,
            wrap="none",
            undo=True,
            tabs="4",
        )
        vsb = tk.Scrollbar(self.editor_frame, orient="vertical",  command=self.text.yview)
        hsb = tk.Scrollbar(self.editor_frame, orient="horizontal", command=self.text.xview)
        self.text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")
        self.text.pack(side="left", fill="both", expand=True)
        self.text.insert("1.0", EXAMPLE_CODE)

    # ── Theming ─────────────────────────────────────────────────────────────
    def _apply_theme(self, name: str):
        self._current_theme = name
        t = THEMES[name]

        self.root.configure(bg=t["app_bg"])
        for widget in (self.hdr, self.ctrl, self.editor_frame):
            widget.configure(bg=t["app_bg"])

        self.title_lbl.configure(bg=t["app_bg"], fg=t["title_fg"])
        self.lang_lbl.configure(bg=t["app_bg"],  fg=t["label_fg"])
        self.theme_lbl.configure(bg=t["app_bg"], fg=t["label_fg"])
        self.status_lbl.configure(bg=t["app_bg"])
        self._set_status("", t["status_neutral"])

        for rb in self._radio_btns:
            rb.configure(
                bg=t["app_bg"],
                fg=t["label_fg"],
                selectcolor=t["app_bg"],
                activebackground=t["app_bg"],
                activeforeground=t["title_fg"],
            )

        self.text.configure(
            bg=t["editor_bg"],
            fg=t["editor_fg"],
            insertbackground=t["editor_cursor"],
            selectbackground=t["editor_sel"],
        )

        # Aggiorna stile combobox
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TCombobox",
            fieldbackground=t["editor_bg"],
            background=t["editor_bg"],
            foreground=t["editor_fg"],
            selectbackground=t["editor_sel"],
        )

    # ── Azioni ──────────────────────────────────────────────────────────────
    @staticmethod
    def _editor_font():
        for name in ("JetBrains Mono", "SF Mono", "Menlo", "Courier New", "Courier"):
            try:
                f = tk.font.Font(family=name, size=13)
                if name.lower() in f.actual("family").lower():
                    return (name, 13)
            except Exception:
                pass
        return ("Courier", 13)

    def _get_language(self) -> str:
        sel = self.lang_var.get()
        return next((k for n, k in LANGUAGES if n == sel), "auto")

    def copy_as_png(self):
        code = self.text.get("1.0", "end-1c").rstrip()
        if not code:
            self._set_status("⚠️  Incolla del codice prima!", "#d19a66")
            return

        t = THEMES[self._current_theme]
        self._set_status("Generazione in corso…", t["status_neutral"])
        self.root.update()

        try:
            png_data = generate_png(code, self._get_language(), t["pygments_style"])

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                f.write(png_data)
                tmp = f.name

            ok = copy_png_to_clipboard(tmp)
            os.unlink(tmp)

            if ok:
                self._set_status("✓  PNG copiato negli appunti!", "#98c379")
            else:
                self._set_status("⚠️  Errore copia negli appunti", "#e06c75")

        except Exception as exc:
            self._set_status(f"Errore: {exc}", "#e06c75")

        neutral = THEMES[self._current_theme]["status_neutral"]
        self.root.after(3500, lambda: self._set_status("", neutral))

    def _set_status(self, msg: str, color: str):
        self.status_var.set(msg)
        self.status_lbl.configure(fg=color)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import tkinter.font  # noqa
    root = tk.Tk()
    App(root)
    root.mainloop()
