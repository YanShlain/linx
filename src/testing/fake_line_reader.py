from domain.exceptions import LinxException


class FakeLineReader:
    """In-memory line reader for unit tests."""

    def __init__(self, lines: list[str]) -> None:
        """Initialize the reader with predefined lines.

        Args:
            lines: Sequence of lines to return from :meth:`read_line`.

        Raises:
            LinxException: If initialization fails.
        """
        try:
            self._file_path = "<fake>"
            self._lines = list(lines)
            self._index = 0
            self.read_count = 0
        except LinxException:
            raise
        except Exception as exc:
            raise LinxException.wrap(
                "FakeLineReader.__init__",
                {"lines": lines},
                exc,
            ) from exc

    def read_line(self) -> str | None:
        """Return the next predefined line.

        Returns:
            The next line from the configured list, or ``None`` when exhausted.

        Raises:
            LinxException: If reading the next line fails.
        """
        try:
            if self._index >= len(self._lines):
                return None
            line = self._lines[self._index]
            self._index += 1
            self.read_count += 1
            return line
        except LinxException:
            raise
        except Exception as exc:
            raise LinxException.wrap(
                "FakeLineReader.read_line",
                {"file_path": self._file_path},
                exc,
            ) from exc

    def close(self) -> None:
        """No-op close for test compatibility.

        Raises:
            LinxException: If close fails unexpectedly.
        """
        try:
            pass
        except LinxException:
            raise
        except Exception as exc:
            raise LinxException.wrap(
                "FakeLineReader.close",
                {"file_path": self._file_path},
                exc,
            ) from exc
