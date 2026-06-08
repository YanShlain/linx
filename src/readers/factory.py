from domain.exceptions import LinxException
from domain.protocols import ILineReader
from readers.base import StreamingLineReader
from readers.docx_file_reader import DocxFileReader
from readers.pdf_file_reader import PdfFileReader
from readers.text_file_reader import TextFileReader


class UnsupportedExtensionError(LinxException):
    """Raised when no reader is registered for a file extension."""


class ReaderFactory:
    """Registry and factory for file readers keyed by extension."""

    _registry: dict[str, type[StreamingLineReader]] = {}

    @classmethod
    def register(cls, extension: str, reader_cls: type[StreamingLineReader]) -> None:
        """Register a reader class for a file extension.

        Args:
            extension: File extension including the leading dot (e.g. ``".txt"``).
            reader_cls: Reader class to instantiate for that extension.

        Raises:
            LinxException: If registration fails.
        """
        try:
            cls._registry[extension.lower()] = reader_cls
        except LinxException:
            raise
        except Exception as exc:
            raise LinxException.wrap(
                "ReaderFactory.register",
                {"extension": extension, "reader_cls": reader_cls.__name__},
                exc,
            ) from exc

    @classmethod
    def create(cls, extension: str, file_path: str) -> ILineReader:
        """Create a line reader for the given file.

        Args:
            extension: File extension including the leading dot.
            file_path: Path to the file to open.

        Returns:
            An :class:`~domain.protocols.ILineReader` for the file type.

        Raises:
            UnsupportedExtensionError: If ``extension`` is not registered.
            LinxException: If reader creation fails.
        """
        try:
            reader_cls = cls._registry.get(extension.lower())
            if reader_cls is None:
                raise UnsupportedExtensionError(
                    "ReaderFactory.create",
                    {"extension": extension, "file_path": file_path},
                )
            return reader_cls(file_path)
        except LinxException:
            raise
        except Exception as exc:
            raise LinxException.wrap(
                "ReaderFactory.create",
                {"extension": extension, "file_path": file_path},
                exc,
            ) from exc


ReaderFactory.register(".txt", TextFileReader)
ReaderFactory.register(".json", TextFileReader)
ReaderFactory.register(".csv", TextFileReader)
ReaderFactory.register(".docx", DocxFileReader)
ReaderFactory.register(".pdf", PdfFileReader)
