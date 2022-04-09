from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4

@dataclass
class Cue:
    id: str = field(default_factory=lambda: str(uuid4())) # a globally unique id (e.g. UUID, SHA1, ...) independent of Mixxx's id scheme
    type: int = 0
    position_ms: Optional[int] = None
    length_ms: int = 0
    hotcue: Optional[int] = None # the hotcue index
    label: str = ''
    color: int = 0xFFFF0000
