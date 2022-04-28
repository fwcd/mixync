from dataclasses import dataclass
from typing import Optional

from mixync.model.cue_type import CueType

@dataclass
class Cue:
    """A position or loop marker within a track."""

    type: CueType = CueType.INVALID
    position_ms: Optional[int] = None
    length_ms: int = 0
    hotcue: Optional[int] = None # the hotcue index
    label: Optional[str] = None
    color: int = 0xFFFF0000
