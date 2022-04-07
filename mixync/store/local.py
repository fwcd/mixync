from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, make_transient
from pathlib import Path

from mixync.model.track import *
from mixync.model.track_location import *
from mixync.store import Store

class LocalStore(Store):
    """A wrapper around the user's local mixxxdb."""

    def __init__(self, path: Path):
        engine = create_engine(f'sqlite:///{path}')
        self.make_session = sessionmaker(bind=engine)
    
    def _query_all(self, *args, **kwargs) -> list:
        with self.make_session() as session:
            for row in session.query(*args, **kwargs):
                make_transient(row)
                row.id = None
                yield row
    
    def tracks(self) -> list[Track]:
        return list(self._query_all(Track))
    
    # TODO: Relativize paths

    def track_locations(self) -> list[TrackLocation]:
        return list(self._query_all(TrackLocation))
    
    # TODO: Update methods
