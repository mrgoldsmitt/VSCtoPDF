"""
version.py - Versionsinformationen und Metadaten für VSCtoPDF.
"""

APP_NAME = "VSCtoPDF"
APP_VERSION = "1.1.2"
APP_RELEASE_DATE = "12.11.2026"
APP_AUTHOR = "Sebastian (mrgoldsmitt)"
APP_LICENSE = "Creative Commons CC BY-NC 4.0"
APP_GITHUB = "https://github.com/mrgoldsmitt/VSCtoPDF"
APP_DESCRIPTION = "Natives macOS-Tool zum Konvertieren von Code-Dateien in DIN-A4 PDF mit Kopf-/Fußzeile & Direktdruck."

CHANGELOG_TEXT = """## [1.1.2] - 2026-11-12
### Hinzugefügt & Verbessert
- **Neue Tabellenspalte 'Ordner-Name':** Zeigt den Namen des übergeordneten Ordners (z. B. 'demo_project') direkt und übersichtlich als eigene Spalte neben Dateiname und Dateityp an.
- **Erweitertes Kontextmenü:** Neue Schnellaktion 'Ordner-Name kopieren' (zusätzlich zu 'Ordner-Pfad kopieren' und 'PDF-Pfad kopieren').
- **Neues SVG-Icon:** Reines Vektorsymbol `folder.svg` für Verzeichnisse in der Tabelle.

## [1.1.1] - 2026-11-12
### Verbessert & Hinzugefügt
- **Manuelle Spaltenbreiten-Anpassung:** Alle Spalten der Dateitabelle können nun frei mit der Maus vergrößert oder verkleinert werden (`QHeaderView.Interactive`).
- **Neues Dropdown-Menü:** Version, Changelog und direkte GitHub-Links sind in einem kompakten Menü-Button (`Menü ▾`) direkt erreichbar.
- **Vollständige Anzeige der Ordner-Pfade:**
  - In der Tabelle durch anpassbare Spaltenbreite und erweiterte Tooltips sowie 'Pfad kopieren'-Aktion.
  - Im PDF-Header durch dynamische Schriftanpassung und automatischen Zweizeilen-Umbruch ohne Abschneiden.
- **Vollständige SVG-Konvertierung:** Alle verbleibenden Emojis wurden durch native Vektor-SVGs (`menu.svg`, `github.svg`, `changelog.svg`, `copy.svg`, `lightbulb.svg`, `download.svg`) ersetzt.
- **Optimierte Button-Beschriftung:** Druck-Button-Schriftgröße verkleinert (`font-size: 11px`), damit der Text auf allen Bildschirmgrößen sauber Platz findet.
- **Weißer Auswahl-Hinweis:** Der Zähler 'x Dateien zum Drucken ausgewählt' ist nun in kontraststarkem Weiß (`#ffffff`) auf einem dezenten Status-Badge formatiert.

## [1.1.0] - 2026-11-11
### Hinzugefügt
- **Reine SVG-Vektoricons:** Alle Oberflächen-Icons durch moderne, skalierbare SVG-Dateien ersetzt (optimiert für Retina-Displays).
- **Native macOS-Installation:**
  - Eigenständiges macOS Application-Bundle (VSCtoPDF.app) mit hochauflösendem AppIcon.icns.
  - Apple Disk Image (.dmg) Installer mit Drag & Drop Shortcut nach /Applications.
  - Automatisches Installationsskript (install.sh).
  - Ein-Klick Build-Skript (build_app.sh).
- **Integrierter Versions- & Changelog-Dialog:**
  - Anzeige von Version, Autor, Lizenz und vollständiger Versionshistorie direkt in der App.
- **PySide6 Native Engine:**
  - Hardwarebeschleunigtes Qt6-Interface mit nativer macOS-Systemintegration, Dark-/Light-Mode und flüssigem Multithreading.

## [1.0.0] - 2026-11-11
### Hinzugefügt
- Initialer Release von VSCtoPDF.
- Konvertierung von Quellcodedateien (.py, .html, .css, .js, .ts, .json, .c, .cpp, .java, etc.) in DIN-A4 PDF.
- Exakte DIN-A4 Seitenbreite mit Zeilennummern, Syntax-Highlighting und automatischem Zeilenumbruch.
- Kopfzeile mit automatischem Ordner-Pfad und Dateinamen.
- Fußzeile mit frei definierbarem Benutzerwort (links) und Seitennummerierung 'Seite X/Y' (rechts).
- Automatisches Speichern im jeweiligen Originalordner der Datei als '<Dateiname>.pdf'.
- Integrierte macOS CUPS-Druckersteuerung mit automatischer Druckererkennung, Duplex-Option und Kopienanzahl.
- Datei- und Ordnerauswahl inklusive Drag & Drop aus dem macOS Finder.
- Interaktive Tabelle mit Checkboxen zum selektiven Auswählen und Abwählen vor dem Drucken.
- Lizenzierung unter Creative Commons CC BY-NC 4.0.
"""
