from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

from mixync.model.playlist_type import PlaylistType

@dataclass
class Playlist:
    """An ordered list of tracks."""

    id: int
    name: str = ''
    position: Optional[int] = None
    date_created: datetime = field(default_factory=datetime.now)
    date_modified: datetime = field(default_factory=datetime.now)
    type: PlaylistType = PlaylistType.DEFAULT
    locked: bool = False
    track_ids: list[str] = field(default_factory=lambda: [])
