import argparse

from pathlib import Path

COMMANDS = {
    'push': (),
    'pull': ()
}

MIXXXDB_PATHS = [
    # Linux
    Path.home() / '.mixxx',
    # macOS
    Path.home() / 'Library' / 'Containers' / 'org.mixxx.mixxx' / 'Data' / 'Library' / 'Application Support' / 'Mixxx',
    Path.home() / 'Library' / 'Application Support' / 'Mixxx',
    # Windows
    Path.home() / 'AppData' / 'Local' / 'Mixxx',
]

def find_local_mixxxdb() -> Path:
    for path in MIXXXDB_PATHS:
        if path.is_dir():
            return path
    return None

def main():
    local_mixxxdb = find_local_mixxxdb()

    parser = argparse.ArgumentParser(description='Tool for copying Mixxx databases in a portable manner')
    parser.add_argument('--local', default=local_mixxxdb, required=local_mixxxdb == None, help='The path to the local mixxxdb.sqlite3.')
    parser.add_argument('command', choices=sorted(COMMANDS.keys()), help='The command to perform.')
    parser.add_argument('portable', help='The path or URL to the (possibly remote) *.mixxxlib directory (will be created if not exists).')

    args = parser.parse_args()

    command = COMMANDS[args.command]
    local_path = Path(args.local)
    portable_path = Path(args.portable)

    # TODO: Copy
