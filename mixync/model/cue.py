from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4

@dataclass
class Cue:
    id: str = field(default_factory=lambda: str(uuid4())) # a globally unique id (e.g. UUID, SHA1, ...) independent of Mixxx's id scheme
    type: int = 0
    position: Optional[int] = None
    # TODO: Figure out in which units these fields are and perhaps restructure them
    length: int = 0
    hotcue: int = -1
    label: str = ''
    color: int = 0xFFFF0000
