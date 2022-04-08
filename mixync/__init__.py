import argparse

from mixync.store import Store
from mixync.store.local import LocalStore
from mixync.store.portable import PortableStore

STORES = [
    LocalStore,
    PortableStore
]

def parse_ref(ref: str) -> Store:
    for store_cls in STORES:
        store = store_cls.parse(ref)
        if store:
            return store
    raise ValueError(f"Could not parse ref '{ref}'")

def main():
    parser = argparse.ArgumentParser(description='Tool for copying Mixxx databases with tracks in a portable manner')
    parser.add_argument('source', help='The source ref (to be copied from)')
    parser.add_argument('dest', help='The destination ref (to be copied to)')

    args = parser.parse_args()

    source = parse_ref(args.source)
    dest = parse_ref(args.dest)

    source.copy_to(dest)
