from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class CrateHeader:
    id: Optional[int]
    name: str

@dataclass
class Crate:
    """An unordered list of tracks."""

    id: Optional[int]
    name: str = ''
    date_created: datetime = field(default_factory=datetime.now)
    date_modified: datetime = field(default_factory=datetime.now)
    hidden: bool = False
    locked: bool = False
    track_ids: set[int] = field(default_factory=lambda: set())

    def header(self) -> CrateHeader:
        return CrateHeader(
            id=self.id,
            name=self.name
        )
