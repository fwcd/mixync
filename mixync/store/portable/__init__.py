from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, make_transient
from pathlib import Path

from mixync.model.crate import *
from mixync.model.cue import *
from mixync.model.directory import *
from mixync.model.playlist import *
from mixync.model.track import *
from mixync.store import Store

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
        pass
        # Base.metadata.create_all(self.engine, checkfirst=True)
    
    def _query_all(self, cls) -> list:
        with self.make_session() as session:
            for row in session.query(cls):
                make_transient(row)
                row.id = None
                yield row
    
    def tracks(self) -> list[Track]:
        return list(self._query_all(Track))
    
    def cues(self) -> list[Cue]:
        return list(self._query_all(Cue))
    
    def crates(self) -> list[Crate]:
        return list(self._query_all(Crate))
    
    def playlists(self) -> list[Playlist]:
        return list(self._query_all(Playlist))
    
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
                if not session.query(Track).where(Track.title == track.title, Track.artist == track.artist).first():
                    session.add(track)
                    count += 1
        return count

    # FIXME: We want to perform a real upsert here instead of a merge
    #        which isn't entirely correct (e.g. cues can get duplicated)

    def update_directories(self, directories: list[Directory]) -> int:
        return self._merge_all(directories)

    def update_cues(self, cues: list[Cue]) -> int:
        return self._merge_all(cues)

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
