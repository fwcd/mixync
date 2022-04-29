from typing import Protocol, Optional

class Identifiable(Protocol):
    id: Optional[int]
