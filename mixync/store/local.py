from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from mixync.model.library import *
from mixync.model.track_locations import *

class LocalStore:
    """A wrapper around the user's local mixxxdb."""

    def __init__(self, path: Path):
        engine = create_engine(f'sqlite:///{path}')
        self.session = sessionmaker(bind=engine)
