#!/usr/bin/env python3
"""
Beispielanwendung für VSCtoPDF Demo.
"""

from typing import List, Dict


class ReportGenerator:
    """Erstellt Zusammenfassungen von Projektdaten."""

    def __init__(self, title: str):
        self.title = title
        self.entries: List[Dict[str, str]] = []

    def add_entry(self, key: str, value: str) -> None:
        """Fügt einen neuen Eintrag hinzu."""
        self.entries.append({"key": key, "value": value})

    def render(self) -> str:
        """Gibt den formatierten Bericht aus."""
        lines = [f"=== {self.title} ==="]
        for item in self.entries:
            lines.append(f" - {item['key']}: {item['value']}")
        return "\n".join(lines)


if __name__ == "__main__":
    rep = ReportGenerator("Demo Bericht")
    rep.add_entry("Projekt", "VSCtoPDF")
    rep.add_entry("Status", "Erfolgreich erstellt")
    print(rep.render())
