import argparse

from pathlib import Path

from mixync.options import Options
from mixync.store import Store
from mixync.store.debug import DebugStore
from mixync.store.mixxx import MixxxStore
from mixync.store.portable import PortableStore

STORES = [
    DebugStore,
    MixxxStore,
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
    parser = argparse.ArgumentParser(prog='mixync', description='Tool for copying Mixxx databases with tracks in a portable manner')
    parser.add_argument('source', help='The source ref (to be copied from)')
    parser.add_argument('dest', help='The destination ref (to be copied to)')
    parser.add_argument('-d', '--dest-root-dir', type=str, help='A root folder to place copied music directories in. Only used by some destination stores.')
    parser.add_argument('-y', '--assume-yes', action='store_true', help='Will disable interactive prompts if enabled.')

    args = parser.parse_args()

    if args.source == args.dest:
        print('Source and destination identical, doing nothing.')
        exit(0)

    source = parse_ref(args.source)
    dest = parse_ref(args.dest)
    opts = Options(
        log=True,
        assume_yes=args.assume_yes,
        dest_root_dir=Path(args.dest_root_dir) if args.dest_root_dir else None
    )

    source.copy_to(dest, opts=opts)
