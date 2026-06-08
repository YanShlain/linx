class FakeLineReader:
    """In-memory line reader for unit tests."""

    def __init__(self, lines: list[str]) -> None:
        """Initialize the reader with predefined lines.

        Args:
            lines: Sequence of lines to return from :meth:`read_line`.
        """
        self._lines = list(lines)
        self._index = 0
        self.read_count = 0

    def read_line(self) -> str | None:
        """Return the next predefined line.

        Returns:
            The next line from the configured list, or ``None`` when exhausted.
        """
        if self._index >= len(self._lines):
            return None
        line = self._lines[self._index]
        self._index += 1
        self.read_count += 1
        return line

    def close(self) -> None:
        """No-op close for test compatibility."""
        pass
