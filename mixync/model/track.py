from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional

from mixync.model.cue import Cue

@dataclass
class Track:
    id: str = field(default_factory=lambda: str(uuid4())) # a globally unique id (e.g. UUID, SHA1, ...) independent of Mixxx's id scheme
    title: str = ''
    artist: str = ''
    location: str = ''
    album: str = ''
    year: str = ''
    genre: str = ''
    comment: str = ''
    duration_ms: Optional[int] = None
    tracknumber: Optional[int] = None
    url: Optional[str] = None
    samplerate: Optional[int] = None
    # We don't need cuepoint, since that one's stored in cues too
    cues: list[Cue] = field(default_factory=lambda: [])
    bpm: Optional[float] = None
    channels: Optional[int] = None
    times_played: Optional[int] = None
    rating: Optional[int] = None
    key: Optional[str] = None
    color: Optional[int] = None
    last_played_at: datetime = field(default_factory=datetime.now)
