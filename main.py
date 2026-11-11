#!/usr/bin/env python3
"""
main.py - Hauptprogramm für VSCtoPDF.
Startet standardmäßig die native macOS Benutzeroberfläche (PySide6 mit SVG-Icons).
Kann bei Bedarf auch als CLI-Tool verwendet werden.
"""

import sys
import os
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from converter import convert_code_file_to_pdf
from printer import get_installed_printers, print_pdf
from version import APP_NAME, APP_VERSION, CHANGELOG_TEXT


def run_cli(args):
    """Kommandozeilen-Modus für Skripte und Batch-Verarbeitung."""
    print("=== VSCtoPDF CLI-Modus ===")
    from gui import scan_directory, is_text_or_code_file

    targets = []
    for item in args.inputs:
        item = os.path.abspath(item)
        if os.path.isdir(item):
            targets.extend(scan_directory(item))
        elif os.path.isfile(item) and is_text_or_code_file(item):
            targets.append(item)
        else:
            print(f"Warnung: '{item}' ist keine lesbare Code-/Textdatei oder existiert nicht.")

    if not targets:
        print("Keine konvertierbaren Dateien gefunden.")
        sys.exit(1)

    print(f"{len(targets)} Datei(en) gefunden.")
    generated_pdfs = []

    for idx, f in enumerate(targets, start=1):
        try:
            pdf_path, pages = convert_code_file_to_pdf(
                input_path=f,
                footer_word=args.word,
                style_name=args.style
            )
            print(f"[{idx}/{len(targets)}] {os.path.basename(f)} -> {pdf_path} ({pages} Seiten)")
            generated_pdfs.append(pdf_path)
        except Exception as e:
            print(f"[{idx}/{len(targets)}] FEHLER bei {f}: {e}")

    if args.print:
        print(f"\nSende {len(generated_pdfs)} PDF-Dateien an Drucker...")
        printers, default_p = get_installed_printers()
        target_printer = args.printer or default_p
        print(f"Ziel-Drucker: {target_printer or 'System-Standard'}")

        for pdf in generated_pdfs:
            ok, msg = print_pdf(
                pdf_path=pdf,
                printer_name=target_printer,
                copies=args.copies,
                duplex=not args.simplex
            )
            status = "OK" if ok else "FEHLER"
            print(f"  [{status}] {os.path.basename(pdf)}: {msg}")

    print("\nFertig!")


def main():
    if len(sys.argv) > 1 and not (len(sys.argv) == 2 and sys.argv[1].startswith("-psn")):
        parser = argparse.ArgumentParser(
            description="Konvertiert Code-Dateien in DIN-A4 PDF und druckt sie optional auf macOS."
        )
        parser.add_argument("-v", "--version", action="version", version=f"{APP_NAME} {APP_VERSION}")
        parser.add_argument("--changelog", action="store_true", help="Zeigt den Changelog der Anwendung an")
        parser.add_argument("inputs", nargs="*", help="Dateien oder Ordner zur Konvertierung")
        parser.add_argument("--word", "-w", default="Code-Dokumentation", help="Benutzerwort in der linken Fußzeile")
        parser.add_argument("--style", "-s", default="friendly", help="Pygments Farbschema (friendly, default, bw, etc.)")
        parser.add_argument("--print", "-p", action="store_true", help="PDFs nach der Konvertierung direkt drucken")
        parser.add_argument("--printer", help="Name des Ziel-Druckers (Standard: System-Standarddrucker)")
        parser.add_argument("--copies", "-c", type=int, default=1, help="Anzahl der Kopien")
        parser.add_argument("--simplex", action="store_true", help="Einseitig drucken (Standard ist Duplex)")
        parser.add_argument("--gui", "-g", action="store_true", help="GUI mit den übergebenen Dateien öffnen")

        args = parser.parse_args()

        if args.changelog:
            print(f"=== {APP_NAME} Changelog ===")
            print(CHANGELOG_TEXT)
            sys.exit(0)

        if args.gui or not args.inputs:
            from PySide6.QtWidgets import QApplication
            from gui import VSCtoPDFMainWindow
            app = QApplication(sys.argv)
            app.setApplicationName("VSCtoPDF")
            window = VSCtoPDFMainWindow()
            if args.inputs:
                window.add_paths(args.inputs)
            if args.word:
                window.txt_footer.setText(args.word)
            window.show()
            sys.exit(app.exec())
        else:
            run_cli(args)
    else:
        from PySide6.QtWidgets import QApplication
        from gui import VSCtoPDFMainWindow
        app = QApplication(sys.argv)
        app.setApplicationName("VSCtoPDF")
        window = VSCtoPDFMainWindow()
        window.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
