import os

import pytest

from linx.readers.factory import ReaderFactory, UnsupportedExtensionError
from linx.readers.text_file_reader import TextFileReader


def test_tp_4_1_factory_returns_text_reader(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("hello", encoding="utf-8")
    reader = ReaderFactory.create(".txt", str(file_path))
    assert isinstance(reader, TextFileReader)
    reader.close()


def test_tp_4_2_factory_unknown_extension_raises():
    with pytest.raises(UnsupportedExtensionError):
        ReaderFactory.create(".exe", "/nonexistent/file.exe")


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
