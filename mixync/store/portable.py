from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, make_transient
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
        self.make_session = sessionmaker(bind=self.engine)

        self._create_tables()
    
    def _create_tables(self):
        Base.metadata.create_all(self.engine, checkfirst=True)
    
    def _query_all(self, *args, **kwargs) -> list:
        with self.make_session() as session:
            for row in session.query(*args, **kwargs):
                make_transient(row)
                row.id = None
                yield row
    
    def tracks(self) -> list[Track]:
        return list(self._query_all(Track))
    
    def track_locations(self) -> list[TrackLocation]:
        return list(self._query_all(TrackLocation))
