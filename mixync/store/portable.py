from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from mixync.model import Base
from mixync.model.track import *
from mixync.model.track_location import *
from mixync.store import Store

class PortableStore(Store):
    """A wrapper around the portable mixxxlib."""

    def __init__(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)

        db_path = path / 'mixxxdb.portable.sqlite'
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.session = sessionmaker(bind=self.engine)

        self.create_tables()
    
    def create_tables(self):
        Base.metadata.create_all(self.engine, checkfirst=True)
