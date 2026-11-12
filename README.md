# VSCtoPDF – Code zu DIN-A4 PDF Konverter & Direktdruck für macOS

**VSCtoPDF** ist eine native macOS-Anwendung (mit modernem PySide6-Interface und gestochen scharfen SVG-Vektoricons), mit der Sie einzelne Quellcodedateien (`.html`, `.css`, `.py`, `.js`, `.ts`, `.json`, etc.) oder ganze Projektordner per Drag & Drop oder Dateidialog einfügen, automatisch als formatierte DIN-A4 PDF-Dokumente exportieren und anschließend selektiv über die installierten Mac-Drucker ausdrucken können.

---

## 🌟 Highlights & Funktionen

- **Native macOS App & Installation:**
  Kann als echte macOS-App direkt nach `/Applications` (Programme) installiert werden. Startet aus Spotlight, Launchpad und dem Finder ohne Terminal.
- **Reine SVG-Vektoricons:**
  Alle Icons der Benutzeroberfläche sind moderne, skalierbare SVG-Dateien (`assets/icons/`), die auch auf Retina-Displays gestochen scharf dargestellt werden.
- **Interaktive Tabellen-Spalten & Vollständige Pfadanzeige:**
  Spaltenbreiten lassen sich stufenlos mit der Maus anpassen. Dateipfade und PDF-Pfade werden mit Tooltip und Kontextmenü vollständig bereitgestellt.
- **Integrierte Menüführung & Versionsverwaltung:**
  Über das Menü (`v1.1.1 ▾`) in der Kopfzeile können Versionsdetails, Changelog, GitHub-Repository und Releases direkt aufgerufen werden.
- **DIN-A4 Format mit Zeilennummern & Syntax-Highlighting:**
  Jede Datei wird exakt auf DIN-A4 Seitenbreite formatiert. Lange Codezeilen brechen automatisch und sauber um. Zeilennummern und Syntax-Hervorhebung sorgen für perfekte Lesbarkeit auf Papier.
- **Kopfzeile (Header):**
  Enthält immer den vollständigen **Ordner-Pfad** der jeweiligen Datei sowie den Dateinamen.
- **Fußzeile (Footer):**
  - **Links:** Ein vom Benutzer frei definierbares Wort / Projektbezeichnung (z. B. `Vertraulich`, `Projekt X`, `Schulungsunterlage`).
  - **Rechts:** Exakte Seitennummerierung im Format **`Seite X/Gesamte Seiten`** (z. B. `Seite 1/3`).
- **Speicherort:**
  Die erzeugten PDF-Dateien werden automatisch **im selben Ordner** wie die jeweilige Originaldatei gespeichert (`dateiname.ext.pdf`).
- **Direktdruck auf dem Mac:**
  - Automatische Erkennung aller auf dem Mac installierten Drucker (CUPS) inklusive Standarddrucker.
  - Interaktive Tabelle mit Checkboxen: Wählen Sie genau die Dateien aus oder ab, die Sie drucken möchten.
  - Buttons für „Alle auswählen“, „Auswahl aufheben“, „In Vorschau öffnen“ und „Im Finder zeigen“.
  - Unterstützung für beidseitigen Druck (**Duplex**) und Angabe der Kopienanzahl.
- **Drag & Drop:**
  Dateien oder ganze Ordner können direkt aus dem Finder in das Fenster gezogen werden.

---

## 📦 Native Installation auf dem Mac

### Option 1: Automatischer Installer (Empfohlen)
Führen Sie im Projektverzeichnis einfach den Installer aus:
```bash
./install.sh
```
Dies kopiert `VSCtoPDF.app` direkt in Ihren Programme-Ordner (`/Applications`). Danach ist das Programm sofort in **Spotlight**, **Launchpad** und im **Dock** verfügbar.

### Option 2: Über das Apple Disk Image (.dmg)
Öffnen Sie die erstellte Datei:
> **`dist/VSCtoPDF.dmg`**

Ziehen Sie das `VSCtoPDF`-Symbol einfach auf den Ordner `Applications`.

### Option 3: Eigenständiges App-Bundle
Sie können `dist/VSCtoPDF.app` auch direkt per Doppelklick starten.

### Option 4: Aus Quellcode / Entwicklungsmodus
```bash
# Per Doppelklick:
start.command

# Oder im Terminal:
.venv/bin/python main.py
```

---

## 🖥️ Bedienung der Benutzeroberfläche

1. **Einstellungen festlegen:**
   - **Fußzeile (links):** Geben Sie das gewünschte Wort oder die Bezeichnung ein.
   - **Drucker:** Wählen Sie den gewünschten Drucker aus der Dropdown-Liste (der Mac-Standarddrucker ist vorausgewählt).
   - **Duplex / Kopien:** Wählen Sie, ob beidseitig gedruckt werden soll und wie viele Kopien benötigt werden.
   - **Farbschema:** Wählen Sie ein Syntax-Farbschema (z. B. `friendly` für augenfreundlichen Druck auf weißem Papier oder `bw` für Schwarz-Weiß).
2. **Dateien oder Ordner hinzufügen:**
   - Ziehen Sie Dateien oder Ordner einfach per **Drag & Drop** in die Tabelle.
   - Alternativ klicken Sie auf **`Dateien hinzufügen...`** oder **`Ordner hinzufügen...`**.
3. **Konvertieren:**
   - Klicken Sie auf **`Alle Dateien als DIN-A4 PDF konvertieren`**.
   - Die PDFs werden im jeweiligen Originalordner erstellt und die Seitenzahlen ermittelt.
4. **Auswählen & Drucken:**
   - In der ersten Spalte (`Drucken`) können Sie einzelne Dateien per Klick an- oder abwählen.
   - Nutzen Sie **`Alle auswählen`** oder **`Auswahl aufheben`**.
   - Klicken Sie auf **`Ausgewählte PDFs drucken`**, um die gewählten Dokumente direkt an den Drucker zu senden.
   - Vorabkontrolle: Doppelklick auf eine Zeile oder **`In Vorschau öffnen`** öffnet das PDF in der macOS Vorschau.

---

## ⌨️ CLI-Modus (Kommandozeile)

Das Programm kann auch ohne grafische Oberfläche in Terminal-Skripten verwendet werden:

```bash
# Einzelne Datei konvertieren
./dist/VSCtoPDF.app/Contents/MacOS/VSCtoPDF script.py --word "MeinProjekt"

# Ganzen Ordner konvertieren und direkt drucken
./dist/VSCtoPDF.app/Contents/MacOS/VSCtoPDF /pfad/zum/ordner --word "Vertraulich" --print

# Auf einem bestimmten Drucker mit 2 Kopien drucken
./dist/VSCtoPDF.app/Contents/MacOS/VSCtoPDF mein_ordner --print --printer "Brother_MFC_J5730DW" --copies 2
```

---

## 📁 Projektstruktur

```
VSCtoPDF/
├── main.py              # Hauptprogramm (PySide6 GUI & CLI Starter)
├── gui.py               # Native macOS GUI mit SVG-Icons & Drag & Drop
├── converter.py         # PDF-Engine (ReportLab, Pygments, A4, Kopf- & Fußzeile)
├── printer.py           # macOS Druckanbindung (CUPS, lpstat, lp)
├── version.py           # Versionsangaben & Changelog-Daten
├── CHANGELOG.md         # Ausführliche Versionshistorie
├── start.command        # Doppelklick-Starter für Entwickler
├── install.sh           # Nativer macOS-Installer nach /Applications
├── build_app.sh         # Erstellt .app Bundle und .dmg Disk Image
├── requirements.txt     # Python-Abhängigkeiten
├── LICENSE              # CC BY-NC 4.0 Lizenz
├── assets/              # Native Ressourcen
│   ├── AppIcon.icns     # Multi-Resolution Retina App-Icon
│   └── icons/           # Alle Icons im reinen SVG-Format (100% vektorisiert)
│       ├── app_icon.svg
│       ├── add_files.svg
│       ├── add_folder.svg
│       ├── delete.svg
│       ├── clear.svg
│       ├── convert.svg
│       ├── print.svg
│       ├── preview.svg
│       ├── finder.svg
│       ├── refresh.svg
│       ├── select_all.svg
│       ├── deselect_all.svg
│       ├── file_code.svg
│       ├── menu.svg
│       ├── github.svg
│       ├── changelog.svg
│       ├── info.svg
│       ├── lightbulb.svg
│       ├── copy.svg
│       └── download.svg
└── examples/            # Beispielprojekt zum Testen
    └── demo_project/
        ├── index.html
        ├── style.css
        └── app.py
```

---

## 📄 Lizenz

Dieses Projekt ist unter der **Creative Commons Namensnennung - Nicht-kommerziell 4.0 International Lizenz (CC BY-NC 4.0)** lizenziert.
- **Erlaubt:** Kopieren, Weiterverbreiten, Verändern und Anpassen.
- **Bedingungen:** Nennung des Autors (Attribution) und ausschließlich nicht-kommerzielle Nutzung.
Details finden sich in der [LICENSE](LICENSE) Datei.
