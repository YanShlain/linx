from typing import Protocol


class ILineReader(Protocol):
    """Protocol for objects that read file content one line at a time."""

    def read_line(self) -> str | None:
        """Read the next line from the source.

        Returns:
            The next line, or ``None`` at end of file.
        """
        ...

    def close(self) -> None:
        """Release resources held by the reader."""
        ...


class IFileTraverser(Protocol):
    """Protocol for objects that yield scannable file paths."""

    def get_next_valid_file(self) -> str | None:
        """Return the next file path eligible for scanning.

        Returns:
            Absolute path to the next valid file, or ``None`` when done.
        """
        ...
