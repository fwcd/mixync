from sqlalchemy import create_engine
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

# FIXME: Update PortableStore to the new store interface

class PortableStore(Store):
    """A wrapper around the portable musiclib."""

    def __init__(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        self.path = path

        db_path = path / 'library.sqlite3'
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.make_session = sessionmaker(bind=self.engine, expire_on_commit=False)

        self._create_tables()

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
    
    def tracks(self) -> Iterable[Track]:
        with self.make_session() as session:
            for track in session.query(PortableTrack):
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
                    color=track.color,
                    last_played_at=track.last_played_at
                )
    
    def crates(self) -> Iterable[Crate]:
        with self.make_session() as session:
            for crate in session.query(PortableCrate):
                yield Crate(
                    id=crate.id,
                    name=crate.name,
                    date_crated=crate.date_created,
                    date_modified=crate.date_modified,
                    track_ids={t.id for t in crate.tracks}
                )
    
    def playlists(self) -> Iterable[Playlist]:
        with self.make_session() as session:
            for playlist in session.query(PortablePlaylist):
                yield Playlist(
                    id=playlist.id,
                    name=playlist.name,
                    date_crated=playlist.date_created,
                    date_modified=playlist.date_modified,
                    track_ids=[t.id for t in sorted(playlist.tracks, key=lambda t: t.position)]
                )

    def directories(self) -> Iterable[Directory]:
        with self.make_session() as session:
            for directory in session.query(PortableDirectory):
                yield Directory(
                    id=directory.id,
                    location=directory.location
                )
    
    def _merge_all(self, rows: list):
        with self.make_session.begin() as session:
            for row in rows:
                session.merge(row)
        return len(rows)
    
    def update_tracks(self, tracks: list[Track]) -> int:
        count = 0
        with self.make_session.begin() as session:
            for track in tracks:
                # TODO: Find a more performant solution, perhaps involving a
                #       unique constraint across (title, artist) on the portable
                #       db and ignoring when a constraint would be violated?
                #       (this seems to be non-trivial with the high-level ORM API though)
                if not session.query(PortableTrack).where(PortableTrack.title == track.title, PortableTrack.artist == track.artist).first():
                    session.add(PortableTrack(
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
                        cues=[PortableCue(
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
                        color=track.color,
                        last_played_at=track.last_played_at
                    ))
                    count += 1
        return count

    # FIXME: We want to perform a real upsert here instead of a merge
    #        which isn't entirely correct (e.g. cues can get duplicated)

    def update_directories(self, directories: list[Directory]) -> int:
        return self._merge_all(directories)

    def update_crates(self, crates: list[Crate]) -> int:
        return self._merge_all(crates)

    def update_playlists(self, playlists: list[Playlist]) -> int:
        return self._merge_all(playlists)

    def download_track(self, location: str) -> bytes:
        path = self.path / location
        with open(path, 'rb') as f:
            return f.read()

    def upload_track(self, location: str, raw: bytes):
        path = self.path / location
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            f.write(raw)
