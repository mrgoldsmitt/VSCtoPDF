"""
gui.py - Native macOS Benutzeroberfläche für VSCtoPDF mit PySide6 und reinen SVG-Icons.
Ermöglicht Drag & Drop, Konvertierung in DIN-A4 PDF und selektiven Direktdruck.
"""

import os
import sys
import subprocess
from typing import List, Dict, Any, Optional

from PySide6.QtCore import Qt, QSize, QThread, Signal
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QComboBox,
    QSpinBox, QCheckBox, QProgressBar, QLabel, QHeaderView, QMenu,
    QFileDialog, QMessageBox, QGroupBox, QAbstractItemView
)

from converter import convert_code_file_to_pdf
from printer import get_installed_printers, print_pdf, open_in_preview, reveal_in_finder

def get_icons_dir() -> str:
    """Ermittelt den Pfad zum Icon-Verzeichnis (funktioniert im Quellcode und als macOS .app)."""
    if hasattr(sys, "_MEIPASS"):
        p = os.path.join(sys._MEIPASS, "assets", "icons")
        if os.path.exists(p):
            return p
    # macOS App Bundle (Contents/Resources/assets/icons)
    bundle_res = os.path.join(os.path.dirname(os.path.dirname(sys.executable)), "Resources", "assets", "icons")
    if os.path.exists(bundle_res):
        return bundle_res
    # Standard Pfad im Entwicklungsverzeichnis
    dev_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icons")
    if os.path.exists(dev_path):
        return dev_path
    return ""


def get_icon(name: str) -> QIcon:
    """Lädt ein SVG-Icon aus dem assets/icons Verzeichnis."""
    icons_dir = get_icons_dir()
    if icons_dir:
        path = os.path.join(icons_dir, name)
        if os.path.exists(path):
            return QIcon(path)
    return QIcon()


# Bekannte Code- & Text-Dateiendungen
CODE_EXTENSIONS = {
    ".html", ".htm", ".css", ".scss", ".sass", ".less", ".js", ".jsx",
    ".ts", ".tsx", ".vue", ".svelte", ".php", ".jsp", ".asp",
    ".py", ".pyw", ".ipynb", ".r", ".rmd", ".jl", ".json", ".yaml", ".yml", ".toml", ".xml",
    ".c", ".h", ".cpp", ".hpp", ".cc", ".hh", ".cxx", ".m", ".mm",
    ".swift", ".java", ".kt", ".kts", ".go", ".rs", ".cs", ".scala",
    ".sh", ".bash", ".zsh", ".fish", ".bat", ".cmd", ".ps1",
    ".ini", ".conf", ".cfg", ".env", ".dockerfile",
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
    basename = os.path.basename(filepath)
    if basename.startswith(".") and not basename.startswith(".env"):
        return False
    ext = os.path.splitext(filepath)[1].lower()
    if ext in IGNORED_EXTS:
        return False
    if ext in CODE_EXTENSIONS or basename.lower() in {"dockerfile", "makefile", "gemfile", "pipfile"}:
        return True
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return False
        return True
    except Exception:
        return False


def scan_directory(dir_path: str) -> List[str]:
    found_files = []
    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in IGNORED_DIRS]
        for f in files:
            fp = os.path.join(root, f)
            if is_text_or_code_file(fp):
                found_files.append(fp)
    return found_files


class ConversionWorker(QThread):
    progress = Signal(int, int, str)
    item_finished = Signal(dict)
    finished_all = Signal(int, int)

    def __init__(self, items: List[Dict[str, Any]], footer_word: str, style_name: str):
        super().__init__()
        self.items = items
        self.footer_word = footer_word
        self.style_name = style_name

    def run(self):
        total = len(self.items)
        success = 0
        for idx, item in enumerate(self.items, start=1):
            src_path = item["path"]
            dest_pdf = src_path + ".pdf"
            self.progress.emit(idx, total, item["name"])
            try:
                out_path, pages = convert_code_file_to_pdf(
                    input_path=src_path,
                    output_path=dest_pdf,
                    footer_word=self.footer_word,
                    style_name=self.style_name
                )
                item["pdf_path"] = out_path
                item["pages"] = str(pages)
                item["status"] = "Konvertiert"
                item["selected"] = True
                success += 1
            except Exception as e:
                item["status"] = f"Fehler: {e}"
            self.item_finished.emit(item)
        self.finished_all.emit(success, total)


class PrintingWorker(QThread):
    progress = Signal(int, int, str)
    item_finished = Signal(dict)
    finished_all = Signal(int, int)

    def __init__(self, items: List[Dict[str, Any]], printer_name: Optional[str], copies: int, duplex: bool):
        super().__init__()
        self.items = items
        self.printer_name = printer_name
        self.copies = copies
        self.duplex = duplex

    def run(self):
        total = len(self.items)
        success = 0
        for idx, item in enumerate(self.items, start=1):
            self.progress.emit(idx, total, item["name"])
            ok, msg = print_pdf(
                pdf_path=item["pdf_path"],
                printer_name=self.printer_name,
                copies=self.copies,
                duplex=self.duplex
            )
            if ok:
                item["status"] = "Gedruckt"
                success += 1
            else:
                item["status"] = "Druckfehler"
            self.item_finished.emit(item)
        self.finished_all.emit(success, total)


class VSCtoPDFMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VSCtoPDF – Code zu DIN-A4 PDF & Direktdruck")
        self.setWindowIcon(get_icon("app_icon.svg"))
        self.resize(1080, 720)
        self.setMinimumSize(880, 520)
        self.setAcceptDrops(True)

        self.file_items: Dict[str, Dict[str, Any]] = {}
        self.worker: Optional[QThread] = None

        self.setup_ui()
        self.load_printers()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(10)

        # -------------------------------------------------------------------
        # 1. Konfigurations-Bereich
        # -------------------------------------------------------------------
        cfg_group = QGroupBox("PDF- & Druck-Einstellungen")
        cfg_layout = QVBoxLayout(cfg_group)
        cfg_layout.setSpacing(8)

        # Zeile 1
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        lbl_footer = QLabel("Fußzeile (links):")
        lbl_footer.setStyleSheet("font-weight: bold;")
        self.txt_footer = QLineEdit("Code-Dokumentation")
        self.txt_footer.setPlaceholderText("z.B. Vertraulich oder Projektname")
        self.txt_footer.setFixedWidth(200)

        lbl_printer = QLabel("Drucker:")
        lbl_printer.setStyleSheet("font-weight: bold;")
        self.combo_printer = QComboBox()
        self.combo_printer.setMinimumWidth(260)

        self.btn_reload_printers = QPushButton()
        self.btn_reload_printers.setIcon(get_icon("refresh.svg"))
        self.btn_reload_printers.setToolTip("Druckerliste aktualisieren")
        self.btn_reload_printers.setFixedSize(30, 30)
        self.btn_reload_printers.clicked.connect(self.load_printers)

        row1.addWidget(lbl_footer)
        row1.addWidget(self.txt_footer)
        row1.addSpacing(16)
        row1.addWidget(lbl_printer)
        row1.addWidget(self.combo_printer)
        row1.addWidget(self.btn_reload_printers)
        row1.addStretch()
        cfg_layout.addLayout(row1)

        # Zeile 2
        row2 = QHBoxLayout()
        row2.setSpacing(12)

        lbl_style = QLabel("Syntax-Farbschema:")
        self.combo_style = QComboBox()
        self.combo_style.addItems(["friendly", "default", "colorful", "bw"])
        self.combo_style.setFixedWidth(120)

        self.chk_duplex = QCheckBox("Beidseitig drucken (Duplex)")
        self.chk_duplex.setChecked(True)

        lbl_copies = QLabel("Kopien:")
        self.spin_copies = QSpinBox()
        self.spin_copies.setRange(1, 99)
        self.spin_copies.setValue(1)
        self.spin_copies.setFixedWidth(65)

        lbl_info = QLabel("ℹ️ DIN-A4 Kopfzeile enthält automatisch den Ordner-Pfad.")
        lbl_info.setStyleSheet("color: #64748b; font-size: 11px;")

        row2.addWidget(lbl_style)
        row2.addWidget(self.combo_style)
        row2.addSpacing(16)
        row2.addWidget(self.chk_duplex)
        row2.addSpacing(16)
        row2.addWidget(lbl_copies)
        row2.addWidget(self.spin_copies)
        row2.addStretch()
        row2.addWidget(lbl_info)
        cfg_layout.addLayout(row2)

        main_layout.addWidget(cfg_group)

        # -------------------------------------------------------------------
        # 2. Dateiverwaltungsleiste
        # -------------------------------------------------------------------
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(8)

        self.btn_add_files = QPushButton("Dateien hinzufügen...")
        self.btn_add_files.setIcon(get_icon("add_files.svg"))
        self.btn_add_files.setIconSize(QSize(18, 18))
        self.btn_add_files.clicked.connect(self.add_files_dialog)

        self.btn_add_folder = QPushButton("Ordner hinzufügen...")
        self.btn_add_folder.setIcon(get_icon("add_folder.svg"))
        self.btn_add_folder.setIconSize(QSize(18, 18))
        self.btn_add_folder.clicked.connect(self.add_folder_dialog)

        self.btn_remove = QPushButton("Aus Liste entfernen")
        self.btn_remove.setIcon(get_icon("delete.svg"))
        self.btn_remove.setIconSize(QSize(18, 18))
        self.btn_remove.clicked.connect(self.remove_selected_from_list)

        self.btn_clear = QPushButton("Liste leeren")
        self.btn_clear.setIcon(get_icon("clear.svg"))
        self.btn_clear.setIconSize(QSize(18, 18))
        self.btn_clear.clicked.connect(self.clear_list)

        lbl_dnd_hint = QLabel("💡 Dateien oder Ordner einfach per Drag & Drop hier hineinziehen!")
        lbl_dnd_hint.setStyleSheet("color: #2563eb; font-style: italic;")

        btn_bar.addWidget(self.btn_add_files)
        btn_bar.addWidget(self.btn_add_folder)
        btn_bar.addSpacing(10)
        btn_bar.addWidget(self.btn_remove)
        btn_bar.addWidget(self.btn_clear)
        btn_bar.addStretch()
        btn_bar.addWidget(lbl_dnd_hint)
        main_layout.addLayout(btn_bar)

        # -------------------------------------------------------------------
        # 3. Datei-Tabelle mit Checkboxen
        # -------------------------------------------------------------------
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Drucken", "Dateiname", "Dateityp", "Ordner-Pfad", "Seiten", "Status", "PDF-Pfad"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Interactive)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(6, 220)

        self.table.itemClicked.connect(self.on_table_item_clicked)
        self.table.itemDoubleClicked.connect(self.on_table_double_clicked)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        main_layout.addWidget(self.table)

        # -------------------------------------------------------------------
        # 4. Konvertierungsleiste
        # -------------------------------------------------------------------
        conv_bar = QHBoxLayout()
        conv_bar.setSpacing(10)

        self.btn_convert = QPushButton("Alle Dateien als DIN-A4 PDF konvertieren")
        self.btn_convert.setIcon(get_icon("convert.svg"))
        self.btn_convert.setIconSize(QSize(20, 20))
        self.btn_convert.setStyleSheet("font-weight: bold; padding: 6px 12px;")
        self.btn_convert.clicked.connect(self.start_conversion)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.lbl_status = QLabel("Bereit – keine Dateien geladen")
        self.lbl_status.setStyleSheet("color: #475569;")

        conv_bar.addWidget(self.btn_convert)
        conv_bar.addWidget(self.progress_bar, 1)
        conv_bar.addWidget(self.lbl_status)
        main_layout.addLayout(conv_bar)

        # -------------------------------------------------------------------
        # 5. Druckleiste
        # -------------------------------------------------------------------
        print_group = QGroupBox("Druckauswahl & Druckauftrag")
        print_layout = QHBoxLayout(print_group)
        print_layout.setSpacing(8)

        self.btn_sel_all = QPushButton("Alle auswählen")
        self.btn_sel_all.setIcon(get_icon("select_all.svg"))
        self.btn_sel_all.clicked.connect(self.select_all_for_print)

        self.btn_desel_all = QPushButton("Auswahl aufheben")
        self.btn_desel_all.setIcon(get_icon("deselect_all.svg"))
        self.btn_desel_all.clicked.connect(self.deselect_all_for_print)

        self.btn_print = QPushButton("Ausgewählte PDFs drucken")
        self.btn_print.setIcon(get_icon("print.svg"))
        self.btn_print.setIconSize(QSize(20, 20))
        self.btn_print.setStyleSheet("font-weight: bold; padding: 6px 14px;")
        self.btn_print.clicked.connect(self.start_printing)

        self.btn_preview = QPushButton("In Vorschau öffnen")
        self.btn_preview.setIcon(get_icon("preview.svg"))
        self.btn_preview.clicked.connect(self.open_current_in_preview)

        self.btn_finder = QPushButton("Im Finder zeigen")
        self.btn_finder.setIcon(get_icon("finder.svg"))
        self.btn_finder.clicked.connect(self.reveal_current_in_finder)

        self.lbl_selection_count = QLabel("0 Dateien zum Drucken ausgewählt")
        self.lbl_selection_count.setStyleSheet("font-weight: bold; color: #1e3a8a;")

        print_layout.addWidget(self.btn_sel_all)
        print_layout.addWidget(self.btn_desel_all)
        print_layout.addSpacing(10)
        print_layout.addWidget(self.btn_print)
        print_layout.addWidget(self.btn_preview)
        print_layout.addWidget(self.btn_finder)
        print_layout.addStretch()
        print_layout.addWidget(self.lbl_selection_count)

        main_layout.addWidget(print_group)

    # -----------------------------------------------------------------------
    # Drag & Drop Events
    # -----------------------------------------------------------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        paths = []
        for url in event.mimeData().urls():
            local_path = url.toLocalFile()
            if local_path:
                paths.append(local_path)
        if paths:
            self.add_paths(paths)
            event.acceptProposedAction()

    # -----------------------------------------------------------------------
    # Drucker laden
    # -----------------------------------------------------------------------
    def load_printers(self):
        printers, default_p = get_installed_printers()
        self.combo_printer.clear()
        if default_p:
            self.combo_printer.addItem(f"Standard: {default_p}", default_p)
        for p in printers:
            if p != default_p:
                self.combo_printer.addItem(p, p)
        if self.combo_printer.count() == 0:
            self.combo_printer.addItem("Standarddrucker", None)

    def get_selected_printer_name(self) -> Optional[str]:
        data = self.combo_printer.currentData()
        if data:
            return data
        txt = self.combo_printer.currentText()
        if txt.startswith("Standard: "):
            return txt.replace("Standard: ", "").strip()
        if txt == "Standarddrucker":
            return None
        return txt

    # -----------------------------------------------------------------------
    # Dateien & Ordner hinzufügen
    # -----------------------------------------------------------------------
    def add_files_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Code-Dateien auswählen",
            "",
            "Alle Dateien (*.*);;Python (*.py);;Web (*.html *.css *.js *.ts);;JSON / YAML (*.json *.yaml *.yml)"
        )
        if files:
            self.add_paths(files)

    def add_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Ordner mit Code-Dateien auswählen")
        if folder:
            self.add_paths([folder])

    def add_paths(self, paths: List[str]):
        added = 0
        for p in paths:
            p = os.path.abspath(p)
            if os.path.isdir(p):
                for f in scan_directory(p):
                    if self._add_single_file(f):
                        added += 1
            elif os.path.isfile(p):
                if is_text_or_code_file(p):
                    if self._add_single_file(p):
                        added += 1
        self.update_selection_label()
        self.lbl_status.setText(f"{len(self.file_items)} Datei(en) in der Liste ({added} neu hinzugefügt).")

    def _add_single_file(self, file_path: str) -> bool:
        if file_path in self.file_items:
            return False

        ext = os.path.splitext(file_path)[1].lower()
        type_str = ext[1:].upper() if ext else "TEXT"
        folder_path = os.path.dirname(file_path)
        name = os.path.basename(file_path)
        pdf_path = file_path + ".pdf"
        has_pdf = os.path.exists(pdf_path)
        status = "Bereits konvertiert" if has_pdf else "Bereit"
        selected = True

        row = self.table.rowCount()
        self.table.insertRow(row)

        chk_item = QTableWidgetItem()
        chk_item.setCheckState(Qt.Checked if selected else Qt.Unchecked)
        chk_item.setTextAlignment(Qt.AlignCenter)

        name_item = QTableWidgetItem(name)
        name_item.setIcon(get_icon("file_code.svg"))

        type_item = QTableWidgetItem(type_str)
        type_item.setTextAlignment(Qt.AlignCenter)

        folder_item = QTableWidgetItem(folder_path)

        pages_item = QTableWidgetItem("Ja" if has_pdf else "-")
        pages_item.setTextAlignment(Qt.AlignCenter)

        status_item = QTableWidgetItem(status)
        status_item.setTextAlignment(Qt.AlignCenter)

        pdf_item = QTableWidgetItem(pdf_path if has_pdf else "-")

        self.table.setItem(row, 0, chk_item)
        self.table.setItem(row, 1, name_item)
        self.table.setItem(row, 2, type_item)
        self.table.setItem(row, 3, folder_item)
        self.table.setItem(row, 4, pages_item)
        self.table.setItem(row, 5, status_item)
        self.table.setItem(row, 6, pdf_item)

        self.file_items[file_path] = {
            "row": row,
            "path": file_path,
            "folder": folder_path,
            "name": name,
            "type": type_str,
            "selected": selected,
            "status": status,
            "pages": "-" if not has_pdf else "Ja",
            "pdf_path": pdf_path if has_pdf else ""
        }
        return True

    def remove_selected_from_list(self):
        selected_rows = sorted(set(idx.row() for idx in self.table.selectedIndexes()), reverse=True)
        if not selected_rows:
            return
        for r in selected_rows:
            # Pfad ermitteln
            path_to_remove = None
            for p, item in self.file_items.items():
                if item["row"] == r:
                    path_to_remove = p
                    break
            if path_to_remove:
                del self.file_items[path_to_remove]
            self.table.removeRow(r)

        # Zeilenindizes aktualisieren
        self._reindex_rows()
        self.update_selection_label()
        self.lbl_status.setText(f"{len(self.file_items)} Datei(en) in der Liste.")

    def clear_list(self):
        self.table.setRowCount(0)
        self.file_items.clear()
        self.update_selection_label()
        self.lbl_status.setText("Liste geleert.")

    def _reindex_rows(self):
        for r in range(self.table.rowCount()):
            folder = self.table.item(r, 3).text()
            name = self.table.item(r, 1).text()
            p = os.path.join(folder, name)
            if p in self.file_items:
                self.file_items[p]["row"] = r

    # -----------------------------------------------------------------------
    # Auswahl-Interaktionen
    # -----------------------------------------------------------------------
    def on_table_item_clicked(self, item: QTableWidgetItem):
        if item.column() == 0:
            row = item.row()
            is_checked = (item.checkState() == Qt.Checked)
            for it in self.file_items.values():
                if it["row"] == row:
                    it["selected"] = is_checked
                    break
            self.update_selection_label()

    def select_all_for_print(self):
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 0)
            if item:
                item.setCheckState(Qt.Checked)
        for it in self.file_items.values():
            it["selected"] = True
        self.update_selection_label()

    def deselect_all_for_print(self):
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 0)
            if item:
                item.setCheckState(Qt.Unchecked)
        for it in self.file_items.values():
            it["selected"] = False
        self.update_selection_label()

    def update_selection_label(self):
        count = sum(1 for it in self.file_items.values() if it["selected"])
        total = len(self.file_items)
        self.lbl_selection_count.setText(f"{count} von {total} Dateien zum Drucken ausgewählt")

    # -----------------------------------------------------------------------
    # Vorschau & Finder Integration
    # -----------------------------------------------------------------------
    def on_table_double_clicked(self, item: QTableWidgetItem):
        row = item.row()
        for it in self.file_items.values():
            if it["row"] == row:
                if it["pdf_path"] and os.path.exists(it["pdf_path"]):
                    open_in_preview(it["pdf_path"])
                else:
                    subprocess.run(["open", it["path"]], check=False)
                break

    def open_current_in_preview(self):
        curr_row = self.table.currentRow()
        if curr_row < 0:
            QMessageBox.information(self, "Vorschau", "Bitte wählen Sie eine Zeile in der Tabelle aus.")
            return
        for it in self.file_items.values():
            if it["row"] == curr_row:
                if it["pdf_path"] and os.path.exists(it["pdf_path"]):
                    open_in_preview(it["pdf_path"])
                else:
                    QMessageBox.warning(self, "Nicht konvertiert", f"Für '{it['name']}' existiert noch kein PDF.")
                break

    def reveal_current_in_finder(self):
        curr_row = self.table.currentRow()
        if curr_row < 0:
            return
        for it in self.file_items.values():
            if it["row"] == curr_row:
                target = it["pdf_path"] if (it["pdf_path"] and os.path.exists(it["pdf_path"])) else it["path"]
                reveal_in_finder(target)
                break

    def show_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        act_preview = QAction(get_icon("preview.svg"), "In Vorschau öffnen", self)
        act_preview.triggered.connect(self.open_current_in_preview)
        act_finder = QAction(get_icon("finder.svg"), "Im Finder zeigen", self)
        act_finder.triggered.connect(self.reveal_current_in_finder)
        act_remove = QAction(get_icon("delete.svg"), "Aus Liste entfernen", self)
        act_remove.triggered.connect(self.remove_selected_from_list)

        menu.addAction(act_preview)
        menu.addAction(act_finder)
        menu.addSeparator()
        menu.addAction(act_remove)
        menu.exec(self.table.viewport().mapToGlobal(pos))

    # -----------------------------------------------------------------------
    # Konvertierung (QThread)
    # -----------------------------------------------------------------------
    def start_conversion(self):
        if not self.file_items:
            QMessageBox.information(self, "Keine Dateien", "Bitte fügen Sie zuerst Code-Dateien oder Ordner hinzu.")
            return

        footer_word = self.txt_footer.text().strip()
        style_name = self.combo_style.currentText().strip()

        self.btn_convert.setEnabled(False)
        self.btn_print.setEnabled(False)
        self.progress_bar.setValue(0)

        self.worker = ConversionWorker(list(self.file_items.values()), footer_word, style_name)
        self.worker.progress.connect(self._on_conv_progress)
        self.worker.item_finished.connect(self._on_conv_item_finished)
        self.worker.finished_all.connect(self._on_conv_finished)
        self.worker.start()

    def _on_conv_progress(self, current: int, total: int, filename: str):
        self.lbl_status.setText(f"Konvertiere {current} von {total}: {filename}...")
        pct = int((current / total) * 100)
        self.progress_bar.setValue(pct)

    def _on_conv_item_finished(self, item: Dict[str, Any]):
        r = item["row"]
        # Spalte 0 (Checkbox)
        chk = self.table.item(r, 0)
        if chk:
            chk.setCheckState(Qt.Checked if item["selected"] else Qt.Unchecked)
        # Spalte 4 (Seiten)
        p_item = self.table.item(r, 4)
        if p_item:
            p_item.setText(item["pages"])
        # Spalte 5 (Status)
        s_item = self.table.item(r, 5)
        if s_item:
            s_item.setText(item["status"])
        # Spalte 6 (PDF-Pfad)
        pdf_item = self.table.item(r, 6)
        if pdf_item:
            pdf_item.setText(item["pdf_path"])
        self.update_selection_label()

    def _on_conv_finished(self, success: int, total: int):
        self.btn_convert.setEnabled(True)
        self.btn_print.setEnabled(True)
        self.progress_bar.setValue(100)
        self.lbl_status.setText(f"Fertig: {success} von {total} Dateien als PDF konvertiert!")
        QMessageBox.showinfo(
            self,
            "Konvertierung abgeschlossen",
            f"{success} von {total} Dateien wurden erfolgreich als DIN-A4 PDF im Quellordner gespeichert.\n\n"
            "Wählen Sie nun die Dateien aus, die Sie direkt drucken möchten."
        )

    # -----------------------------------------------------------------------
    # Drucken (QThread)
    # -----------------------------------------------------------------------
    def start_printing(self):
        to_print = [it for it in self.file_items.values() if it["selected"] and it["pdf_path"] and os.path.exists(it["pdf_path"])]
        if not to_print:
            QMessageBox.warning(
                self,
                "Keine druckbereiten PDFs",
                "Es sind keine konvertierten PDFs zum Drucken ausgewählt.\n"
                "Bitte konvertieren Sie zuerst die Dateien und wählen Sie die Checkboxen an."
            )
            return

        printer_name = self.get_selected_printer_name()
        printer_display = printer_name if printer_name else "Standarddrucker"
        copies = self.spin_copies.value()
        duplex = self.chk_duplex.isChecked()
        duplex_str = "Beidseitig (Duplex)" if duplex else "Einseitig"

        ret = QMessageBox.question(
            self,
            "Druckauftrag bestätigen",
            f"Möchten Sie {len(to_print)} PDF-Datei(en) drucken?\n\n"
            f"• Drucker: {printer_display}\n"
            f"• Modus: {duplex_str}\n"
            f"• Kopien: {copies}\n\n"
            "Jetzt drucken?",
            QMessageBox.Yes | QMessageBox.No
        )
        if ret != QMessageBox.Yes:
            return

        self.btn_print.setEnabled(False)
        self.lbl_status.setText(f"Drucke {len(to_print)} Datei(en)...")

        self.worker = PrintingWorker(to_print, printer_name, copies, duplex)
        self.worker.progress.connect(lambda cur, tot, fn: self.lbl_status.setText(f"Drucke {cur}/{tot}: {fn}..."))
        self.worker.item_finished.connect(self._on_print_item_finished)
        self.worker.finished_all.connect(self._on_print_finished)
        self.worker.start()

    def _on_print_item_finished(self, item: Dict[str, Any]):
        r = item["row"]
        s_item = self.table.item(r, 5)
        if s_item:
            s_item.setText(item["status"])

    def _on_print_finished(self, success: int, total: int):
        self.btn_print.setEnabled(True)
        self.lbl_status.setText(f"Druck abgeschlossen: {success} von {total} Aufträgen gesendet.")
        QMessageBox.showinfo(
            self,
            "Druck abgeschlossen",
            f"{success} von {total} Druckaufträgen wurden erfolgreich an den Drucker übermittelt."
        )


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("VSCtoPDF")
    window = VSCtoPDFMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
