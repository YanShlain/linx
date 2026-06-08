from docx import Document
from pypdf import PdfWriter

from matching.word_matcher import build_match_pattern, match_word_in_file
from readers.docx_file_reader import DocxFileReader
from readers.factory import ReaderFactory
from readers.pdf_file_reader import PdfFileReader

SENSITIVE_WORD = "goat"


def _create_docx(path: str, paragraphs: list[str]) -> None:
    doc = Document()
    for text in paragraphs:
        doc.add_paragraph(text)
    doc.save(path)


def _write_simple_text_pdf(path: str, text: str) -> None:
    """Minimal PDF with a text content stream."""
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    content = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET"
    content_bytes = content.encode("latin-1")
    objects = []

    def add_obj(data: bytes) -> int:
        objects.append(data)
        return len(objects)

    font_obj = add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    content_obj = add_obj(
        f"<< /Length {len(content_bytes)} >>\nstream\n".encode()
        + content_bytes
        + b"\nendstream"
    )
    page_obj = add_obj(
        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        f"/Contents {content_obj} 0 R /Resources << /Font << /F1 {font_obj} 0 R >> >> >>".encode()
    )
    pages_obj = add_obj(f"<< /Type /Pages /Kids [{page_obj} 0 R] /Count 1 >>".encode())
    catalog_obj = add_obj(f"<< /Type /Catalog /Pages {pages_obj} 0 R >>".encode())

    with open(path, "wb") as f:
        f.write(b"%PDF-1.4\n")
        offsets = [0]
        for i, obj in enumerate(objects, start=1):
            offsets.append(f.tell())
            f.write(f"{i} 0 obj\n".encode())
            f.write(obj)
            f.write(b"\nendobj\n")
        xref_pos = f.tell()
        f.write(f"xref\n0 {len(objects) + 1}\n".encode())
        f.write(b"0000000000 65535 f \n")
        for off in offsets[1:]:
            f.write(f"{off:010d} 00000 n \n".encode())
        f.write(f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_obj} 0 R >>\n".encode())
        f.write(f"startxref\n{xref_pos}\n%%EOF\n".encode())


def test_tp_7_1_docx_match(tmp_path):
    file_path = tmp_path / "sample.docx"
    _create_docx(str(file_path), ["Does a goat eat meat?", "Another line"])
    pattern = build_match_pattern(SENSITIVE_WORD)
    reader = DocxFileReader(str(file_path))
    try:
        assert match_word_in_file(reader, pattern) is True
    finally:
        reader.close()


def test_tp_7_2_pdf_match(tmp_path):
    file_path = tmp_path / "sample.pdf"
    _write_simple_text_pdf(str(file_path), "The goat wandered through the meadow.")
    pattern = build_match_pattern(SENSITIVE_WORD)
    reader = PdfFileReader(str(file_path))
    try:
        assert match_word_in_file(reader, pattern) is True
    finally:
        reader.close()


def test_tp_7_3_image_only_pdf_no_match(tmp_path):
    file_path = tmp_path / "blank.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    with open(file_path, "wb") as f:
        writer.write(f)

    pattern = build_match_pattern(SENSITIVE_WORD)
    reader = PdfFileReader(str(file_path))
    try:
        assert match_word_in_file(reader, pattern) is False
    finally:
        reader.close()


def test_factory_creates_docx_and_pdf_readers(tmp_path):
    docx_path = tmp_path / "test.docx"
    _create_docx(str(docx_path), ["hello"])
    pdf_path = tmp_path / "test.pdf"
    _write_simple_text_pdf(str(pdf_path), "hello")

    docx_reader = ReaderFactory.create(".docx", str(docx_path))
    assert isinstance(docx_reader, DocxFileReader)
    docx_reader.close()

    pdf_reader = ReaderFactory.create(".pdf", str(pdf_path))
    assert isinstance(pdf_reader, PdfFileReader)
    pdf_reader.close()
