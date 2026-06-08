from abc import ABC, abstractmethod


class StreamingLineReader(ABC):
    def read_line(self) -> str | None:
        return self._fetch_next_line()

    @abstractmethod
    def _fetch_next_line(self) -> str | None: ...

    @abstractmethod
    def close(self) -> None: ...
