import re

from dataclasses import dataclass
from typing import Optional

@dataclass
class Directory:
    """A music directory containing audio files."""

    id: Optional[int]
    location: str
