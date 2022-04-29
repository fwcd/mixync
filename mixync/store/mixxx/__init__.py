from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from hashlib import sha1
from pathlib import Path
from typing import Iterable, Optional, TypeVar

import sys

from mixync.model.beats import Beats
from mixync.model.crate import Crate
from mixync.model.cue import Cue
from mixync.model.directory import Directory
from mixync.model.keys import Keys
from mixync.model.playlist import Playlist
from mixync.model.track import Track
from mixync.store import Store
from mixync.store.mixxx.model import directory
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
from mixync.utils.cli import confirm

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

def find_local_mixxxdir() -> Optional[Path]:
    for path in MIXXXDIR_PATHS:
        if path.is_dir():
            return path
    return None

def find_local_mixxxdb() -> Optional[Path]:
    mixxxdir = find_local_mixxxdir()
    if not mixxxdir:
        return None
    return mixxxdir / 'mixxxdb.sqlite'

MIN_SCHEMA_VERSION = 32

class MixxxStore(Store):
    """A wrapper around the user's local mixxxdb."""

    def __init__(self, path: Optional[Path]=None):
        path = path or find_local_mixxxdb()
        if not path:
            raise RuntimeError('No mixxxdb found')
        engine = create_engine(f'sqlite:///{path}')
        self.make_session = sessionmaker(bind=engine, expire_on_commit=False)

        schema_version = self._schema_version() or 0
        if schema_version < MIN_SCHEMA_VERSION:
            raise RuntimeError(f'Mixxxdb has schema version {schema_version}, but the minimum version supported by mixync is {MIN_SCHEMA_VERSION}.')
    
    @classmethod
    def parse_ref(cls, ref: str):
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

    def _directories(self) -> list[Path]:
        with self.make_session() as session:
            return [Path(dir.directory) for dir in session.query(MixxxDirectory)]

    def _find_base_directory(self, path: Path, opts: Options) -> Optional[Path]:
        directories = self._directories()

        # Try to find the base directory among the stored directories
        for directory in directories:
            if path.is_relative_to(directory):
                return directory

        # If not skip_uncategorized, use the parent directory
        return None if opts.skip_uncategorized else path.parent

    def relativize_directory(self, directory: Directory, opts: Options) -> Optional[Directory]:
        # TODO: Handle case where user may have multiple directories with same name?
        new_directory = super().relativize_directory(directory, opts)
        if not new_directory:
            return None
        new_directory.location = Path(directory.location).name
        return new_directory

    def relativize_track(self, track: Track, opts: Options) -> Optional[Track]:
        # Relativize w.r.t a base directory from the db and POSIX-ify paths
        new_track = super().relativize_track(track, opts)
        if not new_track:
            return None
        location = Path(track.location)
        base_directory = self._find_base_directory(location, opts)
        if not base_directory:
            return None
        rel_location = location.relative_to(base_directory.parent)
        new_track.location = rel_location.as_posix()
        return new_track
    
    def _find_matching_directory(self, name: str, opts: Options) -> Path:
        directories = self._directories()

        # If a destination root directory is specified, use a subdirectory
        if opts.dest_root_dir:
            return opts.dest_root_dir / name

        # Try to find a matching directory among the stored directories
        for directory in directories:
            if directory.name == name:
                return directory
        
        # Otherwise use a subdirectory of ~/Music
        root_directory = Path.home() / 'Music'
        return root_directory / name

    def absolutize_directory(self, directory: Directory, opts: Options) -> Optional[Directory]:
        new_directory = super().absolutize_directory(directory, opts)
        if not new_directory:
            return None
        location = Path(directory.location)
        if not location.parts:
            raise ValueError('Cannot absolutize a directory with an empty location path.')
        matching_location = self._find_matching_directory(location.parts[0], opts).resolve()
        if not confirm(f"Map '{directory.location}' to '{matching_location}'?", opts):
            print('Okay, quitting')
            sys.exit(0)
        if opts.log and opts.assume_yes:
            print(f"Mapping '{directory.location}' to '{matching_location}'")
        new_directory.location = str(matching_location)
        return new_directory
    
    # TODO: absolutize_track
    
    def _directory_id(self, location: str) -> int:
        return int(sha1(location.encode('utf8')).hexdigest(), 16)

    def directories(self) -> Iterable[Directory]:
        with self.make_session() as session:
            for directory in session.query(MixxxDirectory):
                yield Directory(
                    id=self._directory_id(directory.directory),
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
                        id=track.id,
                        name=track.title or '',
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
                        cues=[Cue(
                            type=c.type,
                            position_ms=sample_to_ms(c.position),
                            length_ms=sample_to_ms(c.length),
                            hotcue=c.hotcue if c.hotcue >= 0 else None,
                            label=c.label if c.label else None,
                            color=c.color
                        ) for c in session.query(MixxxCue).where(MixxxCue.track_id == track.id)],
                        bpm=track.bpm,
                        beats=Beats(
                            data=track.beats,
                            version=track.beats_version,
                            sub_version=track.beats_sub_version
                        ),
                        channels=track.channels,
                        times_played=track.timesplayed,
                        rating=track.rating,
                        key=track.key,
                        keys=Keys(
                            data=track.keys,
                            version=track.keys_version,
                            sub_version=track.keys_sub_version
                        ),
                        color=track.color
                    )
    
    def crates(self, name: Optional[str]=None) -> Iterable[Crate]:
        with self.make_session() as session:
            constraints = [c for c in [
                MixxxCrate.name == name if name else None,
            ] if c]
            for crate in session.query(MixxxCrate).where(*constraints):
                # TODO: Proper creation/modification dates?
                yield Crate(
                    id=crate.id,
                    name=crate.name,
                    locked=bool(crate.locked),
                    track_ids={t.track_id for t in session.query(MixxxCrateTrack).where(MixxxCrateTrack.crate_id == crate.id)}
                )
    
    def playlists(self, name: Optional[str]=None) -> Iterable[Playlist]:
        with self.make_session() as session:
            constraints = [c for c in [
                MixxxPlaylist.name == name if name else None,
            ] if c]
            for playlist in session.query(MixxxPlaylist).where(*constraints):
                yield Playlist(
                    id=playlist.id,
                    name=playlist.name,
                    position=playlist.position,
                    date_created=playlist.date_created,
                    date_modified=playlist.date_modified,
                    type=playlist.hidden,
                    locked=bool(playlist.locked),
                    track_ids=[t.id for t in session.query(MixxxPlaylistTrack).where(MixxxPlaylistTrack.playlist_id == playlist.id)]
                )
    
    def update_tracks(self, tracks: list[Track]) -> list[int]:
        new_ids = []
        with self.make_session.begin() as session:
            for track in tracks:
                location = session.query(MixxxTrackLocation).where(MixxxTrackLocation.location == track.location).first()
                if not location:
                    path = Path(track.location).resolve()
                    location = session.add(MixxxTrackLocation(
                        location=track.location,
                        filename=path.name,
                        directory=str(path.parent),
                        filesize=path.stat().st_size,
                        fs_deleted=0,
                        needs_verification=0
                    ))
                # TODO: Insert main cue point as 'cuepoint' (in addition to the cues below)?
                new_track = session.merge(MixxxTrack(
                    id=track.id,
                    name=track.name,
                    artist=track.artist,
                    album=track.album,
                    year=track.year,
                    genre=track.genre,
                    location=location.id,
                    comment=track.comment,
                    url=track.url,
                    duration=float(track.duration_ms) / 1000.0 if track.duration_ms else None,
                    samplerate=track.sample_rate,
                    bpm=track.bpm,
                    beats=track.beats.data if track.beats else None,
                    beats_version=track.beats.version if track.beats else None,
                    beats_sub_version=track.beats.sub_version if track.beats else None,
                    key=track.key,
                    keys=track.keys.data if track.keys else None,
                    keys_version=track.keys.version if track.keys else None,
                    keys_sub_version=track.keys.sub_version if track.keys else None,
                    channels=track.channels,
                    timesplayed=track.times_played,
                    rating=track.rating,
                    color=track.color
                ))
                session.flush()
                new_ids.append(new_track.id)
                # TODO: More sophisticated cue merging strategy?
                if track.cues:
                    session.execute(delete(MixxxCue).where(MixxxCue.track_id == new_track.id))
                    for cue in track.cues:
                        session.merge(MixxxCue(
                            type=cue.type,
                            position_ms=cue.position_ms,
                            length_ms=cue.length_ms,
                            hotcue=cue.hotcue,
                            label=cue.label,
                            color=cue.color,
                            track_id=new_track.id
                        ))
        return new_ids

    def update_directories(self, directories: list[Directory]) -> list[int]:
        new_ids = []
        with self.make_session() as session:
            for directory in directories:
                session.merge(MixxxDirectory(
                    location=directory.location
                ))
                session.flush()
                new_ids.append(self._directory_id(directory.location))
        return new_ids

    def update_crates(self, crates: list[Crate]) -> list[int]:
        new_ids = []
        with self.make_session() as session:
            for crate in crates:
                new_crate = session.merge(MixxxCrate(
                    id=crate.id,
                    name=crate.name,
                    count=len(crate.track_ids),
                    locked=crate.locked
                ))
                session.flush()
                new_ids.append(new_crate.id)
                # TODO: More sophisticated crate merging strategy
                # (should we delete old tracks like with playlists, even though we don't have to worry about order?)
                for track_id in crate.track_ids:
                    session.merge(MixxxCrateTrack(
                        crate_id=new_crate.id,
                        track_id=track_id
                    ))
        return new_ids

    def update_playlists(self, playlists: list[Playlist]) -> list[int]:
        new_ids = []
        with self.make_session() as session:
            for playlist in playlists:
                new_playlist = session.merge(MixxxPlaylist(
                    id=playlist.id,
                    name=playlist.name,
                    # TODO: Merge position
                    # position=playlist.position,
                    type=playlist.type,
                    locked=playlist.locked
                ))
                session.flush()
                new_ids.append(new_playlist.id)
                # TODO: More sophisticated playlist merging strategy than just replacing?
                session.execute(delete(MixxxPlaylistTrack).where(MixxxPlaylistTrack.playlist_id == new_playlist.id))
                for i, track_id in enumerate(playlist.track_ids):
                    session.merge(MixxxPlaylistTrack(
                        playlist_id=new_playlist.id,
                        track_id=track_id,
                        position=i
                    ))
        return new_ids
    
    def download_track(self, location: str) -> bytes:
        with open(location, 'rb') as f:
            return f.read()
        
    def upload_track(self, location: str, raw: bytes):
        with open(location, 'wb') as f:
            f.write(raw)
