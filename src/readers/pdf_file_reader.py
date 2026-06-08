from pypdf import PdfReader

from readers.base import StreamingLineReader


class PdfFileReader(StreamingLineReader):
    def __init__(self, file_path: str) -> None:
        reader = PdfReader(file_path)
        self._lines: list[str] = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                self._lines.extend(text.splitlines())
        self._index = 0

    def _fetch_next_line(self) -> str | None:
        if self._index >= len(self._lines):
            return None
        line = self._lines[self._index]
        self._index += 1
        return line

    def close(self) -> None:
        pass
