from dataclasses import dataclass

@dataclass
class Options:
    # Whether to skip tracks that are not in any of the defined collection folders
    skip_uncategorized: bool = True
    # Whether to log output during the copy.
    log: bool = False
