import argparse

from mixync.options import Options
from mixync.store import Store
from mixync.store.local import LocalStore
from mixync.store.portable import PortableStore

STORES = [
    LocalStore,
    PortableStore,
]

def parse_ref(ref: str) -> Store:
    for store_cls in STORES:
        store = store_cls.parse_ref(ref)
        if store:
            return store

    print(f"Could not parse ref '{ref}'!")
    exit(1)

def main():
    parser = argparse.ArgumentParser(description='Tool for copying Mixxx databases with tracks in a portable manner')
    parser.add_argument('source', help='The source ref (to be copied from)')
    parser.add_argument('dest', help='The destination ref (to be copied to)')

    args = parser.parse_args()

    if args.source == args.dest:
        print('Source and destination identical, doing nothing.')
        exit(0)

    source = parse_ref(args.source)
    dest = parse_ref(args.dest)
    opts = Options(
        log=True
    )

    source.copy_to(dest, opts=opts)
