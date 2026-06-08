from docx import Document

from readers.base import StreamingLineReader


class DocxFileReader(StreamingLineReader):
    """Line reader that exposes DOCX paragraph text as sequential lines."""

    def __init__(self, file_path: str) -> None:
        """Load paragraph text from a DOCX file into memory.

        Args:
            file_path: Path to the ``.docx`` file to read.
        """
        document = Document(file_path)
        self._lines = [paragraph.text for paragraph in document.paragraphs]
        self._index = 0

    def _fetch_next_line(self) -> str | None:
        """Return the next paragraph as a line.

        Returns:
            The next paragraph text, or ``None`` when all paragraphs are consumed.
        """
        if self._index >= len(self._lines):
            return None
        line = self._lines[self._index]
        self._index += 1
        return line

    def close(self) -> None:
        """Release reader state. No external resources are held."""
        pass
