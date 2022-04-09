from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional

from mixync.model.cue import Cue

@dataclass
class Track:
    id: str = field(default_factory=lambda: str(uuid4())) # a UUID independent of Mixxx's id scheme
    title: str = ''
    artist: str = ''
    location: str = ''
    album: str = ''
    year: str = ''
    genre: str = ''
    comment: str = ''
    duration: Optional[float] = None
    tracknumber: Optional[int] = None
    url: Optional[str] = None
    samplerate: Optional[int] = None
    cuepoint: int = 0
    cues: list[Cue] = field(default_factory=lambda: [])
    bpm: Optional[float] = None
    channels: Optional[int] = None
    times_played: Optional[int] = None
    rating: Optional[int] = None
    key: Optional[str] = None
    color: Optional[int] = None
    last_played_at: datetime = field(default_factory=lambda: datetime())
