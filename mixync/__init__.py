import argparse
import pathlib

def main():
    parser = argparse.ArgumentParser(description='Tool for copying Mixxx databases in a portable manner')
    parser.add_argument('src', help='The source (either a mixxxdb.sqlite3 or a *.mixxxlib)')
    parser.add_argument('dest', help='The destination (either a mixxxdb.sqlite3 or a *.mixxxlib)')

    args = parser.parse_args()

    src_path = pathlib.Path(args.src)
    dest_path = pathlib.Path(args.dest)

    # TODO: Copy
