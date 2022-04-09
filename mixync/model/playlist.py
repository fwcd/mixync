from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

@dataclass
class Playlist:
    id: str = field(default_factory=lambda: str(uuid4())) # a UUID independent of Mixxx's id scheme
    name: str = ''
    position: Optional[int] = None
    date_created: datetime = field(default_factory=lambda: datetime())
    date_modified: datetime = field(default_factory=lambda: datetime())
    track_ids: list[str] = field(default_factory=lambda: [])
