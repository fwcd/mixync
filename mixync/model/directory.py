from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class Directory:
    id: str = field(default_factory=lambda: str(uuid4())) # a globally unique id (e.g. UUID, SHA1, ...) independent of Mixxx's id scheme
    location: str = ''

