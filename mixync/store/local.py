from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, make_transient
from pathlib import Path
from typing import Iterator, Type, TypeVar

from mixync.model.track import *
from mixync.model.track_location import *
from mixync.store import Store

T = TypeVar('T')

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

    def _query_all(self, cls: Type[T]) -> Iterator[T]:
        with self.make_session() as session:
            for row in session.query(cls):
                make_transient(row)
                row.id = None
                yield row
    
    def _query_track_locations(self) -> Iterator[TrackLocation]:
        for row in self._query_all(TrackLocation):
            if not row.fs_deleted:
                # Relativize paths
                directory = Path(row.directory)
                row.directory = directory.name
                row.location = Path(row.location).relative_to(directory.parent).as_posix()
                yield row

    def tracks(self) -> list[Track]:
        return list(self._query_all(Track))
    
    def track_locations(self) -> list[TrackLocation]:
        return list(self._query_track_locations())
    
    # TODO: Update methods
