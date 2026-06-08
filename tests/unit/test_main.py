from unittest.mock import MagicMock, patch

import main
from domain.exceptions import LinxException


def test_main_skips_file_read_error_and_continues(capsys):
    traverser = MagicMock()
    traverser.get_next_valid_file.side_effect = [
        "/tmp/good.txt",
        "/tmp/bad.txt",
        None,
    ]

    def scan_side_effect(file_path: str, pattern) -> None:
        if file_path == "/tmp/bad.txt":
            raise LinxException(
                "TextFileReader.__init__",
                {"file_path": file_path},
                cause=OSError("Permission denied"),
            )
        print(f"Match found: {file_path}")

    with patch.object(main, "parse_args", return_value=("/tmp", "goat")):
        with patch.object(main, "FileTraverser", return_value=traverser):
            with patch.object(main, "_scan_file", side_effect=scan_side_effect):
                main.main()

    captured = capsys.readouterr()
    assert "Match found: /tmp/good.txt" in captured.out
    assert "bad.txt" in captured.err
    assert "TextFileReader.__init__" in captured.err


def test_main_reports_top_level_linx_exception(capsys):
    with patch.object(main, "parse_args", side_effect=LinxException("parse_args", {"argv": None})):
        main.main()

    captured = capsys.readouterr()
    assert "parse_args" in captured.err
