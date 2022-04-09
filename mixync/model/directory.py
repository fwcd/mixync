from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class Directory:
    id: str = field(default_factory=lambda: str(uuid4())) # a UUID independent of Mixxx's id scheme
    location: str = ''

