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

    @classmethod
    def parse_ref(cls, ref: str):
        if ref == '@debug':
            return DebugStore()
        return None
    
    def update_tracks(self, tracks: list[Track]) -> int:
        for track in tracks:
            print(track)

    def update_crates(self, crates: list[Crate]) -> int:
        for crate in crates:
            print(crate)

    def update_playlists(self, playlists: list[Playlist]) -> int:
        for playlist in playlists:
            print(playlist)

    def update_directories(self, directories: list[Directory]) -> int:
        for directory in directories:
            print(directory)

    # Upload/download methods

    def upload_track(self, location: str, raw: bytes):
        pass

    def download_track(self, location: str) -> bytes:
        return bytes()
