"""
gui.py - Grafische Benutzeroberfläche für VSCtoPDF auf macOS.
Ermöglicht das Hinzufügen von Code-Dateien/Ordnern (auch per Drag & Drop),
Konvertierung in DIN-A4 PDF und selektives Drucken auf macOS-Druckern.
"""

import os
import sys
import threading
import subprocess
from typing import List, Dict, Any, Optional

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Drag & Drop Unterstützung
HAS_DND = False
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
except ImportError:
    pass

from converter import convert_code_file_to_pdf
from printer import get_installed_printers, print_pdf, open_in_preview, reveal_in_finder

# Bekannte Code- & Text-Dateiendungen
CODE_EXTENSIONS = {
    # Web
    ".html", ".htm", ".css", ".scss", ".sass", ".less", ".js", ".jsx",
    ".ts", ".tsx", ".vue", ".svelte", ".php", ".jsp", ".asp",
    # Python & Daten
    ".py", ".pyw", ".ipynb", ".r", ".rmd", ".jl", ".json", ".yaml", ".yml", ".toml", ".xml",
    # System & Kompiliert
    ".c", ".h", ".cpp", ".hpp", ".cc", ".hh", ".cxx", ".m", ".mm",
    ".swift", ".java", ".kt", ".kts", ".go", ".rs", ".cs", ".scala",
    # Shell & Konfiguration
    ".sh", ".bash", ".zsh", ".fish", ".bat", ".cmd", ".ps1",
    ".ini", ".conf", ".cfg", ".env", ".dockerfile",
    # Datenbanken & Dokumentation
    ".sql", ".prisma", ".graphql", ".gql", ".md", ".markdown", ".rst", ".txt", ".csv"
}

IGNORED_DIRS = {
    ".git", ".svn", ".hg", ".venv", "venv", "env", "__pycache__",
    "node_modules", "dist", "build", ".idea", ".vscode", ".next", ".nuxt"
}

IGNORED_EXTS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp",
    ".woff", ".woff2", ".ttf", ".eot", ".zip", ".tar", ".gz", ".dmg",
    ".pkg", ".pyc", ".pyo", ".o", ".so", ".dylib", ".a", ".class", ".exe", ".bin", ".ds_store"
}


def is_text_or_code_file(filepath: str) -> bool:
    """Prüft, ob eine Datei eine Text- oder Code-Datei ist."""
    basename = os.path.basename(filepath)
    if basename.startswith(".") and not basename.startswith(".env"):
        return False

    ext = os.path.splitext(filepath)[1].lower()
    if ext in IGNORED_EXTS:
        return False

    if ext in CODE_EXTENSIONS or basename.lower() in {"dockerfile", "makefile", "gemfile", "pipfile"}:
        return True

    # Fallback: Prüfen, ob Datei lesbar und ohne Null-Bytes ist
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return False
        return True
    except Exception:
        return False


def scan_directory(dir_path: str) -> List[str]:
    """Sucht rekursiv nach allen relevanten Quellcodedateien im Ordner."""
    found_files = []
    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in IGNORED_DIRS]
        for f in files:
            fp = os.path.join(root, f)
            if is_text_or_code_file(fp):
                found_files.append(fp)
    return found_files


class VSCtoPDFApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("VSCtoPDF – Code zu DIN-A4 PDF & Druck für Mac")
        self.root.geometry("1020x680")
        self.root.minsize(860, 500)

        # Datenmodell: Liste von Datei-Einträgen
        # Jeder Eintrag: {
        #   'id': str,
        #   'path': str,
        #   'folder': str,
        #   'name': str,
        #   'type': str,
        #   'selected': bool,
        #   'status': str,
        #   'pages': str,
        #   'pdf_path': str
        # }
        self.file_items: Dict[str, Dict[str, Any]] = {}

        self.setup_styles()
        self.build_ui()
        self.setup_dnd()
        self.load_printers()

    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("aqua")
        except Exception:
            pass

    def build_ui(self):
        # Hauptcontainer mit Randabstand
        main_frame = ttk.Frame(self.root, padding="14")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # -------------------------------------------------------------------
        # 1. Konfigurationsleiste (Kopf- & Fußzeile, Drucker, Optionen)
        # -------------------------------------------------------------------
        cfg_frame = ttk.LabelFrame(main_frame, text=" ⚙️ PDF- & Druck-Einstellungen ", padding="10")
        cfg_frame.pack(fill=tk.X, pady=(0, 10))

        # Zeile 1: Fußzeile & Drucker
        row1 = ttk.Frame(cfg_frame)
        row1.pack(fill=tk.X, pady=3)

        # Fußzeile Wort
        ttk.Label(row1, text="Fußzeile (links):", font=("Helvetica", 11, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self.footer_entry = ttk.Entry(row1, width=24)
        self.footer_entry.insert(0, "Code-Dokumentation")
        self.footer_entry.pack(side=tk.LEFT, padx=(0, 20))

        # Drucker-Auswahl
        ttk.Label(row1, text="Drucker:", font=("Helvetica", 11, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self.printer_combo = ttk.Combobox(row1, state="readonly", width=30)
        self.printer_combo.pack(side=tk.LEFT, padx=(0, 12))

        # Drucker aktualisieren Button
        ttk.Button(row1, text="🔄", width=3, command=self.load_printers).pack(side=tk.LEFT)

        # Zeile 2: Druckoptionen (Duplex, Kopien, Farbschema)
        row2 = ttk.Frame(cfg_frame)
        row2.pack(fill=tk.X, pady=(6, 2))

        # Farbschema
        ttk.Label(row2, text="Farbschema:").pack(side=tk.LEFT, padx=(0, 6))
        self.style_combo = ttk.Combobox(row2, state="readonly", width=12, values=["friendly", "default", "colorful", "bw"])
        self.style_combo.set("friendly")
        self.style_combo.pack(side=tk.LEFT, padx=(0, 20))

        # Duplex
        self.duplex_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row2, text="Beidseitig (Duplex)", variable=self.duplex_var).pack(side=tk.LEFT, padx=(0, 20))

        # Kopien
        ttk.Label(row2, text="Kopien:").pack(side=tk.LEFT, padx=(0, 6))
        self.copies_spin = ttk.Spinbox(row2, from_=1, to=99, width=4)
        self.copies_spin.set(1)
        self.copies_spin.pack(side=tk.LEFT)

        # Infotext über Kopfzeile
        info_label = ttk.Label(
            row2,
            text="ℹ️ DIN-A4 Kopfzeile enthält automatisch den Ordner-Pfad der Datei.",
            foreground="#555555",
            font=("Helvetica", 10)
        )
        info_label.pack(side=tk.RIGHT)

        # -------------------------------------------------------------------
        # 2. Dateiverwaltungsleiste (Buttons zum Hinzufügen / Löschen)
        # -------------------------------------------------------------------
        btn_bar = ttk.Frame(main_frame)
        btn_bar.pack(fill=tk.X, pady=(0, 8))

        ttk.Button(btn_bar, text="📄 Dateien hinzufügen...", command=self.add_files_dialog).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_bar, text="📁 Ordner hinzufügen...", command=self.add_folder_dialog).pack(side=tk.LEFT, padx=(0, 14))

        ttk.Button(btn_bar, text="🗑 Aus Liste entfernen", command=self.remove_selected_from_list).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_bar, text="🧹 Liste leeren", command=self.clear_list).pack(side=tk.LEFT)

        self.drop_hint = ttk.Label(
            btn_bar,
            text="💡 Tipp: Dateien oder Ordner einfach per Drag & Drop hier hineinziehen!",
            foreground="#2d6a4f",
            font=("Helvetica", 10, "italic")
        )
        self.drop_hint.pack(side=tk.RIGHT)

        # -------------------------------------------------------------------
        # 3. Datei-Tabelle (Treeview mit Checkboxen)
        # -------------------------------------------------------------------
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        columns = ("select", "name", "type", "folder", "pages", "status", "pdf_path")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="extended"
        )

        self.tree.heading("select", text="Drucken", command=self.toggle_all_selection)
        self.tree.heading("name", text="Dateiname")
        self.tree.heading("type", text="Dateityp")
        self.tree.heading("folder", text="Ordner-Pfad")
        self.tree.heading("pages", text="Seiten")
        self.tree.heading("status", text="Status")
        self.tree.heading("pdf_path", text="Generierter PDF-Pfad")

        self.tree.column("select", width=65, minwidth=60, anchor="center")
        self.tree.column("name", width=180, minwidth=120)
        self.tree.column("type", width=80, minwidth=60, anchor="center")
        self.tree.column("folder", width=250, minwidth=150)
        self.tree.column("pages", width=65, minwidth=50, anchor="center")
        self.tree.column("status", width=110, minwidth=80, anchor="center")
        self.tree.column("pdf_path", width=220, minwidth=120)

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Interaktion: Klick zum Umschalten der Checkbox
        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)
        self.tree.bind("<space>", self.on_tree_space)
        self.tree.bind("<Double-Button-1>", self.on_tree_double_click)

        # Kontextmenü
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Druck-Auswahl umschalten", command=self.toggle_highlighted_selection)
        self.context_menu.add_command(label="In Vorschau öffnen", command=self.open_current_in_preview)
        self.context_menu.add_command(label="Im Finder anzeigen", command=self.reveal_current_in_finder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Aus Liste entfernen", command=self.remove_selected_from_list)
        self.tree.bind("<Button-2>", self.show_context_menu)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Control-Button-1>", self.show_context_menu)

        # -------------------------------------------------------------------
        # 4. Konvertierungsleiste (Großer Konvertieren-Button + Fortschritt)
        # -------------------------------------------------------------------
        conv_frame = ttk.Frame(main_frame)
        conv_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_convert = ttk.Button(
            conv_frame,
            text="🚀 Alle Dateien als DIN-A4 PDF konvertieren",
            command=self.start_conversion
        )
        self.btn_convert.pack(side=tk.LEFT, padx=(0, 14))

        self.progress_bar = ttk.Progressbar(conv_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 14))

        self.lbl_status = ttk.Label(conv_frame, text="Bereit – keine Dateien geladen", font=("Helvetica", 10))
        self.lbl_status.pack(side=tk.RIGHT)

        # -------------------------------------------------------------------
        # 5. Druckleiste (Auswahl-Buttons & Direktdruck)
        # -------------------------------------------------------------------
        print_frame = ttk.LabelFrame(main_frame, text=" 🖨️ Druckauswahl & Druckauftrag ", padding="10")
        print_frame.pack(fill=tk.X)

        ttk.Button(print_frame, text="☑ Alle auswählen", command=self.select_all_for_print).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(print_frame, text="☐ Auswahl aufheben", command=self.deselect_all_for_print).pack(side=tk.LEFT, padx=(0, 16))

        self.btn_print = ttk.Button(
            print_frame,
            text="🖨️ Ausgewählte PDFs drucken",
            command=self.start_printing
        )
        self.btn_print.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Button(print_frame, text="👁 In Vorschau öffnen", command=self.open_current_in_preview).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(print_frame, text="📁 Im Finder zeigen", command=self.reveal_current_in_finder).pack(side=tk.LEFT)

        self.lbl_selection_count = ttk.Label(
            print_frame,
            text="0 Dateien zum Drucken ausgewählt",
            font=("Helvetica", 10, "bold"),
            foreground="#1d3557"
        )
        self.lbl_selection_count.pack(side=tk.RIGHT)

    # -----------------------------------------------------------------------
    # Drag & Drop Unterstützung
    # -----------------------------------------------------------------------
    def setup_dnd(self):
        if HAS_DND:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind("<<Drop>>", self.on_drop)
        else:
            self.drop_hint.configure(text="ℹ️ Nutzen Sie die Buttons oben zum Hinzufügen von Dateien/Ordnern.")

    def on_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        self.add_paths(paths)

    # -----------------------------------------------------------------------
    # Drucker laden
    # -----------------------------------------------------------------------
    def load_printers(self):
        printers, default_p = get_installed_printers()
        display_list = []
        if default_p:
            display_list.append(f"Standard: {default_p}")
        for p in printers:
            if p != default_p and p not in display_list:
                display_list.append(p)

        if not display_list:
            display_list = ["Standarddrucker"]

        self.printer_combo["values"] = display_list
        self.printer_combo.current(0)

    def get_selected_printer_name(self) -> Optional[str]:
        val = self.printer_combo.get()
        if not val or val == "Standarddrucker":
            return None
        if val.startswith("Standard: "):
            return val.replace("Standard: ", "").strip()
        return val.strip()

    # -----------------------------------------------------------------------
    # Dateien & Ordner hinzufügen
    # -----------------------------------------------------------------------
    def add_files_dialog(self):
        files = filedialog.askopenfilenames(
            title="Code-Dateien auswählen",
            filetypes=[
                ("Alle unterstützten Dateien", "*.*"),
                ("Python (*.py)", "*.py"),
                ("Web (*.html, *.css, *.js, *.ts)", "*.html;*.css;*.js;*.ts"),
                ("JSON / YAML", "*.json;*.yaml;*.yml"),
            ]
        )
        if files:
            self.add_paths(list(files))

    def add_folder_dialog(self):
        folder = filedialog.askdirectory(title="Ordner mit Code-Dateien auswählen")
        if folder:
            self.add_paths([folder])

    def add_paths(self, paths: List[str]):
        added_count = 0
        for p in paths:
            p = os.path.abspath(p)
            if os.path.isdir(p):
                folder_files = scan_directory(p)
                for f in folder_files:
                    if self._add_single_file(f):
                        added_count += 1
            elif os.path.isfile(p):
                if is_text_or_code_file(p):
                    if self._add_single_file(p):
                        added_count += 1

        self.update_selection_label()
        self.lbl_status.configure(text=f"{len(self.file_items)} Datei(en) in der Liste ({added_count} neu hinzugefügt).")

    def _add_single_file(self, file_path: str) -> bool:
        if file_path in self.file_items:
            return False  # Bereits in Liste

        ext = os.path.splitext(file_path)[1].lower()
        type_str = ext[1:].upper() if ext else "TEXT"
        folder_path = os.path.dirname(file_path)
        name = os.path.basename(file_path)
        pdf_path = file_path + ".pdf"

        # Prüfen, ob PDF schon existiert
        has_existing_pdf = os.path.exists(pdf_path)
        status = "Bereits konvertiert" if has_existing_pdf else "Bereit"
        selected = True  # Standardmäßig für Druck ausgewählt

        item_id = self.tree.insert(
            "",
            "end",
            values=(
                "☑" if selected else "☐",
                name,
                type_str,
                folder_path,
                "-" if not has_existing_pdf else "Ja",
                status,
                pdf_path if has_existing_pdf else "-"
            )
        )

        self.file_items[file_path] = {
            "id": item_id,
            "path": file_path,
            "folder": folder_path,
            "name": name,
            "type": type_str,
            "selected": selected,
            "status": status,
            "pages": "-",
            "pdf_path": pdf_path if has_existing_pdf else ""
        }
        return True

    def remove_selected_from_list(self):
        selected_nodes = self.tree.selection()
        if not selected_nodes:
            return
        to_del = []
        for path, data in self.file_items.items():
            if data["id"] in selected_nodes:
                to_del.append(path)
                self.tree.delete(data["id"])
        for p in to_del:
            del self.file_items[p]
        self.update_selection_label()
        self.lbl_status.configure(text=f"{len(self.file_items)} Datei(en) in der Liste.")

    def clear_list(self):
        for data in self.file_items.values():
            self.tree.delete(data["id"])
        self.file_items.clear()
        self.update_selection_label()
        self.lbl_status.configure(text="Liste geleert.")

    # -----------------------------------------------------------------------
    # Auswahl-Interaktionen
    # -----------------------------------------------------------------------
    def on_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        column = self.tree.identify_column(event.x)
        row_id = self.tree.identify_row(event.y)

        # Wenn auf Checkbox-Spalte (#1) oder Zeile geklickt wird
        if row_id and column == "#1":
            self.toggle_single_item(row_id)

    def on_tree_space(self, event):
        for row_id in self.tree.selection():
            self.toggle_single_item(row_id)

    def toggle_single_item(self, row_id: str):
        for path, item in self.file_items.items():
            if item["id"] == row_id:
                item["selected"] = not item["selected"]
                self.update_tree_row(item)
                break
        self.update_selection_label()

    def toggle_highlighted_selection(self):
        for row_id in self.tree.selection():
            self.toggle_single_item(row_id)

    def toggle_all_selection(self):
        any_unselected = any(not item["selected"] for item in self.file_items.values())
        for item in self.file_items.values():
            item["selected"] = any_unselected
            self.update_tree_row(item)
        self.update_selection_label()

    def select_all_for_print(self):
        for item in self.file_items.values():
            item["selected"] = True
            self.update_tree_row(item)
        self.update_selection_label()

    def deselect_all_for_print(self):
        for item in self.file_items.values():
            item["selected"] = False
            self.update_tree_row(item)
        self.update_selection_label()

    def update_tree_row(self, item: Dict[str, Any]):
        self.tree.item(
            item["id"],
            values=(
                "☑" if item["selected"] else "☐",
                item["name"],
                item["type"],
                item["folder"],
                item["pages"],
                item["status"],
                item["pdf_path"] or "-"
            )
        )

    def update_selection_label(self):
        count = sum(1 for item in self.file_items.values() if item["selected"])
        total = len(self.file_items)
        self.lbl_selection_count.configure(text=f"{count} von {total} Dateien zum Drucken ausgewählt")

    # -----------------------------------------------------------------------
    # Vorschau & Finder Integration
    # -----------------------------------------------------------------------
    def on_tree_double_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return
        for item in self.file_items.values():
            if item["id"] == row_id:
                if item["pdf_path"] and os.path.exists(item["pdf_path"]):
                    open_in_preview(item["pdf_path"])
                else:
                    # Originaldatei öffnen
                    subprocess.run(["open", item["path"]], check=False)
                break

    def open_current_in_preview(self):
        selected_nodes = self.tree.selection()
        if not selected_nodes:
            messagebox.showinfo("Vorschau", "Bitte wählen Sie eine Zeile in der Tabelle aus.")
            return
        for row_id in selected_nodes:
            for item in self.file_items.values():
                if item["id"] == row_id:
                    if item["pdf_path"] and os.path.exists(item["pdf_path"]):
                        open_in_preview(item["pdf_path"])
                    else:
                        messagebox.showwarning(
                            "Noch nicht konvertiert",
                            f"Für '{item['name']}' existiert noch keine PDF-Datei. Bitte zuerst konvertieren!"
                        )

    def reveal_current_in_finder(self):
        selected_nodes = self.tree.selection()
        if not selected_nodes:
            return
        for row_id in selected_nodes:
            for item in self.file_items.values():
                if item["id"] == row_id:
                    target = item["pdf_path"] if (item["pdf_path"] and os.path.exists(item["pdf_path"])) else item["path"]
                    reveal_in_finder(target)
                    break

    def show_context_menu(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            if row_id not in self.tree.selection():
                self.tree.selection_set(row_id)
            self.context_menu.post(event.x_root, event.y_root)

    # -----------------------------------------------------------------------
    # Konvertierung (Hintergrund-Thread)
    # -----------------------------------------------------------------------
    def start_conversion(self):
        if not self.file_items:
            messagebox.showinfo("Keine Dateien", "Bitte fügen Sie zuerst Code-Dateien oder Ordner hinzu.")
            return

        footer_word = self.footer_entry.get().strip()
        style_name = self.style_combo.get().strip()

        self.btn_convert.configure(state="disabled")
        self.btn_print.configure(state="disabled")
        self.progress_bar["value"] = 0
        self.progress_bar["maximum"] = len(self.file_items)

        thread = threading.Thread(
            target=self._run_conversion,
            args=(footer_word, style_name),
            daemon=True
        )
        thread.start()

    def _run_conversion(self, footer_word: str, style_name: str):
        total = len(self.file_items)
        items_list = list(self.file_items.values())

        success_count = 0
        for idx, item in enumerate(items_list, start=1):
            src_path = item["path"]
            # PDF wird direkt im Quellordner als <name>.pdf gespeichert
            dest_pdf = src_path + ".pdf"

            self.root.after(0, self._update_conv_status, idx, total, item["name"])

            try:
                out_path, pages = convert_code_file_to_pdf(
                    input_path=src_path,
                    output_path=dest_pdf,
                    footer_word=footer_word,
                    style_name=style_name
                )
                item["pdf_path"] = out_path
                item["pages"] = str(pages)
                item["status"] = "Konvertiert"
                item["selected"] = True  # Nach Konvertierung für Druck vorwählen
                success_count += 1
            except Exception as e:
                item["status"] = f"Fehler: {e}"

            self.root.after(0, self._step_conv_progress, idx, item)

        self.root.after(0, self._finish_conversion, success_count, total)

    def _update_conv_status(self, current: int, total: int, filename: str):
        self.lbl_status.configure(text=f"Konvertiere {current} von {total}: {filename}...")

    def _step_conv_progress(self, idx: int, item: Dict[str, Any]):
        self.progress_bar["value"] = idx
        self.update_tree_row(item)
        self.update_selection_label()

    def _finish_conversion(self, success_count: int, total: int):
        self.btn_convert.configure(state="normal")
        self.btn_print.configure(state="normal")
        self.lbl_status.configure(text=f"Fertig: {success_count} von {total} Dateien erfolgreich als PDF konvertiert!")
        messagebox.showinfo(
            "Konvertierung abgeschlossen",
            f"{success_count} von {total} Dateien wurden erfolgreich im jeweiligen Originalordner als DIN-A4 PDF gespeichert.\n\n"
            "Sie können nun die gewünschten Dateien unten auswählen und direkt drucken!"
        )

    # -----------------------------------------------------------------------
    # Drucken (Hintergrund-Thread)
    # -----------------------------------------------------------------------
    def start_printing(self):
        # Alle ausgewählten Dateien ermitteln, für die eine PDF existiert
        to_print = []
        for item in self.file_items.values():
            if item["selected"]:
                if item["pdf_path"] and os.path.exists(item["pdf_path"]):
                    to_print.append(item)
                else:
                    # PDF fehlt noch
                    pass

        if not to_print:
            messagebox.showwarning(
                "Keine druckbereiten PDFs",
                "Es sind keine konvertierten PDF-Dateien zum Drucken ausgewählt.\n"
                "Bitte konvertieren Sie zuerst die Dateien über den Button '🚀 Alle Dateien als DIN-A4 PDF konvertieren' "
                "und aktivieren Sie die Häkchen bei den gewünschten Dateien."
            )
            return

        printer_name = self.get_selected_printer_name()
        printer_display = printer_name if printer_name else "Standarddrucker"

        try:
            copies = int(self.copies_spin.get())
            if copies < 1:
                copies = 1
        except Exception:
            copies = 1

        duplex = self.duplex_var.get()
        duplex_str = "Beidseitig (Duplex)" if duplex else "Einseitig"

        # Bestätigung anfordern
        confirm = messagebox.askyesno(
            "Druckauftrag bestätigen",
            f"Möchten Sie {len(to_print)} PDF-Datei(en) an folgenden Drucker senden?\n\n"
            f"• Drucker: {printer_display}\n"
            f"• Modus: {duplex_str}\n"
            f"• Kopien: {copies}\n\n"
            "Jetzt drucken?"
        )
        if not confirm:
            return

        self.btn_print.configure(state="disabled")
        self.lbl_status.configure(text=f"Drucke {len(to_print)} Datei(en)...")

        thread = threading.Thread(
            target=self._run_printing,
            args=(to_print, printer_name, copies, duplex),
            daemon=True
        )
        thread.start()

    def _run_printing(self, items_to_print: List[Dict[str, Any]], printer_name: Optional[str], copies: int, duplex: bool):
        success_count = 0
        total = len(items_to_print)

        for idx, item in enumerate(items_to_print, start=1):
            pdf_path = item["pdf_path"]
            self.root.after(0, lambda f=item["name"], i=idx: self.lbl_status.configure(text=f"Drucke {i}/{total}: {f}..."))

            ok, msg = print_pdf(
                pdf_path=pdf_path,
                printer_name=printer_name,
                copies=copies,
                duplex=duplex
            )

            if ok:
                item["status"] = "Gedruckt"
                success_count += 1
            else:
                item["status"] = f"Druckfehler"

            self.root.after(0, lambda it=item: self.update_tree_row(it))

        self.root.after(0, self._finish_printing, success_count, total)

    def _finish_printing(self, success_count: int, total: int):
        self.btn_print.configure(state="normal")
        self.lbl_status.configure(text=f"Druck abgeschlossen: {success_count} von {total} Aufträgen übermittelt.")
        messagebox.showinfo(
            "Druck abgeschlossen",
            f"{success_count} von {total} Druckaufträgen wurden erfolgreich an den Druckerdienst übermittelt."
        )


def main():
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    app = VSCtoPDFApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
