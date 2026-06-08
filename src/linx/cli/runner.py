from pathlib import Path

from linx.cli.args import parse_args
from linx.domain.extensions import SUPPORTED_EXTENSIONS
from linx.matching.word_matcher import build_match_pattern, match_word_in_file
from linx.readers.factory import ReaderFactory
from linx.traversal.file_traverser import FileTraverser

UNLIMITED_DEPTH: None = None


def main() -> None:
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
