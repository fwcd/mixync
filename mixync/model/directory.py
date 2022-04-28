from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class Directory:
    """A music directory containing audio files."""

    location: str = ''

