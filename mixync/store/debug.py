from typing import TypeVar

from mixync.model.crate import Crate
from mixync.model.directory import Directory
from mixync.model.playlist import Playlist
from mixync.model.track import Track
from mixync.store import Store
from mixync.utils.typing import HasId

T = TypeVar('T', bound='HasId')

class DebugStore(Store):
    """A simple store that outputs updates to stdout for debugging."""

    def __init__(self, compact: bool=False):
        self.compact = compact

    @classmethod
    def parse_ref(cls, ref: str):
        if ref == '@debug':
            return DebugStore(compact=False)
        elif ref == '@debugcompact':
            return DebugStore(compact=True)
        return None
    
    def _fake_ids(self, values: list[T]) -> list[int]:
        i = max([0] + [v.id for v in values if v.id]) + 1
        new_ids = []
        for value in values:
            if value.id:
                new_ids.append(value.id)
            else:
                new_ids.append(i)
                i += 1
        return new_ids
    
    def update_tracks(self, tracks: list[Track]) -> list[int]:
        for track in tracks:
            print(track.name if self.compact else track)
        return self._fake_ids(tracks)

    def update_crates(self, crates: list[Crate]) -> list[int]:
        for crate in crates:
            print(crate.name if self.compact else crate)
        return self._fake_ids(crates)

    def update_playlists(self, playlists: list[Playlist]) -> list[int]:
        for playlist in playlists:
            print(playlist.name if self.compact else playlist)
        return self._fake_ids(playlists)

    def update_directories(self, directories: list[Directory]) -> list[int]:
        for directory in directories:
            print(directory.location if self.compact else directory)
        return self._fake_ids(directories)

    # Upload/download methods

    def upload_track(self, location: str, raw: bytes):
        pass

    def download_track(self, location: str) -> bytes:
        return bytes()
