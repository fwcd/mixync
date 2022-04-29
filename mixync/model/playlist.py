from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from mixync.model.playlist_type import PlaylistType

@dataclass
class PlaylistHeader:
    id: Optional[int]
    name: str

@dataclass
class Playlist:
    """An ordered list of tracks."""

    id: Optional[int]
    name: str = ''
    position: Optional[int] = None
    date_created: datetime = field(default_factory=datetime.now)
    date_modified: datetime = field(default_factory=datetime.now)
    type: PlaylistType = PlaylistType.DEFAULT
    locked: bool = False
    track_ids: list[int] = field(default_factory=lambda: [])

    def header(self) -> PlaylistHeader:
        return PlaylistHeader(
            id=self.id,
            name=self.name
        )
