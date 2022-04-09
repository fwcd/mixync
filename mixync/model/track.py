from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from mixync.model.cue import Cue

@dataclass
class Track:
    id: str # a UUID independent of Mixxx's id scheme
    title: str
    artist: str
    location: str
    duration: float
    album: Optional[str] = None
    tracknumber: Optional[int] = None
    year: Optional[str] = None
    genre: Optional[str] = None
    comment: Optional[str] = None
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
