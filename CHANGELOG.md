# Changelog - VSCtoPDF

Alle relevanten Änderungen und Neuerungen dieses Projekts werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/)
und dieses Projekt folgt der [semantischen Versionierung](https://semver.org/lang/de/).

---

## [1.1.0] - 2026-11-11

### Hinzugefügt
- **Reine SVG-Vektoricons:** Alle Oberflächen-Icons wurden durch moderne, skalierbare SVG-Dateien (`assets/icons/`) ersetzt. Bietet gestochen scharfe Darstellung auf allen Apple Retina-Displays.
- **Native macOS-Installation:**
  - Eigenständiges macOS Application-Bundle (`VSCtoPDF.app`) mit hochauflösendem App-Icon (`AppIcon.icns`).
  - Apple Disk Image (`dist/VSCtoPDF.dmg`) für einfache Drag & Drop Installation nach `/Applications`.
  - Automatisches Installationsskript (`install.sh`) zur Einbettung in macOS Spotlight, Launchpad und Programme-Ordner.
  - Reproduzierbares Build-Skript (`build_app.sh`).
- **Integrierter Info- & Changelog-Dialog:**
  - Neuer Button und Menüeintrag im Programm zum Anzeigen der aktuellen Version, Lizenzhinweise und des vollständigen Changelogs direkt in der Benutzeroberfläche.
- **PySide6 UI Engine:**
  - Umstellung auf PySide6 (Qt6) für echte native Cocoa-Optik, Dark-/Light-Mode und flüssige Hintergrund-Threads ohne UI-Lags.

---

## [1.0.0] - 2026-11-11

### Hinzugefügt
- Initialer Release von VSCtoPDF.
- Konvertierung von Quellcodedateien (`.py`, `.html`, `.css`, `.js`, `.ts`, `.json`, `.sql`, etc.) in DIN-A4 PDF.
- Exakte DIN-A4 Seitenbreite mit Zeilennummern, Syntax-Highlighting und automatischem Zeilenumbruch.
- Kopfzeile mit automatischem Ordner-Pfad und Dateinamen.
- Fußzeile mit frei definierbarem Benutzerwort (links) und Seitennummerierung `Seite X/Y` (rechts).
- Automatisches Speichern im jeweiligen Originalordner der Datei als `<Dateiname>.pdf`.
- Integrierte macOS CUPS-Druckersteuerung mit automatischer Druckererkennung, Duplex-Option und Kopienanzahl.
- Datei- und Ordnerauswahl inklusive Drag & Drop aus dem macOS Finder.
- Interaktive Tabelle mit Checkboxen zum selektiven Auswählen und Abwählen vor dem Drucken.
- Lizenzierung unter Creative Commons CC BY-NC 4.0.
