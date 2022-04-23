from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Keys:
    """
    A binary keygrid, in one of Mixxx's formats (e.g. KeyMap-1.0).
    See https://github.com/mixxxdj/mixxx/blob/adecac93b3e8764985437266aa8ade17ccda62c6/src/track/keys.h.
    """

    data: Optional[bytes] = None
    version: Optional[str] = None
    sub_version: Optional[str] = None
