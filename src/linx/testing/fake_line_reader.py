from linx.domain.protocols import ILineReader


class FakeLineReader:
    def __init__(self, lines: list[str]) -> None:
        self._lines = list(lines)
        self._index = 0
        self.read_count = 0

    def read_line(self) -> str | None:
        if self._index >= len(self._lines):
            return None
        line = self._lines[self._index]
        self._index += 1
        self.read_count += 1
        return line

    def close(self) -> None:
        pass
