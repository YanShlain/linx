import os
import sys

import pytest

from cli.args import parse_args

TEST_FOLDER = os.path.join(os.path.dirname(__file__), "..", "..", "test_folder")


def test_tp_1_1_valid_file_path(tmp_path, monkeypatch):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["main.py", str(file_path), "goat"])
    path, word = parse_args([str(file_path), "goat"])
    assert path == os.path.abspath(str(file_path))
    assert word == "goat"


def test_tp_1_2_valid_directory_path(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py", TEST_FOLDER, "goat"])
    path, word = parse_args([TEST_FOLDER, "goat"])
    assert path == os.path.abspath(TEST_FOLDER)
    assert word == "goat"


def test_tp_1_3_missing_path_exits(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py", "/nonexistent/path", "goat"])
    with pytest.raises(SystemExit) as exc_info:
        parse_args(["/nonexistent/path/that/does/not/exist", "goat"])
    assert exc_info.value.code == 1


def test_tp_1_4_missing_args_exits():
    with pytest.raises(SystemExit) as exc_info:
        parse_args([])
    assert exc_info.value.code != 0
