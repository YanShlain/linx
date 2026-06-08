# File Scanner — Test Plan

Test plan derived from [requirements.md](requirements.md). Implementation proceeds test-by-test; each module's tests are written before or alongside its code.

## TP-1: Argparse & path validation

| ID | Case | Input | Expected |
|----|------|-------|----------|
| TP-1.1 | Valid file path | existing file + word | Returns `(abs_path, word)` |
| TP-1.2 | Valid directory path | existing dir + word | Returns `(abs_path, word)` |
| TP-1.3 | Missing path | nonexistent path | Error message to stderr, exit code 1 |
| TP-1.4 | Missing args | no arguments | Usage/help, exit code ≠ 0 |

## TP-2: Word matching (`match_word_in_file` + `build_match_pattern`)

Use `FakeLineReader` with scripted lines. Sensitive word: **`goat`**.

| ID | Lines fed to reader | Expected |
|----|---------------------|----------|
| TP-2.1 | `["Does a goat eat meat?"]` | `True` — case insensitive |
| TP-2.2 | `["GOAT is an abbreviation"]` | `True` |
| TP-2.3 | `["Riddle: You go at red"]` | `False` — `go at` |
| TP-2.4 | `["The main part of a goat's diet"]` | `False` — possessive |
| TP-2.5 | `["GOATttttt wandered"]` | `False` |
| TP-2.6 | `["Mountain Goatt mammal"]` | `False` |
| TP-2.7 | Multi-line, match on line 3 | `True`; stops reading after first match |
| TP-2.8 | Empty reader (immediate None) | `False` |

## TP-3: FileTraverser (`get_next_valid_file`)

Use temp directory fixtures.

| ID | Case | Setup | Expected order / behavior |
|----|------|-------|---------------------------|
| TP-3.1 | Single supported file | one `.txt` | Returns path once, then `None` |
| TP-3.2 | Single unsupported file | one `.exe` | Returns `None` immediately |
| TP-3.3 | Empty supported file | zero-byte `.txt` | Skipped, returns `None` |
| TP-3.4 | Nested directories | `a/b/c/file.txt` | Returns file (unlimited depth) |
| TP-3.5 | max_depth=0 | dir with nested file | Only files in root dir returned |
| TP-3.6 | max_depth=1 | root + one subdir | Files at depth 0 and 1 only |
| TP-3.7 | Extension case | `.CSV` file | Returned (case-insensitive ext) |
| TP-3.8 | Mixed tree | txt + json + exe + empty txt | Only valid non-empty supported files, DFS order |

## TP-4: ReaderFactory & TextFileReader

| ID | Case | Expected |
|----|------|----------|
| TP-4.1 | Factory `.txt` | Returns `TextFileReader` instance |
| TP-4.2 | Factory unknown ext | Raises `UnsupportedExtensionError` |
| TP-4.3 | read_line streaming | Large temp file (>1 MB); constant memory; all lines reachable |
| TP-4.4 | UTF-8 with errors | Binary noise in file; no crash (`errors="replace"`) |

## TP-5: Integration — `test_folder/` with word `goat`

| ID | File | Expected |
|----|------|----------|
| TP-5.1 | `folder1/text1.txt` | MATCH (`GOAT`) |
| TP-5.2 | `folder1/text3.txt` | MATCH (`goat` at end of line) |
| TP-5.3 | `text2.txt` | NO MATCH (`GOATttttt`) |
| TP-5.4 | `csv1.csv` | NO MATCH (`Goatt`) |
| TP-5.5 | `folder4/csv.csv` | MATCH (exact `Goat` tokens) |
| TP-5.6 | `folder2/json.json` | MATCH |
| TP-5.7 | Scan entire `test_folder/` | Prints only expected paths; no false positives |

## TP-6: End-to-end CLI (`main.py`)

| ID | Command | Expected |
|----|---------|----------|
| TP-6.1 | `python main.py test_folder goat` | Exit 0; match messages for TP-5.1/5.2/5.5/5.6 |
| TP-6.2 | `python main.py missing goat` | Error message; exit 1 |
| TP-6.3 | Single file with match | One message with full absolute path |

## TP-7: Phase 1b — docx/pdf

| ID | Case | Expected |
|----|------|----------|
| TP-7.1 | Sample `.docx` containing word | MATCH via `read_line()` |
| TP-7.2 | Sample `.pdf` containing word | MATCH via `read_line()` |
| TP-7.3 | Image-only PDF | NO MATCH (empty text) |

## Test execution order during implementation

1. Write `docs/test_plan.md` (this document).
2. TP-2 tests → implement `word_matcher`.
3. TP-3 tests → implement `FileTraverser`.
4. TP-4 tests → implement `ReaderFactory` + `TextFileReader`.
5. TP-1 tests → implement `parse_args`.
6. TP-5/TP-6 → wire `main.py` orchestrator; integration pass.
7. TP-7 after Phase 1b.
