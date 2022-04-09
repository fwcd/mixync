from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Playlist:
    id: str # a UUID independent of Mixxx's id scheme
    name: str
    position: int
    date_created: datetime = field(default_factory=lambda: datetime())
    date_modified: datetime = field(default_factory=lambda: datetime())
    track_ids: list[str] = field(default_factory=lambda: [])
