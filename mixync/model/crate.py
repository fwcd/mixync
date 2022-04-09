from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

@dataclass
class Crate:
    id: str = field(default_factory=lambda: str(uuid4())) # a globally unique id (e.g. UUID, SHA1, ...) independent of Mixxx's id scheme
    name: str = ''
    date_created: datetime = field(default_factory=datetime.now)
    date_modified: datetime = field(default_factory=datetime.now)
    track_ids: set[str] = field(default_factory=lambda: {})
