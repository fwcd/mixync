from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Beats:
    """
    A binary beatgrid, in one of Mixxx's formats (e.g. BeatMap-1.0).
    See https://github.com/mixxxdj/mixxx/blob/adecac93b3e8764985437266aa8ade17ccda62c6/src/track/beats.h.
    """

    data: Optional[bytes] = None
    version: Optional[str] = None
    sub_version: Optional[str] = None
