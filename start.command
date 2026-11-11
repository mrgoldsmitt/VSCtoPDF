#!/bin/bash
# ==============================================================================
# VSCtoPDF Starter für macOS
# Doppelklick startet das Programm direkt im Finder.
# ==============================================================================

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Prüfen, ob .venv existiert, andernfalls automatisch anlegen
if [ ! -f ".venv/bin/python" ]; then
    echo "Initialisiere Python-Umgebung..."
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi

exec .venv/bin/python main.py "$@"
