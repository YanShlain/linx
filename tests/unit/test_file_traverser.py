import os

from traversal.file_traverser import FileTraverser

SUPPORTED = [".txt", ".json", ".csv", ".docx", ".pdf"]


def test_tp_3_1_single_supported_file(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("content", encoding="utf-8")
    traverser = FileTraverser(str(file_path), max_depth=None, supported_extensions=SUPPORTED)
    assert traverser.get_next_valid_file() == str(file_path)
    assert traverser.get_next_valid_file() is None


def test_tp_3_2_single_unsupported_file(tmp_path):
    file_path = tmp_path / "file.exe"
    file_path.write_bytes(b"content")
    traverser = FileTraverser(str(file_path), max_depth=None, supported_extensions=SUPPORTED)
    assert traverser.get_next_valid_file() is None


def test_tp_3_3_empty_supported_file_skipped(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_bytes(b"")
    traverser = FileTraverser(str(file_path), max_depth=None, supported_extensions=SUPPORTED)
    assert traverser.get_next_valid_file() is None


def test_tp_3_4_nested_directories(tmp_path):
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True)
    file_path = nested / "file.txt"
    file_path.write_text("content", encoding="utf-8")
    traverser = FileTraverser(str(tmp_path), max_depth=None, supported_extensions=SUPPORTED)
    assert traverser.get_next_valid_file() == str(file_path)
    assert traverser.get_next_valid_file() is None


def test_tp_3_5_max_depth_zero(tmp_path):
    root_file = tmp_path / "root.txt"
    root_file.write_text("root", encoding="utf-8")
    nested = tmp_path / "sub"
    nested.mkdir()
    nested_file = nested / "nested.txt"
    nested_file.write_text("nested", encoding="utf-8")

    traverser = FileTraverser(str(tmp_path), max_depth=0, supported_extensions=SUPPORTED)
    results = []
    while (path := traverser.get_next_valid_file()) is not None:
        results.append(path)

    assert results == [str(root_file)]


def test_tp_3_6_max_depth_one(tmp_path):
    root_file = tmp_path / "root.txt"
    root_file.write_text("root", encoding="utf-8")
    sub = tmp_path / "sub"
    sub.mkdir()
    sub_file = sub / "sub.txt"
    sub_file.write_text("sub", encoding="utf-8")
    deep = sub / "deep"
    deep.mkdir()
    deep_file = deep / "deep.txt"
    deep_file.write_text("deep", encoding="utf-8")

    traverser = FileTraverser(str(tmp_path), max_depth=1, supported_extensions=SUPPORTED)
    results = []
    while (path := traverser.get_next_valid_file()) is not None:
        results.append(os.path.basename(path))

    assert set(results) == {"root.txt", "sub.txt"}
    assert "deep.txt" not in results


def test_tp_3_7_extension_case_insensitive(tmp_path):
    file_path = tmp_path / "data.CSV"
    file_path.write_text("a,b,c", encoding="utf-8")
    traverser = FileTraverser(str(file_path), max_depth=None, supported_extensions=SUPPORTED)
    assert traverser.get_next_valid_file() == str(file_path)
    assert traverser.get_next_valid_file() is None


def test_tp_3_8_mixed_tree_dfs_order(tmp_path):
    (tmp_path / "alpha.txt").write_text("a", encoding="utf-8")
    (tmp_path / "empty.txt").write_bytes(b"")
    (tmp_path / "skip.exe").write_bytes(b"x")
    (tmp_path / "beta.json").write_text("{}", encoding="utf-8")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "gamma.txt").write_text("g", encoding="utf-8")

    traverser = FileTraverser(str(tmp_path), max_depth=None, supported_extensions=SUPPORTED)
    results = [os.path.basename(p) for p in iter(traverser.get_next_valid_file, None)]

    assert results == ["alpha.txt", "beta.json", "gamma.txt"]
