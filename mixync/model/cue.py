from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4

from mixync.model.cue_type import CueType

@dataclass
class Cue:
    """A position or loop marker within a track."""

    id: str = field(default_factory=lambda: str(uuid4())) # a globally unique id (e.g. UUID, SHA1, ...) independent of Mixxx's id scheme
    type: CueType = CueType.INVALID
    position_ms: Optional[int] = None
    length_ms: int = 0
    hotcue: Optional[int] = None # the hotcue index
    label: Optional[str] = None
    color: int = 0xFFFF0000
