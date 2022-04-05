from dataclasses import dataclass
from pathlib import Path

from mixync.store.local import LocalStore
from mixync.store.portable import PortableStore

@dataclass
class Context:
    # The local mixxxdb.sqlite3
    local_store: LocalStore
    # The portable *.mixxxlib
    portable_store: PortableStore
