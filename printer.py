"""
printer.py - macOS CUPS-Druckersteuerung, Druckererkennung und Systemintegration.
"""

import subprocess
import shutil
import re
import os
from typing import List, Tuple, Optional


def get_installed_printers() -> Tuple[List[str], Optional[str]]:
    """
    Ermittelt die auf dem Mac installierten Drucker und den Standarddrucker.
    Gibt (drucker_liste, standard_drucker) zurück.
    """
    printers = []
    default_printer = None

    if not shutil.which("lpstat"):
        return printers, default_printer

    # 1. Standard-Drucker abfragen
    try:
        res_d = subprocess.run(
            ["lpstat", "-d"], capture_output=True, text=True, check=False, timeout=5
        )
        # Typischer Output:
        # "system default destination: Brother_MFC_J5730DW"
        # oder auf Deutsch:
        # "System-Standardzielort: Brother_MFC_J5730DW"
        match = re.search(r":\s*([^\s]+)", res_d.stdout)
        if match:
            default_printer = match.group(1).strip()
    except Exception:
        pass

    # 2. Alle konfigurierten Drucker abfragen
    try:
        res_p = subprocess.run(
            ["lpstat", "-p"], capture_output=True, text=True, check=False, timeout=5
        )
        for line in res_p.stdout.splitlines():
            # Englisch: "printer Brother_MFC_J5730DW is idle..."
            # Deutsch: "Drucker „Brother_MFC_J5730DW“ ist inaktiv..."
            match = re.search(r"(?:printer|Drucker)\s+[„\"]?([^“\"\s]+)", line)
            if match:
                p_name = match.group(1)
                if p_name not in printers:
                    printers.append(p_name)
    except Exception:
        pass

    # Falls der Standarddrucker nicht in der Liste gefunden wurde, hinzufügen
    if default_printer and default_printer not in printers:
        printers.insert(0, default_printer)

    return printers, default_printer


def print_pdf(
    pdf_path: str,
    printer_name: Optional[str] = None,
    copies: int = 1,
    duplex: bool = True
) -> Tuple[bool, str]:
    """
    Sendet eine PDF-Datei an den ausgewählten oder Standard-Drucker über `lp`.

    :param pdf_path: Vollständiger Pfad zur PDF-Datei
    :param printer_name: Name des Ziel-Druckers (oder None für Standarddrucker)
    :param copies: Anzahl der Kopien (Standard: 1)
    :param duplex: Beidseitig (Duplex) drucken (Standard: True)
    :return: (erfolgreich: bool, nachricht: str)
    """
    if not os.path.exists(pdf_path):
        return False, f"Datei existiert nicht: {pdf_path}"

    if not shutil.which("lp"):
        return False, "Das Druckprogramm 'lp' ist auf diesem System nicht verfügbar."

    cmd = ["lp"]

    if printer_name and printer_name != "Standarddrucker":
        cmd.extend(["-d", printer_name])

    if copies > 1:
        cmd.extend(["-n", str(copies)])

    if duplex:
        cmd.extend(["-o", "sides=two-sided-long-edge"])
    else:
        cmd.extend(["-o", "sides=one-sided"])

    job_title = os.path.basename(pdf_path)
    cmd.extend(["-t", job_title])
    cmd.append(pdf_path)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=15
        )
        if result.returncode == 0:
            out = result.stdout.strip()
            return True, out if out else f"Druckauftrag für {job_title} erfolgreich übermittelt."
        else:
            err = result.stderr.strip() or result.stdout.strip()
            return False, f"Druckfehler (Code {result.returncode}): {err}"
    except Exception as e:
        return False, f"Fehler beim Ausführen von lp: {e}"


def open_in_preview(pdf_path: str) -> Tuple[bool, str]:
    """Öffnet die PDF-Datei in der macOS Vorschau (Preview.app)."""
    if not os.path.exists(pdf_path):
        return False, f"Datei nicht gefunden: {pdf_path}"
    try:
        subprocess.run(["open", "-a", "Preview", pdf_path], check=False)
        return True, "In Vorschau geöffnet."
    except Exception as e:
        return False, f"Konnte Vorschau nicht öffnen: {e}"


def reveal_in_finder(pdf_path: str) -> Tuple[bool, str]:
    """Zeigt die Datei im macOS Finder an."""
    if not os.path.exists(pdf_path):
        return False, f"Datei nicht gefunden: {pdf_path}"
    try:
        subprocess.run(["open", "-R", pdf_path], check=False)
        return True, "Im Finder angezeigt."
    except Exception as e:
        return False, f"Konnte Finder nicht öffnen: {e}"
