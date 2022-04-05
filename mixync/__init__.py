import argparse
import pathlib

COMMANDS = {
    'push': (),
    'pull': ()
}

def main():
    parser = argparse.ArgumentParser(description='Tool for copying Mixxx databases in a portable manner')

    # TODO: Figure out local path automatically
    parser.add_argument('--local', help='The path to the local mixxxdb.sqlite3.')
    parser.add_argument('command', choices=sorted(COMMANDS.keys()), help='The command to perform.')
    parser.add_argument('portable', help='The path or URL to the (possibly remote) *.mixxxlib directory (will be created if not exists).')

    args = parser.parse_args()

    command = COMMANDS[args.command]
    local_path = pathlib.Path(args.local)
    portable_path = pathlib.Path(args.portable)

    # TODO: Copy
