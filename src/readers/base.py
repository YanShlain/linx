from abc import ABC, abstractmethod

from domain.exceptions import LinxException


class StreamingLineReader(ABC):
    """Abstract base class for readers that stream file content line by line."""

    _file_path: str

    def read_line(self) -> str | None:
        """Read the next line from the underlying source.

        Returns:
            The next line without trailing newlines, or ``None`` at end of file.

        Raises:
            LinxException: If reading the next line fails.
        """
        try:
            return self._fetch_next_line()
        except LinxException:
            raise
        except Exception as exc:
            raise LinxException.wrap(
                "StreamingLineReader.read_line",
                {"file_path": getattr(self, "_file_path", "<unknown>")},
                exc,
            ) from exc

    @abstractmethod
    def _fetch_next_line(self) -> str | None:
        """Fetch the next line from the concrete reader implementation.

        Returns:
            The next line without trailing newlines, or ``None`` at end of file.
        """
        ...

    def close(self) -> None:
        """Release resources held by the reader.

        Raises:
            LinxException: If releasing resources fails.
        """
        try:
            self._close()
        except LinxException:
            raise
        except Exception as exc:
            raise LinxException.wrap(
                "StreamingLineReader.close",
                {"file_path": getattr(self, "_file_path", "<unknown>")},
                exc,
            ) from exc

    @abstractmethod
    def _close(self) -> None:
        """Release resources held by the concrete reader."""
        ...
