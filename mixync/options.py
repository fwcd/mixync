from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

@dataclass
class Options:
    # Whether to skip tracks that are not in any of the defined collection folders
    skip_uncategorized: bool = True
    # Whether to log output during the copy.
    log: bool = False
    # Whether to log output verbosely during the copy.
    verbose: bool = False
    # Whether to skip all actual file changes.
    dry_run: bool = False
    # Whether to disable interactive prompts.
    assume_yes: bool = False
    # A root folder to place copied music directories in. Only used
    # by some stores. For example, when set to ~/Music/Mixync and when
    # copying to the @local Mixxx store, the directories would be placed
    # under this directory.
    dest_root_dir: Optional[Path] = None
    # Names of music directories to include.
    filter_dirs: set[str] = field(default_factory=set)
