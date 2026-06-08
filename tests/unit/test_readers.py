import pytest

from domain.exceptions import LinxException, report_linx_error
from readers.factory import ReaderFactory, UnsupportedExtensionError
from readers.text_file_reader import TextFileReader


def test_tp_4_1_factory_returns_text_reader(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("hello", encoding="utf-8")
    reader = ReaderFactory.create(".txt", str(file_path))
    assert isinstance(reader, TextFileReader)
    reader.close()


def test_tp_4_2_factory_unknown_extension_raises():
    with pytest.raises(UnsupportedExtensionError) as exc_info:
        ReaderFactory.create(".exe", "/nonexistent/file.exe")
    exc = exc_info.value
    assert exc.operation == "ReaderFactory.create"
    assert exc.parameters["extension"] == ".exe"


def test_tp_4_3_read_line_streaming_large_file(tmp_path):
    file_path = tmp_path / "large.txt"
    line_count = 50_000
    with open(file_path, "w", encoding="utf-8") as f:
        for i in range(line_count):
            f.write(f"line {i}\n")

    reader = TextFileReader(str(file_path))
    count = 0
    while reader.read_line() is not None:
        count += 1
    reader.close()

    assert count == line_count


def test_tp_4_4_utf8_with_errors_no_crash(tmp_path):
    file_path = tmp_path / "noisy.txt"
    file_path.write_bytes(b"valid line\n\xff\xfe invalid\nanother line\n")

    reader = TextFileReader(str(file_path))
    lines = []
    while (line := reader.read_line()) is not None:
        lines.append(line)
    reader.close()

    assert len(lines) == 3


def test_linx_exception_includes_operation_and_parameters():
    exc = LinxException(
        "TextFileReader.__init__",
        {"file_path": "/tmp/missing.txt"},
        cause=FileNotFoundError("missing"),
    )
    message = str(exc)
    assert "TextFileReader.__init__" in message
    assert "file_path='/tmp/missing.txt'" in message
    assert "FileNotFoundError" in message


def test_linx_exception_wrap_preserves_existing_linx_exception():
    original = LinxException("inner", {"x": 1})
    wrapped = LinxException.wrap("outer", {"y": 2}, original)
    assert wrapped is original


def test_report_linx_error_writes_to_stderr(capsys):
    exc = LinxException("demo", {"value": 1})
    report_linx_error(exc)
    captured = capsys.readouterr()
    assert captured.err.startswith("Error: ")
    assert "demo" in captured.err


def test_text_file_reader_wraps_missing_file(tmp_path):
    missing = tmp_path / "missing.txt"
    with pytest.raises(LinxException) as exc_info:
        TextFileReader(str(missing))
    exc = exc_info.value
    assert exc.operation == "TextFileReader.__init__"
    assert exc.parameters["file_path"] == str(missing)
