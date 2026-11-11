#!/bin/bash
# ==============================================================================
# VSCtoPDF - Nativer macOS Installer
# Installiert VSCtoPDF.app direkt in /Applications (oder ~/Applications)
# ==============================================================================

set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo "=========================================================="
echo "      VSCtoPDF - Nativer macOS Installer                  "
echo "=========================================================="

APP_SRC="$DIR/dist/VSCtoPDF.app"
TARGET_DIR="/Applications"

# Prüfen, ob das .app-Paket existiert. Falls nicht, zuerst bauen.
if [ ! -d "$APP_SRC" ]; then
    echo "⚠️  VSCtoPDF.app noch nicht gebaut. Starte Build-Prozess..."
    ./build_app.sh
fi

echo "📦 Installiere VSCtoPDF nach $TARGET_DIR/VSCtoPDF.app ..."

# Falls Schreibrechte in /Applications fehlen, nach ~/Applications ausweichen
if [ ! -w "$TARGET_DIR" ]; then
    if sudo -v 2>/dev/null; then
        echo "🔐 Kopiere mit Administrator-Rechten nach /Applications..."
        sudo rm -rf "$TARGET_DIR/VSCtoPDF.app"
        sudo cp -R "$APP_SRC" "$TARGET_DIR/"
        sudo xattr -cr "$TARGET_DIR/VSCtoPDF.app" 2>/dev/null || true
    else
        TARGET_DIR="$HOME/Applications"
        mkdir -p "$TARGET_DIR"
        echo "ℹ️  Installiere in Benutzer-Programme: $TARGET_DIR ..."
        rm -rf "$TARGET_DIR/VSCtoPDF.app"
        cp -R "$APP_SRC" "$TARGET_DIR/"
        xattr -cr "$TARGET_DIR/VSCtoPDF.app" 2>/dev/null || true
    fi
else
    rm -rf "$TARGET_DIR/VSCtoPDF.app"
    cp -R "$APP_SRC" "$TARGET_DIR/"
    xattr -cr "$TARGET_DIR/VSCtoPDF.app" 2>/dev/null || true
fi

echo "✅ Installation erfolgreich abgeschlossen!"
echo "   Sie finden 'VSCtoPDF' ab sofort im Launchpad, in Spotlight (Cmd+Leertaste) und im Programme-Ordner."
echo ""
if [ -t 0 ]; then
    read -t 10 -p "Möchten Sie VSCtoPDF jetzt starten? (J/n): " -n 1 -r || true
    echo ""
    if [[ $REPLY =~ ^[JjYy]$ ]] || [[ -z $REPLY ]]; then
        open "$TARGET_DIR/VSCtoPDF.app"
    fi
fi
