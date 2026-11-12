"""
converter.py - Konvertierung von Code-Dateien in DIN-A4 PDFs mit Syntax-Highlighting,
Kopfzeile (Ordner-Pfad) und Fußzeile (Benutzerwort + Seite/Gesamte Seiten).
"""

import os
import re
import html
from typing import Optional, Tuple

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import pygments
from pygments.lexers import get_lexer_for_filename, TextLexer, guess_lexer
from pygments.styles import get_style_by_name
import pypdf

# ---------------------------------------------------------------------------
# Schrifterkennung & Registrierung (Menlo für macOS, sonst Standard-Courier)
# ---------------------------------------------------------------------------
CODE_FONT_NAME = "Courier"
try:
    menlo_path = "/System/Library/Fonts/Menlo.ttc"
    if os.path.exists(menlo_path):
        pdfmetrics.registerFont(TTFont("Menlo", menlo_path, subfontIndex=0))
        pdfmetrics.registerFont(TTFont("Menlo-Bold", menlo_path, subfontIndex=1))
        pdfmetrics.registerFont(TTFont("Menlo-Italic", menlo_path, subfontIndex=2))
        pdfmetrics.registerFont(TTFont("Menlo-BoldItalic", menlo_path, subfontIndex=3))
        pdfmetrics.registerFontFamily(
            "Menlo",
            normal="Menlo",
            bold="Menlo-Bold",
            italic="Menlo-Italic",
            boldItalic="Menlo-BoldItalic",
        )
        CODE_FONT_NAME = "Menlo"
except Exception:
    CODE_FONT_NAME = "Courier"


class NumberedCanvas(canvas.Canvas):
    """
    Zweistufiger ReportLab-Canvas für exakte Gesamtseitenzahlen ("Seite X/Y"),
    Kopfzeile mit Ordner-Pfad und Fußzeile mit frei definiertem Benutzerwort.
    """
    page_width, page_height = A4
    left_m = 36.0
    right_m = 595.27 - 36.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.folder_path = ""
        self.file_name = ""
        self.footer_word = ""

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages: int):
        self.saveState()
        h = self.page_height

        # ---------------- Kopfzeile ----------------
        avail_w = self.right_m - self.left_m
        full_folder_str = f"Ordner: {self.folder_path}"

        # Dynamische Schrift- und Zeilenanpassung: Der Ordnerpfad wird immer VOLLSTÄNDIG dargestellt
        f_size = 8.0
        text_w = self.stringWidth(full_folder_str, "Helvetica", f_size)
        if text_w > avail_w:
            f_size = max(6.5, 8.0 * (avail_w / text_w))
            text_w = self.stringWidth(full_folder_str, "Helvetica", f_size)

        self.setFont("Helvetica", f_size)
        self.setFillColorRGB(0.38, 0.42, 0.48)

        if text_w <= avail_w:
            self.drawString(self.left_m, h - 26, full_folder_str)
        else:
            # Bei extrem langen Pfaden sauber auf zwei Zeilen verteilen
            split_idx = len(self.folder_path) // 2
            slash_idx = self.folder_path.rfind("/", 0, split_idx + 15)
            if slash_idx == -1:
                slash_idx = split_idx
            part1 = f"Ordner: {self.folder_path[:slash_idx+1]}"
            part2 = f"        {self.folder_path[slash_idx+1:]}"
            self.setFont("Helvetica", 6.5)
            self.drawString(self.left_m, h - 22, part1)
            self.drawString(self.left_m, h - 29, part2)

        # Dateiname
        self.setFont("Helvetica-Bold", 9)
        self.setFillColorRGB(0.12, 0.15, 0.20)
        self.drawString(self.left_m, h - 38, f"Datei: {self.file_name}")

        # Trennlinie unter Kopfzeile
        self.setStrokeColorRGB(0.80, 0.83, 0.87)
        self.setLineWidth(0.75)
        self.line(self.left_m, h - 44, self.right_m, h - 44)

        # ---------------- Fußzeile ----------------
        # Trennlinie über Fußzeile
        self.line(self.left_m, 40, self.right_m, 40)
        self.setFont("Helvetica", 8)
        self.setFillColorRGB(0.38, 0.42, 0.48)

        # Links: Benutzerdefiniertes Wort
        if self.footer_word:
            self.drawString(self.left_m, 28, str(self.footer_word))

        # Rechts: Seite/Gesamte Seiten
        page_str = f"Seite {self._pageNumber}/{total_pages}"
        self.drawRightString(self.right_m, 28, page_str)

        self.restoreState()


def make_canvas_factory(folder_path: str, file_name: str, footer_word: str):
    """Erzeugt eine spezialisierte Canvas-Klasse mit den übergebenen Metadaten."""
    class CustomCanvas(NumberedCanvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.folder_path = folder_path
            self.file_name = file_name
            self.footer_word = footer_word
    return CustomCanvas


def read_file_safely(file_path: str) -> str:
    """Liest Textdateien mit mehreren Fallback-Encodings ein."""
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def convert_code_file_to_pdf(
    input_path: str,
    output_path: Optional[str] = None,
    footer_word: str = "",
    style_name: str = "friendly"
) -> Tuple[str, int]:
    """
    Konvertiert eine Quellcodedatei in eine DIN-A4 PDF-Datei.

    :param input_path: Pfad zur Quellcodedatei
    :param output_path: Ziel-PDF (Standard: gleicher Ordner wie Originaldatei + '.pdf')
    :param footer_word: Benutzerdefiniertes Wort in der linken Fußzeile
    :param style_name: Pygments Farbschema ('friendly', 'default', 'colorful', 'bw')
    :return: (generierter_pdf_pfad, anzahl_seiten)
    """
    input_path = os.path.abspath(input_path)
    folder_path = os.path.dirname(input_path)
    file_name = os.path.basename(input_path)

    # Standard-Zielpfad: Exakt im gleichen Verzeichnis wie die Originaldatei
    if output_path is None:
        output_path = input_path + ".pdf"

    code_text = read_file_safely(input_path)

    # Lexer für Syntax-Highlighting ermitteln
    try:
        lexer = get_lexer_for_filename(input_path, code_text)
    except Exception:
        try:
            lexer = guess_lexer(code_text)
        except Exception:
            lexer = TextLexer()

    try:
        style = get_style_by_name(style_name)
    except Exception:
        style = get_style_by_name("friendly")

    tokens = pygments.lex(code_text, lexer)

    # Tokens zeilenweise in ReportLab-kompatibles HTML aufteilen
    lines_formatted = [[]]
    for ttype, value in tokens:
        t_style = style.style_for_token(ttype)
        color = t_style.get("color")
        bold = t_style.get("bold")
        italic = t_style.get("italic")

        parts = value.split("\n")
        for i, part in enumerate(parts):
            if i > 0:
                lines_formatted.append([])
            if part:
                part = part.expandtabs(4)
                esc = html.escape(part)
                # Whitespace erhalten
                esc = re.sub(r" {2,}", lambda m: "&nbsp;" * len(m.group(0)), esc)
                esc = esc.replace(" ", "&nbsp;")
                span = esc
                if color:
                    span = f'<font color="#{color}">{span}</font>'
                if bold:
                    span = f"<b>{span}</b>"
                if italic:
                    span = f"<i>{span}</i>"
                lines_formatted[-1].append(span)

    # Falls die Datei mit einem Zeilenumbruch endete, letzte leere Zeile erhalten
    total_lines = len(lines_formatted)
    digits = max(len(str(total_lines)), 3)
    char_w = 4.8  # Ungefähre Zeichenbreite bei 8pt Monospace
    prefix_chars = digits + 3  # z.B. '   1 | '
    left_indent = prefix_chars * char_w + 4

    styles = getSampleStyleSheet()
    code_style = ParagraphStyle(
        "CodeStyle",
        parent=styles["Normal"],
        fontName=CODE_FONT_NAME,
        fontSize=8,
        leading=10.2,
        leftIndent=left_indent,
        firstLineIndent=-left_indent,
        wordWrap="CJK",
    )

    story = []
    for idx, line_spans in enumerate(lines_formatted, start=1):
        num_str = f"{idx:{digits}d}"
        prefix = f'<font color="#8892b0">{num_str}&nbsp;|&nbsp;</font>'
        content = "".join(line_spans)
        if not content:
            content = "&nbsp;"
        story.append(Paragraph(prefix + content, code_style))

    # Dokument erzeugen (DIN-A4: 595.27 x 841.89 pt)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=52,
        bottomMargin=48,
    )
    canvas_cls = make_canvas_factory(folder_path, file_name, footer_word)
    doc.build(story, canvasmaker=canvas_cls)

    # Seitenzahl auslesen
    page_count = 1
    try:
        reader = pypdf.PdfReader(output_path)
        page_count = len(reader.pages)
    except Exception:
        pass

    return output_path, page_count
