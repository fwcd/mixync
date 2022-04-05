import sqlite3

from pathlib import Path

class PortableStore:
    """A wrapper around the portable mixxxlib."""

    def __init__(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)

        db_path = path / 'mixxxdb.portable.sqlite3'
        self.connection = sqlite3.connect(db_path)
