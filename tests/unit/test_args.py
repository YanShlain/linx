import os
import sys

import pytest

from cli.args import parse_args

TEST_FOLDER = os.path.join(os.path.dirname(__file__), "..", "..", "test_folder")


def test_tp_1_1_valid_file_path(tmp_path, monkeypatch):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello", encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "--path", str(file_path), "--regex", "goat"],
    )
    path, word = parse_args(["--path", str(file_path), "--regex", "goat"])
    assert path == os.path.abspath(str(file_path))
    assert word == "goat"


def test_tp_1_2_valid_directory_path(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "--path", TEST_FOLDER, "--regex", "goat"],
    )
    path, word = parse_args(["--path", TEST_FOLDER, "--regex", "goat"])
    assert path == os.path.abspath(TEST_FOLDER)
    assert word == "goat"


def test_tp_1_3_missing_path_exits(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "--path", "/nonexistent/path", "--regex", "goat"],
    )
    with pytest.raises(SystemExit) as exc_info:
        parse_args(
            ["--path", "/nonexistent/path/that/does/not/exist", "--regex", "goat"]
        )
    assert exc_info.value.code == 1


def test_tp_1_4_missing_args_exits():
    with pytest.raises(SystemExit) as exc_info:
        parse_args([])
    assert exc_info.value.code != 0
