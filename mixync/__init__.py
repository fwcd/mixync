import argparse
import sys

from pathlib import Path

from mixync.options import Options, ResourceType
from mixync.store import Store
from mixync.store.debug import DebugStore
from mixync.store.mixxx import MixxxStore
from mixync.store.portable import PortableStore

STORES = [
    DebugStore,
    MixxxStore,
    PortableStore,
]

RESOURCE_TYPES = {
    'tracks': ResourceType.TRACK,
    'directories': ResourceType.DIRECTORY,
    'playlists': ResourceType.PLAYLIST,
    'crates': ResourceType.CRATE,
}

def parse_ref(ref: str) -> Store:
    for store_cls in STORES:
        store = store_cls.parse_ref(ref)
        if store:
            return store

    print(f"Could not parse ref '{ref}'!")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(prog='mixync', description='Tool for copying Mixxx databases with tracks in a portable manner')
    parser.add_argument('source', help='The source ref (to be copied from)')
    parser.add_argument('dest', help='The destination ref (to be copied to)')
    parser.add_argument('-r', '--dest-root-dir', type=str, help='A root folder to place copied music directories in. Only used by some destination stores.')
    parser.add_argument('-f', '--filter', default='', help=f"Comma-separated list of resource types to filter (all by default, supported types: {', '.join(sorted(RESOURCE_TYPES.keys()))}).")
    parser.add_argument('-d', '--filter-dirs', default='', help='Comma-separated list of directory names to filter.')
    parser.add_argument('-y', '--assume-yes', action='store_true', help='Whether to disable interactive prompts.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Whether to log verbosely.')
    parser.add_argument('--dry-run', action='store_true', help='Whether to skip all actual file changes.')

    args = parser.parse_args()

    if args.source == args.dest:
        print('Source and destination identical, doing nothing.')
        sys.exit(0)

    source = parse_ref(args.source)
    dest = parse_ref(args.dest)
    opts = Options(
        log=True,
        verbose=args.verbose,
        dry_run=args.dry_run,
        assume_yes=args.assume_yes,
        dest_root_dir=Path(args.dest_root_dir) if args.dest_root_dir else None,
        filter={t for t in [RESOURCE_TYPES.get(t, None) for t in args.filter.split(',')] if t},
        filter_dirs={d.strip() for d in args.filter_dirs.split(',')}
    )

    source.copy_to(dest, opts=opts)
