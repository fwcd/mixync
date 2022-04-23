from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker, make_transient
from pathlib import Path
from typing import Iterable

from mixync.model.crate import *
from mixync.model.cue import *
from mixync.model.directory import *
from mixync.model.playlist import *
from mixync.model.track import *
from mixync.store import Store
from mixync.store.portable.model import Base
from mixync.store.portable.model.crate import *
from mixync.store.portable.model.crate_track import *
from mixync.store.portable.model.cue import *
from mixync.store.portable.model.directory import *
from mixync.store.portable.model.playlist import *
from mixync.store.portable.model.playlist_track import *
from mixync.store.portable.model.track import *

class PortableStore(Store):
    """A wrapper around a portable musiclib."""

    def __init__(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.audio_path = path / 'audio'

        db_path = path / 'library.sqlite3'
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.make_session = sessionmaker(bind=self.engine, expire_on_commit=False)

        self._create_tables()

        self.previous_id_mappings = {}

    @staticmethod
    def parse_ref(ref: str):
        try:
            path = Path(ref)
        except:
            return None
        if path.name.endswith('.musiclib'):
            return PortableStore(path)
        return None
    
    def _create_tables(self):
        Base.metadata.create_all(self.engine, checkfirst=True)
    
    def tracks(self, name: Optional[str]=None, artist: Optional[str]=None) -> Iterable[Track]:
        with self.make_session() as session:
            constraints = [c for c in [
                PortableTrack.name == name if name else None,
                PortableTrack.artist == artist if artist else None,
            ] if c]
            for track in session.query(PortableTrack).where(*constraints):
                yield Track(
                    id=track.id,
                    title=track.title,
                    artist=track.artist,
                    location=track.location,
                    album=track.album,
                    year=track.year,
                    genre=track.genre,
                    comment=track.comment,
                    duration_ms=track.duration_ms,
                    track_number=track.track_number,
                    url=track.url,
                    sample_rate=track.sample_rate,
                    cues=[Cue(
                        id=cue.id,
                        type=cue.type,
                        position_ms=cue.position_ms,
                        length_ms=cue.length_ms,
                        hotcue=cue.hotcue,
                        label=cue.label,
                        color=cue.color
                    ) for cue in track.cues],
                    bpm=track.bpm,
                    channels=track.channels,
                    times_played=track.times_played,
                    rating=track.rating,
                    key=track.key,
                    color=track.color
                )
    
    def crates(self, name: Optional[str]=None) -> Iterable[Crate]:
        with self.make_session() as session:
            constraints = [c for c in [
                PortableCrate.name == name if name else None,
            ] if c]
            for crate in session.query(PortableCrate).where(*constraints):
                yield Crate(
                    id=crate.id,
                    name=crate.name,
                    date_created=crate.date_created,
                    date_modified=crate.date_modified,
                    locked=crate.locked,
                    track_ids={t.track_id for t in crate.tracks}
                )
    
    def playlists(self, name: Optional[str]=None) -> Iterable[Playlist]:
        with self.make_session() as session:
            constraints = [c for c in [
                PortablePlaylist.name == name if name else None,
            ] if c]
            for playlist in session.query(PortablePlaylist).where(*constraints):
                yield Playlist(
                    id=playlist.id,
                    name=playlist.name,
                    date_created=playlist.date_created,
                    date_modified=playlist.date_modified,
                    type=playlist.type,
                    locked=playlist.locked,
                    track_ids=[t.track_id for t in sorted(playlist.tracks, key=lambda t: t.position)]
                )

    def directories(self) -> Iterable[Directory]:
        with self.make_session() as session:
            for directory in session.query(PortableDirectory):
                yield Directory(
                    id=directory.id,
                    location=directory.location
                )
    
    def _model_to_portable_id(self, session, cls, id, *constraints) -> str:
        mapped_id = self.previous_id_mappings.get(id, None)
        if mapped_id:
            return mapped_id
        existing = session.query(cls).where(*constraints).first()
        new_id = existing.id if existing and existing.id else id
        self.previous_id_mappings[id] = new_id
        return new_id
    
    def update_tracks(self, tracks: list[Track]) -> int:
        count = 0
        with self.make_session.begin() as session:
            for track in tracks:
                id = self._model_to_portable_id(session, PortableTrack, track.id, PortableTrack.title == track.title, PortableTrack.artist == track.artist)
                session.merge(PortableTrack(
                    id=id,
                    title=track.title,
                    artist=track.artist,
                    location=track.location,
                    album=track.album,
                    year=track.year,
                    genre=track.genre,
                    comment=track.comment,
                    duration_ms=track.duration_ms,
                    track_number=track.track_number,
                    url=track.url,
                    sample_rate=track.sample_rate,
                    bpm=track.bpm,
                    beats=track.beats.data if track.beats else None,
                    beats_version=track.beats.version if track.beats else None,
                    beats_sub_version=track.beats.sub_version if track.beats else None,
                    channels=track.channels,
                    times_played=track.times_played,
                    rating=track.rating,
                    key=track.key,
                    keys=track.keys.data if track.keys else None,
                    keys_version=track.keys.version if track.keys else None,
                    keys_sub_version=track.keys.sub_version if track.keys else None,
                    color=track.color
                ))
                if track.cues:
                    session.execute(delete(PortableCue).where(PortableCue.track_id == id))
                for cue in track.cues:
                    session.merge(PortableCue(
                        id=cue.id,
                        type=cue.type,
                        position_ms=cue.position_ms,
                        length_ms=cue.length_ms,
                        hotcue=cue.hotcue,
                        label=cue.label,
                        color=cue.color,
                        track_id=id
                    ))
                count += 1
        return count

    def update_directories(self, directories: list[Directory]) -> int:
        count = 0
        with self.make_session.begin() as session:
            for directory in directories:
                id = self._model_to_portable_id(session, PortableDirectory, directory.id, PortableDirectory.location == directory.location)
                session.merge(PortableDirectory(
                    id=id,
                    location=directory.location
                ))
                count += 1
        return count

    def update_crates(self, crates: list[Crate]) -> int:
        count = 0
        with self.make_session.begin() as session:
            for crate in crates:
                id = self._model_to_portable_id(session, PortableCrate, crate.id, PortableCrate.name == crate.name)
                session.merge(PortableCrate(
                    id=id,
                    name=crate.name,
                    date_created=crate.date_created,
                    date_modified=crate.date_modified,
                    locked=crate.locked
                ))
                for track_id in crate.track_ids:
                    # TODO: Delete old tracks?
                    session.merge(PortableCrateTrack(
                        crate_id=id,
                        track_id=self._model_to_portable_id(session, PortableTrack, track_id)
                    ))
                count += 1
        return count

    def update_playlists(self, playlists: list[Playlist]) -> int:
        count = 0
        with self.make_session.begin() as session:
            for playlist in playlists:
                id = self._model_to_portable_id(session, PortablePlaylist, playlist.id, PortablePlaylist.name == playlist.name)
                session.merge(PortablePlaylist(
                    id=id,
                    name=playlist.name,
                    position=playlist.position,
                    date_created=playlist.date_created,
                    date_modified=playlist.date_modified,
                    type=playlist.type,
                    locked=playlist.locked
                ))
                session.execute(delete(PortablePlaylistTrack).where(PortablePlaylistTrack.playlist_id == id))
                for i, track_id in enumerate(playlist.track_ids):
                    session.merge(PortablePlaylistTrack(
                        playlist_id=playlist.id,
                        track_id=self._model_to_portable_id(session, PortableTrack, track_id),
                        position=i
                    ))
                count += 1
        return count

    def download_track(self, location: str) -> bytes:
        path = self.audio_path / location
        with open(path, 'rb') as f:
            return f.read()

    def upload_track(self, location: str, raw: bytes):
        path = self.audio_path / location
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            f.write(raw)
