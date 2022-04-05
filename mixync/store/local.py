import sqlite3

from pathlib import Path

class LocalStore:
    """A wrapper around the user's local mixxxdb."""

    def __init__(self, path: Path):
        self.connection = sqlite3.connect(path)
