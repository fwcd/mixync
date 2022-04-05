from sqlalchemy import create_engine, select
from pathlib import Path

from mixync.model.library import *
from mixync.model.track_locations import *

class LocalStore:
    """A wrapper around the user's local mixxxdb."""

    def __init__(self, path: Path):
        engine = create_engine(f'sqlite:///{path}')
        self.connection = engine.connect()

        # DEBUG
        for row in self.connection.execute(select(Library)):
            print(row)
