from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, make_transient
from pathlib import Path
from typing import Iterator, Type, TypeVar
from mixync.model import directory

from mixync.model.directory import *
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
        self.make_session = sessionmaker(bind=engine, expire_on_commit=False)
    
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
    
    def _find_base_directory(self, path: Path) -> Path:
        directories = [Path(dir.directory) for dir in self._query_all(Directory)]

        # Add some default directories as fallback
        directories += [Path.home() / 'Music', Path.home() / 'Downloads']

        # Try to find the base directory among the stored directories
        for directory in directories:
            if path.is_relative_to(directory):
                return directory

        # Fall back to the parent if no other base directory is found
        return path.parent

    def relativize_directory(self, directory: Directory) -> Directory:
        # TODO: Handle case where user may have multiple directories with same name?
        rel = directory.clone()
        rel.directory = Path(rel.directory).name
        return rel

    def relativize_track_location(self, track_location: TrackLocation) -> TrackLocation:
        rel = track_location.clone()
        # Relativize w.r.t a base directory from the db and POSIX-ify paths
        location = Path(rel.location)
        directory = Path(rel.directory)
        base_directory = self._find_base_directory(location)
        rel.directory = directory.name
        rel.location = location.relative_to(base_directory.parent).as_posix()
        return rel
    
    def directories(self) -> list[Directory]:
        return list(self._query_all(Directory))

    def tracks(self) -> list[Track]:
        return list(self._query_all(Track))
    
    def track_locations(self) -> list[TrackLocation]:
        return list(l for l in self._query_all(TrackLocation) if not l.fs_deleted)
    
    # TODO: Update methods and upload

    def download_track(self, location: str) -> bytes:
        with open(location, 'rb') as f:
            return f.read()
        
    def upload_track(self, location: str, raw: bytes):
        with open(location, 'wb') as f:
            f.write(raw)
