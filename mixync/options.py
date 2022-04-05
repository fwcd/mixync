from dataclasses import dataclass
from pathlib import Path

@dataclass
class Options:
    # The mixxxdb.sqlite3
    local_path: Path
    # The *.mixxxlib directory
    portable_path: Path
    # Whether to perform a dry run
    dry_run: bool
