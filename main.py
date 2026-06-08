from pathlib import Path

from cli.args import parse_args
from domain.configurations import SUPPORTED_EXTENSIONS
from domain.exceptions import LinxException, report_linx_error
from matching.word_matcher import build_match_pattern, match_word_in_file
from readers.factory import ReaderFactory
from traversal.file_traverser import FileTraverser

UNLIMITED_DEPTH: None = None


def _scan_file(file_path: str, pattern) -> None:
    """Scan a single file and print a match message when found.

    Args:
        file_path: Absolute path to the file to scan.
        pattern: Compiled search pattern.

    Raises:
        LinxException: If the file cannot be read or scanned.
    """
    extension = Path(file_path).suffix
    reader = ReaderFactory.create(extension, file_path)
    try:
        if match_word_in_file(reader, pattern):
            print(f"Match found: {file_path}")
    finally:
        try:
            reader.close()
        except LinxException as exc:
            report_linx_error(exc)


def main() -> None:
    """Scan files for a sensitive word and print paths where a match is found.

    Parses CLI arguments, traverses the target path for supported file types,
    and prints a line for each file that contains the word. File-level failures
    are reported and skipped so the scan continues.

    Returns:
        None. Matching file paths are written to stdout.
    """
    try:
        root_path, sensitive_word = parse_args()
        pattern = build_match_pattern(sensitive_word)

        traverser = FileTraverser(
            initial_path=root_path,
            max_depth=UNLIMITED_DEPTH,
            supported_extensions=SUPPORTED_EXTENSIONS,
        )

        while (file_path := traverser.get_next_valid_file()) is not None:
            try:
                _scan_file(file_path, pattern)
            except LinxException as exc:
                report_linx_error(exc)
    except SystemExit:
        raise
    except LinxException as exc:
        report_linx_error(exc)
    except Exception as exc:
        report_linx_error(LinxException.wrap("main", {}, exc))


if __name__ == "__main__":
    main()
