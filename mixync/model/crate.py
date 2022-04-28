from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class CrateHeader:
    id: int
    name: str

@dataclass
class Crate:
    """An unordered list of tracks."""

    id: int
    name: str = ''
    date_created: datetime = field(default_factory=datetime.now)
    date_modified: datetime = field(default_factory=datetime.now)
    hidden: bool = False
    locked: bool = False
    track_ids: set[str] = field(default_factory=lambda: {})

    def header(self) -> CrateHeader:
        return CrateHeader(
            id=self.id,
            name=self.name
        )
