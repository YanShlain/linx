from domain.protocols import ILineReader
from readers.base import StreamingLineReader
from readers.docx_file_reader import DocxFileReader
from readers.pdf_file_reader import PdfFileReader
from readers.text_file_reader import TextFileReader


class UnsupportedExtensionError(Exception):
    pass


class ReaderFactory:
    _registry: dict[str, type[StreamingLineReader]] = {}

    @classmethod
    def register(cls, extension: str, reader_cls: type[StreamingLineReader]) -> None:
        cls._registry[extension.lower()] = reader_cls

    @classmethod
    def create(cls, extension: str, file_path: str) -> ILineReader:
        reader_cls = cls._registry.get(extension.lower())
        if reader_cls is None:
            raise UnsupportedExtensionError(f"Unsupported extension: {extension}")
        return reader_cls(file_path)


ReaderFactory.register(".txt", TextFileReader)
ReaderFactory.register(".json", TextFileReader)
ReaderFactory.register(".csv", TextFileReader)
ReaderFactory.register(".docx", DocxFileReader)
ReaderFactory.register(".pdf", PdfFileReader)
