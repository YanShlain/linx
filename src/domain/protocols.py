from typing import Protocol


class ILineReader(Protocol):
    def read_line(self) -> str | None: ...

    def close(self) -> None: ...


class IFileTraverser(Protocol):
    def get_next_valid_file(self) -> str | None: ...
