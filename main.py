#!/usr/bin/env python3
"""
main.py - Hauptprogramm für VSCtoPDF.
Startet standardmäßig die macOS GUI. Kann bei Bedarf auch als CLI-Tool verwendet werden.
"""

import sys
import os
import argparse

# Sicherstellen, dass das aktuelle Skriptverzeichnis im Python-Pfad liegt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from converter import convert_code_file_to_pdf
from printer import get_installed_printers, print_pdf


def run_cli(args):
    """Kommandozeilen-Modus für Skripte und Batch-Verarbeitung."""
    print(f"=== VSCtoPDF CLI-Modus ===")
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
        # CLI Argumente parsen
        parser = argparse.ArgumentParser(
            description="Konvertiert Code-Dateien in DIN-A4 PDF und druckt sie optional auf macOS."
        )
        parser.add_argument("inputs", nargs="*", help="Dateien oder Ordner zur Konvertierung")
        parser.add_argument("--word", "-w", default="Code-Dokumentation", help="Benutzerwort in der linken Fußzeile")
        parser.add_argument("--style", "-s", default="friendly", help="Pygments Farbschema (friendly, default, bw, etc.)")
        parser.add_argument("--print", "-p", action="store_true", help="PDFs nach der Konvertierung direkt drucken")
        parser.add_argument("--printer", help="Name des Ziel-Druckers (Standard: System-Standarddrucker)")
        parser.add_argument("--copies", "-c", type=int, default=1, help="Anzahl der Kopien")
        parser.add_argument("--simplex", action="store_true", help="Einseitig drucken (Standard ist Duplex)")
        parser.add_argument("--gui", "-g", action="store_true", help="GUI mit den übergebenen Dateien öffnen")

        args = parser.parse_args()

        if args.gui or not args.inputs:
            from gui import main as start_gui, HAS_DND
            import tkinter as tk
            if HAS_DND:
                from tkinterdnd2 import TkinterDnD
                root = TkinterDnD.Tk()
            else:
                root = tk.Tk()
            from gui import VSCtoPDFApp
            app = VSCtoPDFApp(root)
            if args.inputs:
                app.add_paths(args.inputs)
            if args.word:
                app.footer_entry.delete(0, tk.END)
                app.footer_entry.insert(0, args.word)
            root.mainloop()
        else:
            run_cli(args)
    else:
        # Standard: GUI starten
        from gui import main as start_gui
        start_gui()


if __name__ == "__main__":
    main()
