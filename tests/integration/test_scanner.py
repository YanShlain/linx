import os
import subprocess
import sys
from pathlib import Path

from domain.configurations import SUPPORTED_EXTENSIONS
from matching.word_matcher import build_match_pattern, match_word_in_file
from readers.factory import ReaderFactory
from traversal.file_traverser import FileTraverser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEST_FOLDER = os.path.join(ROOT, "test_folder")
SENSITIVE_WORD = "goat"


def _scan_file(relative_path: str) -> bool:
    file_path = os.path.join(TEST_FOLDER, relative_path)
    pattern = build_match_pattern(SENSITIVE_WORD)
    extension = os.path.splitext(file_path)[1]
    reader = ReaderFactory.create(extension, file_path)
    try:
        return match_word_in_file(reader, pattern)
    finally:
        reader.close()


def test_tp_5_1_text1_matches():
    assert _scan_file("folder1/text1.txt") is True


def test_tp_5_2_text3_matches():
    assert _scan_file("folder1/text3.txt") is True


def test_tp_5_3_text2_no_match():
    assert _scan_file("text2.txt") is False


def test_tp_5_4_csv1_no_match():
    assert _scan_file("csv1.csv") is False


def test_tp_5_5_folder4_csv_matches():
    assert _scan_file("folder4/csv.csv") is True


def test_tp_5_6_json_matches():
    assert _scan_file("folder2/json.json") is True


def test_tp_5_7_full_scan_only_expected_matches():
    pattern = build_match_pattern(SENSITIVE_WORD)
    traverser = FileTraverser(
        initial_path=TEST_FOLDER,
        max_depth=None,
        supported_extensions=SUPPORTED_EXTENSIONS,
    )

    matched_paths = []
    while (file_path := traverser.get_next_valid_file()) is not None:
        extension = os.path.splitext(file_path)[1]
        reader = ReaderFactory.create(extension, file_path)
        try:
            if match_word_in_file(reader, pattern):
                matched_paths.append(
                    Path(file_path).relative_to(TEST_FOLDER).as_posix()
                )
        finally:
            reader.close()

    required_matches = {
        "folder1/text1.txt",
        "folder1/text3.txt",
        "folder4/csv.csv",
        "folder2/json.json",
    }
    no_match_files = {
        "text2.txt",
        "csv1.csv",
    }

    assert required_matches.issubset(set(matched_paths))
    assert no_match_files.isdisjoint(set(matched_paths))


def test_tp_6_1_cli_scan_test_folder():
    result = subprocess.run(
        [sys.executable, "main.py", TEST_FOLDER, SENSITIVE_WORD],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = result.stdout
    assert "folder1" in output and "text1.txt" in output
    assert "text3.txt" in output
    assert "folder4" in output and "csv.csv" in output
    assert "folder2" in output and "json.json" in output
    assert "text2.txt" not in output
    assert "csv1.csv" not in output


def test_tp_6_2_cli_missing_path():
    result = subprocess.run(
        [sys.executable, "main.py", "missing", SENSITIVE_WORD],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "does not exist" in result.stderr.lower() or "error" in result.stderr.lower()


def test_tp_6_3_cli_single_file_match():
    file_path = os.path.join(TEST_FOLDER, "folder1", "text1.txt")
    result = subprocess.run(
        [sys.executable, "main.py", file_path, SENSITIVE_WORD],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == f"Match found: {os.path.abspath(file_path)}"
