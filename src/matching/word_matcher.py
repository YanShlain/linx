import re

from domain.protocols import ILineReader


def build_match_pattern(sensitive_word: str) -> re.Pattern[str]:
    escaped = re.escape(sensitive_word)
    return re.compile(rf"(?i)(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9'])")


def match_word_in_file(reader: ILineReader, pattern: re.Pattern[str]) -> bool:
    while (line := reader.read_line()) is not None:
        if pattern.search(line):
            return True
    return False
