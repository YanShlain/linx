import argparse
import os
import sys

from domain.exceptions import LinxException


def parse_args(argv: list[str] | None = None) -> tuple[str, str]:
    """Parse and validate command-line arguments for the scanner.

    Args:
        argv: Optional argument list. When ``None``, uses ``sys.argv``.

    Returns:
        A tuple of ``(absolute_path, search_term)`` where ``absolute_path`` is the
        resolved scan target and ``search_term`` is the value passed to ``--regex``.

    Raises:
        SystemExit: If the path does not exist or required arguments are missing.
        LinxException: If argument parsing fails unexpectedly.
    """
    try:
        parser = argparse.ArgumentParser(
            description="Scan files for a sensitive word with exact case-insensitive matching.",
        )
        parser.add_argument(
            "--path",
            required=True,
            help="Full path to a file or directory to scan",
        )
        parser.add_argument(
            "--regex",
            required=True,
            help="Sensitive word to search for (matched as a whole word, case-insensitive)",
        )

        args = parser.parse_args(argv)

        abs_path = os.path.abspath(args.path)
        if not os.path.exists(abs_path):
            print(f"Error: path does not exist: {args.path}", file=sys.stderr)
            sys.exit(1)

        return abs_path, args.regex
    except SystemExit:
        raise
    except Exception as exc:
        raise LinxException.wrap("parse_args", {"argv": argv}, exc) from exc
