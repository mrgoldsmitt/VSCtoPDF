#!/bin/bash
# ==============================================================================
# VSCtoPDF - Build-Skript für macOS (.app Bundle und .dmg Installer)
# ==============================================================================

set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

VERSION="1.1.3"
APP_NAME="VSCtoPDF"

echo "🔨 [1/4] Virtuelle Python-Umgebung prüfen..."
if [ ! -f ".venv/bin/python" ]; then
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi

echo "🎨 [2/4] App-Icon (ICNS) aus SVG erzeugen..."
.venv/bin/python -c "
import os, subprocess
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication
import sys

app = QApplication.instance() or QApplication(sys.argv)
icon_dir = 'assets/AppIcon.iconset'
os.makedirs(icon_dir, exist_ok=True)
renderer = QSvgRenderer('assets/icons/app_icon.svg')

sizes = [
    (16, 'icon_16x16.png'), (32, 'icon_16x16@2x.png'),
    (32, 'icon_32x32.png'), (64, 'icon_32x32@2x.png'),
    (128, 'icon_128x128.png'), (256, 'icon_128x128@2x.png'),
    (256, 'icon_256x256.png'), (512, 'icon_256x256@2x.png'),
    (512, 'icon_512x512.png'), (1024, 'icon_512x512@2x.png')
]
for sz, fname in sizes:
    img = QImage(sz, sz, QImage.Format_ARGB32)
    img.fill(0)
    p = QPainter(img)
    renderer.render(p)
    p.end()
    img.save(os.path.join(icon_dir, fname))

subprocess.run(['iconutil', '-c', 'icns', icon_dir, '-o', 'assets/AppIcon.icns'], check=True)
import shutil
shutil.rmtree(icon_dir, ignore_errors=True)
"

echo "🚀 [3/4] Kompiliere VSCtoPDF.app v$VERSION mit PyInstaller..."
.venv/bin/pyinstaller --noconfirm --windowed \
    --name "$APP_NAME" \
    --icon "assets/AppIcon.icns" \
    --osx-bundle-identifier "com.mrgoldsmitt.vsctopdf" \
    --add-data "assets:assets" \
    main.py

# Info.plist Metadaten verfeinern
PLIST="dist/$APP_NAME.app/Contents/Info.plist"
if [ -f "$PLIST" ]; then
    plutil -replace CFBundleShortVersionString -string "$VERSION" "$PLIST"
    plutil -replace CFBundleVersion -string "$VERSION" "$PLIST"
    plutil -replace CFBundleDisplayName -string "$APP_NAME" "$PLIST"
    plutil -replace NSHumanReadableCopyright -string "Copyright © 2026 Sebastian (mrgoldsmitt). CC BY-NC 4.0" "$PLIST"
fi

echo "💿 [4/4] Erstelle VSCtoPDF.dmg Disk Image..."
mkdir -p dist/dmg_staging
cp -R "dist/$APP_NAME.app" dist/dmg_staging/
ln -s /Applications dist/dmg_staging/Applications
hdiutil create -volname "$APP_NAME v$VERSION" -srcfolder dist/dmg_staging -ov -format UDZO "dist/$APP_NAME.dmg"
rm -rf dist/dmg_staging

echo ""
echo "✅ Build v$VERSION erfolgreich fertiggestellt!"
echo "   - App-Bundle:  dist/$APP_NAME.app"
echo "   - Installer:   dist/$APP_NAME.dmg"
echo "   - Installation: Führen Sie ./install.sh aus"
