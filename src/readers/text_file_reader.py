from readers.base import StreamingLineReader


class TextFileReader(StreamingLineReader):
    def __init__(self, file_path: str) -> None:
        self._file = open(file_path, encoding="utf-8", errors="replace")

    def _fetch_next_line(self) -> str | None:
        line = self._file.readline()
        if not line:
            return None
        return line.rstrip("\n\r")

    def close(self) -> None:
        self._file.close()
