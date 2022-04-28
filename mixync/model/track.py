from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from mixync.model.beats import Beats
from mixync.model.cue import Cue
from mixync.model.keys import Keys

@dataclass
class TrackHeader:
    id: int
    title: str
    artist: str

@dataclass
class Track:
    """A song."""

    id: int
    title: str = ''
    artist: str = ''
    location: str = ''
    album: str = ''
    year: str = ''
    genre: str = ''
    comment: str = ''
    duration_ms: Optional[int] = None
    track_number: Optional[int] = None
    url: Optional[str] = None
    sample_rate: Optional[int] = None
    # We don't need cuepoint, since that one's stored in cues too
    cues: list[Cue] = field(default_factory=lambda: [])
    bpm: Optional[float] = None
    beats: Optional[Beats] = None
    key: Optional[str] = None
    keys: Optional[Keys] = None
    channels: Optional[int] = None
    times_played: Optional[int] = None
    rating: Optional[int] = None
    color: Optional[int] = None
    last_played_at: Optional[datetime] = None

    def header(self) -> TrackHeader:
        return TrackHeader(
            id=self.id,
            title=self.title,
            artist=self.artist
        )
