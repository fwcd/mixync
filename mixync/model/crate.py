from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

@dataclass
class Crate:
    id: str = field(default_factory=lambda: str(uuid4())) # a UUID independent of Mixxx's id scheme
    name: str = ''
    date_created: datetime = field(default_factory=lambda: datetime())
    date_modified: datetime = field(default_factory=lambda: datetime())
    track_ids: set[str] = field(default_factory=lambda: {})
