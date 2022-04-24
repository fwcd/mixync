from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class Options:
    # Whether to skip tracks that are not in any of the defined collection folders
    skip_uncategorized: bool = True
    # Whether to log output during the copy.
    log: bool = False
    # A root folder to place copied music directories in. Only used
    # by some stores. For example, when set to ~/Music/Mixync and when
    # copying to the @local Mixxx store, the directories would be placed
    # under this directory.
    dest_root_dir: Optional[Path] = None
