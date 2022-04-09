from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, make_transient
from pathlib import Path
from typing import Iterator, Optional, Type, TypeVar

from mixync.store import Store
from mixync.store.mixxx.model.crate import *
from mixync.store.mixxx.model.crate_track import *
from mixync.store.mixxx.model.cue import *
from mixync.store.mixxx.model.directory import *
from mixync.store.mixxx.model.playlist import *
from mixync.store.mixxx.model.playlist_track import *
from mixync.store.mixxx.model.track import *
from mixync.store.mixxx.model.track_location import *
from mixync.options import Options

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

class MixxxStore(Store):
    """A wrapper around the user's local mixxxdb."""

    def __init__(self, path: Path=LOCAL_MIXXXDB_PATH):
        engine = create_engine(f'sqlite:///{path}')
        self.make_session = sessionmaker(bind=engine, expire_on_commit=False)
    
    @staticmethod
    def parse_ref(ref: str):
        if ref == '@local':
            return MixxxStore()
        try:
            path = Path(ref)
        except:
            return None
        if path.name == 'mixxxdb.sqlite':
            return MixxxStore(path)
        return None

    def _query_all(self, cls: Type[T]) -> Iterator[T]:
        with self.make_session() as session:
            for row in session.query(cls):
                make_transient(row)
                row.id = None
                yield row
    
    def _find_base_directory(self, path: Path, opts: Options) -> Optional[Path]:
        directories = [Path(dir.directory) for dir in self._query_all(MixxxDirectory)]

        # Try to find the base directory among the stored directories
        for directory in directories:
            if path.is_relative_to(directory):
                return directory

        # If not skip_uncategorized, use the parent directory
        return None if opts.skip_uncategorized else path.parent

    def relativize_directory_location(self, location: str, opts: Options) -> Optional[Directory]:
        # TODO: Handle case where user may have multiple directories with same name?
        return Path(location).name

    def relativize_track_location(self, location: str, opts: Options) -> Optional[TrackLocation]:
        # Relativize w.r.t a base directory from the db and POSIX-ify paths
        location = Path(location)
        base_directory = self._find_base_directory(location, opts)
        if not base_directory:
            return None
        rel_location = location.relative_to(base_directory.parent)
        return rel_location.as_posix()
    
    def directories(self) -> list[Directory]:
        return list(self._query_all(MixxxDirectory))

    def tracks(self) -> list[Track]:
        return list(self._query_all(MixxxTrack))
    
    def track_locations(self) -> list[TrackLocation]:
        return list(l for l in self._query_all(MixxxTrackLocation) if not l.fs_deleted)

    def cues(self) -> list[Cue]:
        return list(self._query_all(MixxxCue))
    
    def crates(self) -> list[Crate]:
        return list(self._query_all(MixxxCrate))
    
    def crate_tracks(self) -> list[CrateTrack]:
        return list(self._query_all(MixxxCrateTrack))
    
    def playlists(self) -> list[Playlist]:
        return list(self._query_all(MixxxPlaylist))
    
    def playlist_tracks(self) -> list[PlaylistTrack]:
        return list(self._query_all(MixxxPlaylistTrack))
    
    # TODO: Update methods and upload

    def download_track(self, location: str) -> bytes:
        with open(location, 'rb') as f:
            return f.read()
        
    def upload_track(self, location: str, raw: bytes):
        with open(location, 'wb') as f:
            f.write(raw)
