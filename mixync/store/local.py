from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, make_transient
from pathlib import Path

from mixync.model.track import *
from mixync.model.track_location import *
from mixync.store import Store

MIXXXDIR_PATHS = [
    # Linux
    Path.home() / '.mixxx',
    # macOS
    Path.home() / 'Library' / 'Containers' / 'org.mixxx.mixxx' / 'Data' / 'Library' / 'Application Support' / 'Mixxx',
    Path.home() / 'Library' / 'Application Support' / 'Mixxx',
    # Windows
    Path.home() / 'AppData' / 'Local' / 'Mixxx',
]

def find_local_mixxxdir() -> Path:
    for path in MIXXXDIR_PATHS:
        if path.is_dir():
            return path
    return None

LOCAL_MIXXXDB_PATH = find_local_mixxxdir() / 'mixxxdb.sqlite'

class LocalStore(Store):
    """A wrapper around the user's local mixxxdb."""

    def __init__(self, path: Path=LOCAL_MIXXXDB_PATH):
        engine = create_engine(f'sqlite:///{path}')
        self.make_session = sessionmaker(bind=engine)
    
    @staticmethod
    def parse_ref(ref: str):
        if ref == '@local':
            return LocalStore()
        try:
            path = Path(ref)
            if path.name == 'mixxxdb.sqlite':
                return LocalStore(path)
        except:
            pass
        return None

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
