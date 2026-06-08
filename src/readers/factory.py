from domain.protocols import ILineReader
from readers.base import StreamingLineReader
from readers.docx_file_reader import DocxFileReader
from readers.pdf_file_reader import PdfFileReader
from readers.text_file_reader import TextFileReader


class UnsupportedExtensionError(Exception):
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
        """
        cls._registry[extension.lower()] = reader_cls

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
        """
        reader_cls = cls._registry.get(extension.lower())
        if reader_cls is None:
            raise UnsupportedExtensionError(f"Unsupported extension: {extension}")
        return reader_cls(file_path)


ReaderFactory.register(".txt", TextFileReader)
ReaderFactory.register(".json", TextFileReader)
ReaderFactory.register(".csv", TextFileReader)
ReaderFactory.register(".docx", DocxFileReader)
ReaderFactory.register(".pdf", PdfFileReader)
