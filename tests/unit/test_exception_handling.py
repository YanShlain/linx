import os
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest

import main
from cli.args import parse_args
from domain.exceptions import LinxException, report_linx_error
from matching.word_matcher import build_match_pattern, match_word_in_file
from readers.docx_file_reader import DocxFileReader
from readers.factory import ReaderFactory, UnsupportedExtensionError
from readers.pdf_file_reader import PdfFileReader
from readers.text_file_reader import TextFileReader
from testing.fake_line_reader import FakeLineReader
from traversal.file_traverser import FileTraverser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SUPPORTED = [".txt", ".json", ".csv", ".docx", ".pdf"]
SENSITIVE_WORD = "goat"


class _BrokenReader:
    _file_path = "/broken.txt"

    def read_line(self) -> str | None:
        raise RuntimeError("read failed")

    def close(self) -> None:
        pass


# --- LinxException ---


def test_linx_exception_stores_cause():
    cause = ValueError("original")
    exc = LinxException("demo", {"key": "value"}, cause=cause)
    assert exc.cause is cause
    assert exc.operation == "demo"
    assert exc.parameters == {"key": "value"}


def test_linx_exception_wrap_creates_new_exception_with_cause():
    cause = RuntimeError("inner")
    wrapped = LinxException.wrap("outer", {"step": 1}, cause)
    assert wrapped is not cause
    assert isinstance(wrapped, LinxException)
    assert wrapped.operation == "outer"
    assert wrapped.parameters == {"step": 1}
    assert wrapped.cause is cause


def test_unsupported_extension_error_is_linx_exception():
    exc = UnsupportedExtensionError(
        "ReaderFactory.create",
        {"extension": ".exe", "file_path": "/tmp/app.exe"},
    )
    assert isinstance(exc, LinxException)
    assert exc.parameters["extension"] == ".exe"


# --- matching ---


def test_match_word_in_file_wraps_reader_failures():
    pattern = build_match_pattern(SENSITIVE_WORD)
    with pytest.raises(LinxException) as exc_info:
        match_word_in_file(_BrokenReader(), pattern)
    exc = exc_info.value
    assert exc.operation == "match_word_in_file"
    assert exc.parameters["file_path"] == "/broken.txt"
    assert isinstance(exc.cause, RuntimeError)


def test_match_word_in_file_preserves_linx_exception():
    pattern = build_match_pattern(SENSITIVE_WORD)

    class LinxReader:
        _file_path = "/tmp/a.txt"

        def read_line(self) -> str | None:
            raise LinxException("FakeLineReader.read_line", {"file_path": self._file_path})

        def close(self) -> None:
            pass

    with pytest.raises(LinxException) as exc_info:
        match_word_in_file(LinxReader(), pattern)
    assert exc_info.value.operation == "FakeLineReader.read_line"


def test_build_match_pattern_wraps_compile_failure():
    with patch("matching.word_matcher.re.compile", side_effect=RuntimeError("compile failed")):
        with pytest.raises(LinxException) as exc_info:
            build_match_pattern(SENSITIVE_WORD)
    exc = exc_info.value
    assert exc.operation == "build_match_pattern"
    assert exc.parameters["sensitive_word"] == SENSITIVE_WORD


# --- readers ---


def test_text_file_reader_read_line_wraps_io_error(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("hello", encoding="utf-8")
    reader = TextFileReader(str(file_path))
    reader._file.readline = MagicMock(side_effect=OSError("read failed"))

    with pytest.raises(LinxException) as exc_info:
        reader.read_line()

    exc = exc_info.value
    assert exc.operation == "StreamingLineReader.read_line"
    assert exc.parameters["file_path"] == str(file_path)
    assert isinstance(exc.cause, OSError)


def test_text_file_reader_close_wraps_io_error(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("hello", encoding="utf-8")
    reader = TextFileReader(str(file_path))
    reader._file.close = MagicMock(side_effect=OSError("close failed"))

    with pytest.raises(LinxException) as exc_info:
        reader.close()

    exc = exc_info.value
    assert exc.operation == "StreamingLineReader.close"
    assert exc.parameters["file_path"] == str(file_path)


def test_docx_reader_wraps_missing_file(tmp_path):
    missing = tmp_path / "missing.docx"
    with pytest.raises(LinxException) as exc_info:
        DocxFileReader(str(missing))
    exc = exc_info.value
    assert exc.operation == "DocxFileReader.__init__"
    assert exc.parameters["file_path"] == str(missing)


def test_pdf_reader_wraps_missing_file(tmp_path):
    missing = tmp_path / "missing.pdf"
    with pytest.raises(LinxException) as exc_info:
        PdfFileReader(str(missing))
    exc = exc_info.value
    assert exc.operation == "PdfFileReader.__init__"
    assert exc.parameters["file_path"] == str(missing)


def test_docx_reader_wraps_corrupt_file(tmp_path):
    corrupt = tmp_path / "corrupt.docx"
    corrupt.write_bytes(b"not-a-docx")
    with pytest.raises(LinxException) as exc_info:
        DocxFileReader(str(corrupt))
    exc = exc_info.value
    assert exc.operation == "DocxFileReader.__init__"
    assert exc.parameters["file_path"] == str(corrupt)
    assert exc.cause is not None


def test_reader_factory_create_propagates_reader_linx_exception(tmp_path):
    missing = tmp_path / "missing.txt"
    with pytest.raises(LinxException) as exc_info:
        ReaderFactory.create(".txt", str(missing))
    assert exc_info.value.operation == "TextFileReader.__init__"


def test_reader_factory_unknown_extension_includes_both_parameters():
    with pytest.raises(UnsupportedExtensionError) as exc_info:
        ReaderFactory.create(".exe", "/tmp/sample.exe")
    exc = exc_info.value
    assert exc.parameters["extension"] == ".exe"
    assert exc.parameters["file_path"] == "/tmp/sample.exe"


def test_fake_line_reader_wraps_read_errors():
    reader = FakeLineReader(["only line"])
    reader._lines = None  # type: ignore[assignment]

    with pytest.raises(LinxException) as exc_info:
        reader.read_line()

    assert exc_info.value.operation == "FakeLineReader.read_line"


# --- traversal ---


def test_file_traverser_reports_scandir_failure_and_continues(tmp_path, capsys):
    good = tmp_path / "good.txt"
    good.write_text("content", encoding="utf-8")
    blocked = tmp_path / "blocked"
    blocked.mkdir()
    (blocked / "nested.txt").write_text("nested", encoding="utf-8")

    real_scandir = os.scandir

    def scandir_side_effect(path: str):
        if os.path.basename(path) == "blocked":
            raise PermissionError("access denied")
        return real_scandir(path)

    with patch("traversal.file_traverser.os.scandir", side_effect=scandir_side_effect):
        traverser = FileTraverser(str(tmp_path), max_depth=None, supported_extensions=SUPPORTED)
        results = list(iter(traverser.get_next_valid_file, None))

    assert str(good) in results
    captured = capsys.readouterr()
    assert "blocked" in captured.err
    assert "FileTraverser.get_next_valid_file" in captured.err


def test_file_traverser_skips_file_when_getsize_fails(tmp_path, capsys):
    good = tmp_path / "good.txt"
    good.write_text("content", encoding="utf-8")
    bad = tmp_path / "bad.txt"
    bad.write_text("content", encoding="utf-8")

    real_getsize = os.path.getsize

    def getsize_side_effect(path: str) -> int:
        if os.path.basename(path) == "bad.txt":
            raise OSError("stat failed")
        return real_getsize(path)

    with patch("traversal.file_traverser.os.path.getsize", side_effect=getsize_side_effect):
        traverser = FileTraverser(str(tmp_path), max_depth=None, supported_extensions=SUPPORTED)
        results = list(iter(traverser.get_next_valid_file, None))

    assert str(good) in results
    assert str(bad) not in results
    captured = capsys.readouterr()
    assert "bad.txt" in captured.err
    assert "FileTraverser._is_valid_file" in captured.err


# --- CLI / main ---


def test_parse_args_wraps_unexpected_error():
    with patch("cli.args.os.path.exists", side_effect=RuntimeError("unexpected")):
        with pytest.raises(LinxException) as exc_info:
            parse_args(["--path", "/tmp", "--regex", "goat"])
    exc = exc_info.value
    assert exc.operation == "parse_args"
    assert exc.parameters["argv"] == ["--path", "/tmp", "--regex", "goat"]


def test_main_wraps_unexpected_exception(capsys):
    with patch.object(main, "parse_args", side_effect=RuntimeError("boom")):
        main.main()
    captured = capsys.readouterr()
    assert "main" in captured.err
    assert "boom" in captured.err


def test_main_reports_close_failure_and_completes(capsys):
    pattern = build_match_pattern(SENSITIVE_WORD)
    reader = MagicMock()
    reader.close.side_effect = LinxException(
        "StreamingLineReader.close",
        {"file_path": "/tmp/a.txt"},
        cause=OSError("close failed"),
    )

    with patch.object(main, "ReaderFactory") as factory:
        factory.create.return_value = reader
        with patch.object(main, "match_word_in_file", return_value=False):
            main._scan_file("/tmp/a.txt", pattern)

    captured = capsys.readouterr()
    assert "StreamingLineReader.close" in captured.err
    assert "/tmp/a.txt" in captured.err


def test_main_skips_unsupported_extension_during_scan(capsys, tmp_path):
    file_path = tmp_path / "app.exe"
    file_path.write_bytes(b"binary")

    traverser = MagicMock()
    traverser.get_next_valid_file.side_effect = [str(file_path), None]

    with patch.object(main, "parse_args", return_value=(str(tmp_path), SENSITIVE_WORD)):
        with patch.object(main, "FileTraverser", return_value=traverser):
            main.main()

    captured = capsys.readouterr()
    assert "ReaderFactory.create" in captured.err
    assert ".exe" in captured.err


def test_cli_skips_corrupt_docx_and_continues(tmp_path):
    good_file = tmp_path / "good.txt"
    good_file.write_text("goat", encoding="utf-8")
    bad_file = tmp_path / "bad.docx"
    bad_file.write_bytes(b"not-a-docx")

    result = subprocess.run(
        [
            sys.executable,
            "main.py",
            "--path",
            str(tmp_path),
            "--regex",
            SENSITIVE_WORD,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "bad.docx" in result.stderr
    assert "DocxFileReader.__init__" in result.stderr
    assert f"Match found: {os.path.abspath(good_file)}" in result.stdout
