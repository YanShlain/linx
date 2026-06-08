from pathlib import Path

from cli.args import parse_args
from domain.configurations import SUPPORTED_EXTENSIONS
from matching.word_matcher import build_match_pattern, match_word_in_file
from readers.factory import ReaderFactory
from traversal.file_traverser import FileTraverser

UNLIMITED_DEPTH: None = None


def main() -> None:
    """Scan files for a sensitive word and print paths where a match is found.

    Parses CLI arguments, traverses the target path for supported file types,
    and prints a line for each file that contains the word.

    Returns:
        None. Matching file paths are written to stdout.
    """
    root_path, sensitive_word = parse_args()
    pattern = build_match_pattern(sensitive_word)

    traverser = FileTraverser(
        initial_path=root_path,
        max_depth=UNLIMITED_DEPTH,
        supported_extensions=SUPPORTED_EXTENSIONS,
    )

    while (file_path := traverser.get_next_valid_file()) is not None:
        extension = Path(file_path).suffix
        reader = ReaderFactory.create(extension, file_path)
        try:
            if match_word_in_file(reader, pattern):
                print(f"Match found: {file_path}")
        finally:
            reader.close()

if __name__ == "__main__":
    main()
