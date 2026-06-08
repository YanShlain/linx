from readers.base import StreamingLineReader


class TextFileReader(StreamingLineReader):
    """Line reader for plain-text files encoded as UTF-8."""

    def __init__(self, file_path: str) -> None:
        """Open a text file for line-by-line reading.

        Args:
            file_path: Path to the text file to read.
        """
        self._file = open(file_path, encoding="utf-8", errors="replace")

    def _fetch_next_line(self) -> str | None:
        """Read the next line from the open text file.

        Returns:
            The next line without trailing newlines, or ``None`` at end of file.
        """
        line = self._file.readline()
        if not line:
            return None
        return line.rstrip("\n\r")

    def close(self) -> None:
        """Close the underlying file handle."""
        self._file.close()
