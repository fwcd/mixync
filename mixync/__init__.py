import argparse
import pathlib

def main():
    parser = argparse.ArgumentParser(description='Tool for copying Mixxx databases in a portable manner')
    parser.add_argument('src', help='The source path (should end in mixxxdb.sqlite3)')
    parser.add_argument('dest', help='The destination path (should end in mixxxdb.sqlite3 or the like)')

    args = parser.parse_args()

    src_path = pathlib.Path(args.src)
    dest_path = pathlib.Path(args.dest)

    # TODO: Copy
