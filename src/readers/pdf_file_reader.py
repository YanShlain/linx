from pypdf import PdfReader

from readers.base import StreamingLineReader


class PdfFileReader(StreamingLineReader):
    """Line reader that exposes extracted PDF text as sequential lines."""

    def __init__(self, file_path: str) -> None:
        """Extract text from a PDF file into memory.

        Args:
            file_path: Path to the ``.pdf`` file to read.
        """
        reader = PdfReader(file_path)
        self._lines: list[str] = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self._lines.extend(text.splitlines())
        self._index = 0

    def _fetch_next_line(self) -> str | None:
        """Return the next extracted text line.

        Returns:
            The next line of extracted text, or ``None`` when all lines are consumed.
        """
        if self._index >= len(self._lines):
            return None
        line = self._lines[self._index]
        self._index += 1
        return line

    def close(self) -> None:
        """Release reader state. No external resources are held."""
        pass
