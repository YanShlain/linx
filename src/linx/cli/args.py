import argparse
import os
import sys


def parse_args(argv: list[str] | None = None) -> tuple[str, str]:
    parser = argparse.ArgumentParser(
        description="Scan files for a sensitive word with exact case-insensitive matching.",
    )
    parser.add_argument("path", help="Full path to a file or directory to scan")
    parser.add_argument("word", help="Sensitive word to search for")

    args = parser.parse_args(argv)

    abs_path = os.path.abspath(args.path)
    if not os.path.exists(abs_path):
        print(f"Error: path does not exist: {args.path}", file=sys.stderr)
        sys.exit(1)

    return abs_path, args.word
