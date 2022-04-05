from sqlalchemy import create_engine
from pathlib import Path

class LocalStore:
    """A wrapper around the user's local mixxxdb."""

    def __init__(self, path: Path):
        self.engine = create_engine(f'sqlite:///{path}')
