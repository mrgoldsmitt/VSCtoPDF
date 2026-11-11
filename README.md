# VSCtoPDF – Code zu DIN-A4 PDF Konverter & Direktdruck für macOS

**VSCtoPDF** ist eine maßgeschneiderte macOS-Anwendung, mit der Sie einzelne Quellcodedateien (`.html`, `.css`, `.py`, `.js`, `.ts`, `.json`, etc.) oder ganze Projektordner per Drag & Drop oder Dateidialog einfügen, automatisch als formatierte DIN-A4 PDF-Dokumente exportieren und anschließend selektiv über die installierten Mac-Drucker ausdrucken können.

---

## 🌟 Highlights & Funktionen

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
  - Interaktive Tabelle mit Checkboxen (`☑` / `☐`): Wählen Sie genau die Dateien aus oder ab, die Sie drucken möchten.
  - Buttons für „Alle auswählen“, „Auswahl aufheben“, „In Vorschau öffnen“ und „Im Finder zeigen“.
  - Unterstützung für beidseitigen Druck (**Duplex**) und Angabe der Kopienanzahl.
- **Drag & Drop:**
  Dateien oder ganze Ordner können direkt aus dem Finder in das Fenster gezogen werden.

---

## 🚀 Schnellstart

### Methode 1: Per Doppelklick (Empfohlen)
Doppelklicken Sie im Finder einfach auf:
```bash
start.command
```
*Tipp:* Das Skript initialisiert beim ersten Start automatisch die virtuelle Umgebung (`.venv`) und startet direkt die grafische Oberfläche.

### Methode 2: Über das Terminal
```bash
# In das Projektverzeichnis wechseln
cd /Users/mrgoldsmitt/Projekte/VSCtoPDF

# Programm starten
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
   - Alternativ klicken Sie auf **`📄 Dateien hinzufügen...`** oder **`📁 Ordner hinzufügen...`**.
3. **Konvertieren:**
   - Klicken Sie auf den Button **`🚀 Alle Dateien als DIN-A4 PDF konvertieren`**.
   - Die PDFs werden im jeweiligen Originalordner erstellt und die Seitenzahlen ermittelt.
4. **Auswählen & Drucken:**
   - In der ersten Spalte (`Drucken`) können Sie einzelne Dateien per Mausklick oder `Leertaste` an- oder abwählen (`☑` / `☐`).
   - Nutzen Sie **`☑ Alle auswählen`** oder **`☐ Auswahl aufheben`**.
   - Klicken Sie auf **`🖨️ Ausgewählte PDFs drucken`**, um die gewählten Dokumente direkt an den Drucker zu senden.
   - Vorabkontrolle: Doppelklick auf eine Zeile oder **`👁 In Vorschau öffnen`** öffnet das PDF in der macOS Vorschau.

---

## ⌨️ CLI-Modus (Kommandozeile)

Das Programm kann auch ohne grafische Oberfläche in Terminal-Skripten verwendet werden:

```bash
# Einzelne Datei konvertieren
.venv/bin/python main.py script.py --word "MeinProjekt"

# Ganzen Ordner konvertieren und direkt drucken
.venv/bin/python main.py /pfad/zum/ordner --word "Vertraulich" --print

# Auf einem bestimmten Drucker mit 2 Kopien drucken
.venv/bin/python main.py mein_ordner --print --printer "Brother_MFC_J5730DW" --copies 2
```

### CLI-Optionen
- `inputs`: Beliebig viele Dateien oder Ordner
- `-w, --word`: Text für die linke Fußzeile
- `-s, --style`: Syntax-Farbschema (`friendly`, `default`, `colorful`, `bw`)
- `-p, --print`: Direkt nach der Konvertierung drucken
- `--printer`: Ziel-Drucker (Standard: System-Standarddrucker)
- `-c, --copies`: Anzahl der Exemplare
- `--simplex`: Einseitig drucken (Standard ist beidseitig Duplex)
- `-g, --gui`: Startet die Benutzeroberfläche mit den angegebenen Pfaden

---

## 📁 Projektstruktur

```
VSCtoPDF/
├── main.py              # Hauptprogramm (GUI & CLI Starter)
├── gui.py               # Grafische Benutzeroberfläche (Tkinter & Drag&Drop)
├── converter.py         # PDF-Engine (ReportLab, Pygments, A4, Kopf- & Fußzeile)
├── printer.py           # macOS Druckanbindung (CUPS, lpstat, lp)
├── start.command        # Doppelklick-Starter für den macOS Finder
├── requirements.txt     # Python-Abhängigkeiten
├── LICENSE              # CC BY-NC 4.0 Lizenz
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
