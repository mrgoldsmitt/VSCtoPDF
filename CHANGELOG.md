# Changelog - VSCtoPDF

Alle relevanten Änderungen und Neuerungen dieses Projekts werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/)
und dieses Projekt folgt der [semantischen Versionierung](https://semver.org/lang/de/).

---

## [1.1.3] - 2026-11-12

### Verbessert & Optimiert
- **macOS System-Menüleiste:** Menü für Version, Changelog und GitHub vollständig in die native macOS-Menüleiste am oberen Bildschirmrand integriert (mit Standard-Menüs *Ablage*, *Bearbeiten* und *Hilfe* sowie Tastatur-Shortcuts wie Cmd+O, Cmd+P, Cmd+A, Cmd+W) – der Menü-Button im Fenster wurde entfernt.
- **Hinweistext ohne Button-Optik:** Der Hinweis *„x von y Dateien zum Drucken“* wird als reiner Text in weißer Schrift ohne Button-Hintergrund dargestellt.
- **Button-Umbenennung:** Der Button *„Ausgewählte PDFs drucken“* wurde in *„PDFs drucken“* umbenannt.

---

## [1.1.2] - 2026-11-12

### Hinzugefügt & Verbessert
- **Neue Tabellenspalte 'Ordner-Name':** Zeigt den Namen des übergeordneten Ordners (z. B. `demo_project`) direkt und übersichtlich als eigene Spalte neben Dateiname und Dateityp an.
- **Erweitertes Kontextmenü:** Neue Schnellaktion *„Ordner-Name kopieren“* (zusätzlich zu *„Ordner-Pfad kopieren“* und *„PDF-Pfad kopieren“*).
- **Neues SVG-Icon:** Reines Vektorsymbol `folder.svg` für Verzeichnisse in der Tabelle.

---

## [1.1.1] - 2026-11-12

### Verbessert & Hinzugefügt
- **Manuelle Spaltenbreiten-Anpassung:** Alle Spalten der Dateitabelle können nun mit der Maus stufenlos in der Breite angepasst werden (`QHeaderView.Interactive`).
- **Neues Dropdown-Menü:** Version, Changelog und GitHub-Links sind in einem kompakten Menü-Button (`Menü ▾`) direkt erreichbar.
- **Vollständige Anzeige der Ordner-Pfade:**
  - In der Tabelle durch frei erweiterbare Spaltenbreite, vollständige Tooltips beim Überfahren mit der Maus sowie neue Aktionen im Kontextmenü zum Kopieren von Ordner- und PDF-Pfaden.
  - Im PDF-Header durch dynamische Schriftgrößenanpassung und automatischen Zweizeilen-Umbruch (kein Abschneiden mit `...` mehr).
- **Vollständige SVG-Konvertierung:** Alle verbleibenden Emojis wurden durch native Vektor-SVGs (`menu.svg`, `github.svg`, `changelog.svg`, `copy.svg`, `lightbulb.svg`, `download.svg`) ersetzt.
- **Optimierte Button-Beschriftung:** Druck-Button-Schriftgröße verkleinert (`font-size: 11px`), damit der Text auf allen Bildschirmgrößen sauber Platz findet.
- **Weißer Auswahl-Hinweis:** Der Zähler 'x Dateien zum Drucken ausgewählt' ist nun in kontraststarkem Weiß (`#ffffff`) auf einem dezenten Status-Badge formatiert.

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
