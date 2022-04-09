from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, make_transient
from pathlib import Path

from mixync.model import Base
from mixync.model.crate import *
from mixync.model.crate_track import *
from mixync.model.cue import *
from mixync.model.directory import *
from mixync.model.playlist import *
from mixync.model.track import *
from mixync.model.track_location import *
from mixync.store import Store

class PortableStore(Store):
    """A wrapper around the portable mixxxlib."""

    def __init__(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        self.path = path

        db_path = path / 'mixxxdb.portable.sqlite'
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.make_session = sessionmaker(bind=self.engine, expire_on_commit=False)

        self._create_tables()

    @staticmethod
    def parse_ref(ref: str):
        try:
            path = Path(ref)
            if path.name.endswith('.mixxxlib'):
                return PortableStore(path)
        except:
            pass
        return None
    
    def _create_tables(self):
        Base.metadata.create_all(self.engine, checkfirst=True)
    
    def _query_all(self, cls) -> list:
        with self.make_session() as session:
            for row in session.query(cls):
                make_transient(row)
                row.id = None
                yield row
    
    def tracks(self) -> list[Track]:
        return list(self._query_all(Track))
    
    def track_locations(self) -> list[TrackLocation]:
        return list(self._query_all(TrackLocation))
    
    def update_tracks(self, tracks: list[Track]):
        with self.make_session() as session:
            for track in tracks:
                # TODO: Find a more performant solution, perhaps involving a
                #       unique constraint across (title, artist) on the portable
                #       db and ignoring when a constraint would be violated?
                #       (this seems to be non-trivial with the high-level ORM API though)
                if not session.query(Track).where(Track.title == track.title, Track.artist == track.artist).first():
                    session.add(track)
            session.commit()

    def update_track_locations(self, track_locations: list[TrackLocation]):
        visited_locations = set()
        with self.make_session() as session:
            for location in track_locations:
                # TODO: See note in method above about performance
                if location.location not in visited_locations and not session.query(TrackLocation).where(TrackLocation.location == location.location).first():
                    session.add(location)
                    visited_locations.add(location.location)
            session.commit()
    
    def update_directories(self, directories: list[Directory]):
        with self.make_session() as session:
            for directory in directories:
                session.merge(directory)
            session.commit()
    
    def download_track(self, location: str) -> bytes:
        path = self.path / location
        with open(path, 'rb') as f:
            return f.read()

    def upload_track(self, location: str, raw: bytes):
        path = self.path / location
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            f.write(raw)
