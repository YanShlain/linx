import re

from domain.exceptions import LinxException
from domain.protocols import ILineReader


def build_match_pattern(sensitive_word: str) -> re.Pattern[str]:
    """Build a case-insensitive whole-word regex for the given term.

    Args:
        sensitive_word: The word to search for in file content.

    Returns:
        A compiled regular expression that matches the word as a standalone
        token (not as part of a longer alphanumeric word).

    Raises:
        LinxException: If the pattern cannot be compiled.
    """
    try:
        escaped = re.escape(sensitive_word)
        return re.compile(rf"(?i)(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9'])")
    except LinxException:
        raise
    except Exception as exc:
        raise LinxException.wrap(
            "build_match_pattern",
            {"sensitive_word": sensitive_word},
            exc,
        ) from exc


def match_word_in_file(reader: ILineReader, pattern: re.Pattern[str]) -> bool:
    """Check whether any line from a reader matches the given pattern.

    Args:
        reader: A line reader that yields file content one line at a time.
        pattern: A compiled regex produced by :func:`build_match_pattern`.

    Returns:
        ``True`` if at least one line matches the pattern; otherwise ``False``.

    Raises:
        LinxException: If reading or matching fails.
    """
    try:
        while (line := reader.read_line()) is not None:
            if pattern.search(line):
                return True
        return False
    except LinxException:
        raise
    except Exception as exc:
        raise LinxException.wrap(
            "match_word_in_file",
            {
                "file_path": getattr(reader, "_file_path", "<unknown>"),
                "pattern": pattern.pattern,
            },
            exc,
        ) from exc
