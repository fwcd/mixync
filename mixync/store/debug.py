from __future__ import annotations
from typing import Optional, Iterable

from mixync.model.crate import Crate
from mixync.model.cue import Cue
from mixync.model.directory import Directory
from mixync.model.playlist import Playlist
from mixync.model.track import Track
from mixync.options import Options
from mixync.store import Store
from mixync.utils.progress import ProgressLine
from mixync.utils.str import truncate

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
    
    def update_tracks(self, tracks: list[Track]) -> int:
        for track in tracks:
            print(track.title if self.compact else track)
        return len(tracks)

    def update_crates(self, crates: list[Crate]) -> int:
        for crate in crates:
            print(crate.name if self.compact else crate)
        return len(crates)

    def update_playlists(self, playlists: list[Playlist]) -> int:
        for playlist in playlists:
            print(playlist.name if self.compact else playlist)
        return len(playlists)

    def update_directories(self, directories: list[Directory]) -> int:
        for directory in directories:
            print(directory.location if self.compact else directory)
        return len(directories)

    # Upload/download methods

    def upload_track(self, location: str, raw: bytes):
        pass

    def download_track(self, location: str) -> bytes:
        return bytes()
