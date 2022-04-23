from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, make_transient
from pathlib import Path
from typing import Iterable, Optional, Type, TypeVar

import hashlib
import random

from mixync.model.crate import Crate
from mixync.model.cue import Cue
from mixync.model.directory import Directory
from mixync.model.playlist import Playlist
from mixync.model.track import Track
from mixync.store import Store
from mixync.store.mixxx.model.crate import *
from mixync.store.mixxx.model.crate_track import *
from mixync.store.mixxx.model.cue import *
from mixync.store.mixxx.model.directory import *
from mixync.store.mixxx.model.playlist import *
from mixync.store.mixxx.model.playlist_track import *
from mixync.store.mixxx.model.setting import *
from mixync.store.mixxx.model.track import *
from mixync.store.mixxx.model.track_location import *
from mixync.options import Options

T = TypeVar('T')
ID_HASH_BASE = random.getrandbits(64)

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
MIN_SCHEMA_VERSION = 32

class MixxxStore(Store):
    """A wrapper around the user's local mixxxdb."""

    def __init__(self, path: Path=LOCAL_MIXXXDB_PATH):
        engine = create_engine(f'sqlite:///{path}')
        self.make_session = sessionmaker(bind=engine, expire_on_commit=False)

        schema_version = self._schema_version()
        if schema_version < MIN_SCHEMA_VERSION:
            raise RuntimeError(f'Mixxxdb has schema version {schema_version}, but the minimum version supported by mixync is {MIN_SCHEMA_VERSION}.')
    
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
    
    def _schema_version(self) -> Optional[int]:
        with self.make_session() as session:
            row = session.query(MixxxSetting).where(MixxxSetting.name == 'mixxx.schema.version').first()
            if not row:
                return None
            return int(row.value)

    def _find_base_directory(self, path: Path, opts: Options) -> Optional[Path]:
        with self.make_session() as session:
            directories = [Path(dir.directory) for dir in session.query(MixxxDirectory)]

        # Try to find the base directory among the stored directories
        for directory in directories:
            if path.is_relative_to(directory):
                return directory

        # If not skip_uncategorized, use the parent directory
        return None if opts.skip_uncategorized else path.parent

    def relativize_directory(self, directory: Directory, opts: Options) -> Optional[Directory]:
        # TODO: Handle case where user may have multiple directories with same name?
        new_directory = super().relativize_directory(directory, opts)
        new_directory.location = Path(directory.location).name
        return new_directory

    def relativize_track(self, track: Track, opts: Options) -> Optional[Track]:
        # Relativize w.r.t a base directory from the db and POSIX-ify paths
        new_track = super().relativize_track(track, opts)
        location = Path(track.location)
        base_directory = self._find_base_directory(location, opts)
        if not base_directory:
            return None
        rel_location = location.relative_to(base_directory.parent)
        new_track.location = rel_location.as_posix()
        return new_track
    
    def _make_model_id(self, id):
        h = hashlib.sha1()
        h.update(str(ID_HASH_BASE).encode())
        h.update(str(id).encode())
        return h.hexdigest()

    def directories(self) -> Iterable[Directory]:
        with self.make_session() as session:
            for directory in session.query(MixxxDirectory):
                yield Directory(
                    id=self._make_model_id(directory.directory),
                    location=directory.directory
                )
    
    # TODO: Use SQLAlechemy ORM relationships to model e.g. track_locations or crate_tracks
    
    def tracks(self, name: Optional[str]=None, artist: Optional[str]=None) -> Iterable[Track]:
        with self.make_session() as session:
            constraints = [c for c in [
                MixxxTrack.name == name if name else None,
                MixxxTrack.artist == artist if artist else None,
            ] if c]
            for track in session.query(MixxxTrack).where(*constraints):
                def sample_to_ms(s) -> int:
                    return int(s * 1000 / (track.channels * track.samplerate))

                location = session.query(MixxxTrackLocation).where(MixxxTrackLocation.id == track.location).first()
                if location and not location.fs_deleted:
                    yield Track(
                        id=self._make_model_id(track.id),
                        title=track.title or '',
                        artist=track.artist or '',
                        location=location.location or '',
                        album=track.album or '',
                        year=track.year or '',
                        genre=track.genre or '',
                        comment=track.comment or '',
                        duration_ms=int(track.duration * 1000),
                        track_number=track.tracknumber,
                        url=track.url,
                        sample_rate=track.samplerate,
                        cues=list(Cue(
                            id=self._make_model_id(c.id),
                            type=c.type,
                            position_ms=sample_to_ms(c.position),
                            length_ms=sample_to_ms(c.length),
                            hotcue=c.hotcue if c.hotcue >= 0 else None,
                            label=c.label if c.label else None,
                            color=c.color
                        ) for c in session.query(MixxxCue).where(MixxxCue.track_id == track.id)),
                        bpm=track.bpm,
                        channels=track.channels,
                        times_played=track.timesplayed,
                        rating=track.rating,
                        key=track.key,
                        color=track.color,
                        last_played_at=track.last_played_at
                    )
    
    def crates(self, name: Optional[str]=None) -> Iterable[Crate]:
        with self.make_session() as session:
            constraints = [c for c in [
                MixxxCrate.name == name if name else None,
            ] if c]
            for crate in session.query(MixxxCrate).where(*constraints):
                # TODO: Proper creation/modification dates?
                yield Crate(
                    id=self._make_model_id(crate.id),
                    name=crate.name,
                    locked=bool(crate.locked),
                    track_ids=list(
                        self._make_model_id(t.track_id)
                        for t in session.query(MixxxCrateTrack).where(MixxxCrateTrack.crate_id == crate.id)
                    )
                )
    
    def playlists(self, name: Optional[str]=None) -> Iterable[Playlist]:
        with self.make_session() as session:
            constraints = [c for c in [
                MixxxPlaylist.name == name if name else None,
            ] if c]
            for playlist in session.query(MixxxPlaylist).where(*constraints):
                yield Playlist(
                    id=self._make_model_id(playlist.id),
                    name=playlist.name,
                    position=playlist.position,
                    date_created=playlist.date_created,
                    date_modified=playlist.date_modified,
                    type=playlist.hidden,
                    locked=bool(playlist.locked),
                    track_ids=list(
                        self._make_model_id(t.id)
                        for t in session.query(MixxxPlaylistTrack).where(MixxxPlaylistTrack.playlist_id == playlist.id)
                    )
                )
    
    # TODO: Update methods and upload

    def download_track(self, location: str) -> bytes:
        with open(location, 'rb') as f:
            return f.read()
        
    def upload_track(self, location: str, raw: bytes):
        with open(location, 'wb') as f:
            f.write(raw)
