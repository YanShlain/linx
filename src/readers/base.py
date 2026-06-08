from abc import ABC, abstractmethod


class StreamingLineReader(ABC):
    """Abstract base class for readers that stream file content line by line."""

    def read_line(self) -> str | None:
        """Read the next line from the underlying source.

        Returns:
            The next line without trailing newlines, or ``None`` at end of file.
        """
        return self._fetch_next_line()

    @abstractmethod
    def _fetch_next_line(self) -> str | None:
        """Fetch the next line from the concrete reader implementation.

        Returns:
            The next line without trailing newlines, or ``None`` at end of file.
        """
        ...

    @abstractmethod
    def close(self) -> None:
        """Release resources held by the reader."""
        ...
