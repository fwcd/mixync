from typing import Protocol, Optional

class HasId(Protocol):
    id: Optional[int]
