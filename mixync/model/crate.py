from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Crate:
    id: str # a UUID independent of Mixxx's id scheme
    name: str
    date_created: datetime = field(default_factory=lambda: datetime())
    date_modified: datetime = field(default_factory=lambda: datetime())
    track_ids: set[str] = field(default_factory=lambda: {})
