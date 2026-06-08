from docx import Document

from readers.base import StreamingLineReader


class DocxFileReader(StreamingLineReader):
    def __init__(self, file_path: str) -> None:
        document = Document(file_path)
        self._lines = [paragraph.text for paragraph in document.paragraphs]
        self._index = 0

    def _fetch_next_line(self) -> str | None:
        if self._index >= len(self._lines):
            return None
        line = self._lines[self._index]
        self._index += 1
        return line

    def close(self) -> None:
        pass
