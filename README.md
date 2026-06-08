# Linx File Scanner

Linx is a command-line tool that scans a file or directory tree on your local filesystem for a sensitive word. It walks supported files recursively, reads their text content, and reports every file where the word appears as a whole word (case-insensitive).

Typical use cases include auditing folders for leaked credentials, policy keywords, or other terms you need to locate across mixed document types.

## What it does

Given a root path and a search term, Linx:

1. **Validates** the path exists (exits with code 1 if not).
2. **Traverses** the filesystem depth-first, skipping empty files and unsupported extensions.
3. **Reads** each file through a format-specific reader that yields text line by line.
4. **Matches** the word using an exact-word regex (see [Exact-word matching](#exact-word-matching)).
5. **Prints** `Match found: <absolute path>` for every file that contains a match.

The scan is lazy: files are discovered and read one at a time, so memory use stays bounded even on large directory trees.

## Usage

Install dependencies first:

```bash
uv sync --dev
```

Run the scanner with **uv**:

```bash
uv run main.py --path <path> --regex <word>
```

Example:

```bash
uv run main.py --path test_folder --regex goat
```

### Getting help

To print argument usage and exit:

```bash
uv run main.py --help
```

Short form:

```bash
uv run main.py -h
```

Example output:

```
usage: main.py [-h] --path PATH --regex REGEX

Scan files for a sensitive word with exact case-insensitive matching.

options:
  -h, --help     show this help message and exit
  --path PATH    Full path to a file or directory to scan
  --regex REGEX  Sensitive word to search for (matched as a whole word, case-insensitive)
```

### Arguments

| Option | Required | Description |
|--------|----------|-------------|
| `--path` | Yes | Full path to a **file** or **directory** to scan. Directories are walked recursively. |
| `--regex` | Yes | Sensitive word to search for. Treated as a **literal string** (not a custom regex). Matching is case-insensitive and exact-word only (see [Exact-word matching](#exact-word-matching)). |

**Other options:**

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show usage and exit. Does not require `--path` or `--regex`. |

When a match is found, the scanner prints:

```
Match found: <full absolute path>
```

If the path does not exist, an error is printed to stderr and the program exits with code 1.

## Supported file types

| Extension | Reader | How content is read |
|-----------|--------|---------------------|
| `.txt`, `.json`, `.csv` | `TextFileReader` | Streamed line-by-line (UTF-8, replacement on decode errors) |
| `.docx` | `DocxFileReader` | Paragraph text via `python-docx` |
| `.pdf` | `PdfFileReader` | Extracted page text via `pypdf` |

## Architecture

Root `main.py` delegates to `linx.cli.runner`, the **orchestrator** (composition root):

1. `parse_args()` — validate path and parse CLI arguments
2. `build_match_pattern()` — compile the exact-word regex once
3. `FileTraverser.get_next_valid_file()` — lazy DFS over supported, non-empty files
4. `ReaderFactory.create(ext, path)` — factory pattern for format-specific readers
5. `match_word_in_file(reader, pattern)` — delegate scan via `read_line()`

```
main.py  →  linx.cli.runner
  └── src/linx/
        ├── cli/
        │     ├── args.py        # argparse + path validation
        │     └── runner.py      # orchestrator (composition root)
        ├── domain/
        │     ├── extensions.py  # SUPPORTED_EXTENSIONS
        │     └── protocols.py   # ILineReader, IFileTraverser
        ├── traversal/
        │     └── file_traverser.py
        ├── readers/
        │     ├── base.py        # StreamingLineReader ABC
        │     ├── text_file_reader.py
        │     ├── docx_file_reader.py
        │     ├── pdf_file_reader.py
        │     └── factory.py     # ReaderFactory
        ├── matching/
        │     └── word_matcher.py
        └── testing/             # test doubles (FakeLineReader)
```

### Exact-word matching

The sensitive word is matched with a compiled regex:

```python
(?i)(?<![A-Za-z0-9]){word}(?![A-Za-z0-9'])
```

This ensures case-insensitive matching of whole words only (e.g. `goat` matches, `goat's` and `GOATttttt` do not).

## Adding a new file reader

All readers implement the same contract: yield text chunks via `read_line()` until there is nothing left (`None`), then release resources in `close()`. The matcher and orchestrator do not need to change.

### Step 1 — Allow the extension during traversal

Add the new extension to `SUPPORTED_EXTENSIONS` in `src/linx/domain/extensions.py`:

```python
SUPPORTED_EXTENSIONS: list[str] = [".txt", ".json", ".csv", ".docx", ".pdf", ".md"]
```

Without this, `FileTraverser` will skip files with that extension.

### Step 2 — Implement a reader class

Create a module under `src/linx/readers/` (e.g. `markdown_file_reader.py`) and subclass `StreamingLineReader`:

```python
from readers import StreamingLineReader


class MarkdownFileReader(StreamingLineReader):
    def __init__(self, file_path: str) -> None:
        self._file = open(file_path, encoding="utf-8", errors="replace")

    def _fetch_next_line(self) -> str | None:
        line = self._file.readline()
        if not line:
            return None
        return line.rstrip("\n\r")

    def close(self) -> None:
        self._file.close()
```

**Contract:**

- `_fetch_next_line()` — return the next text segment to search, or `None` when exhausted. Segments are usually lines, but formats like PDF/DOCX may map paragraphs or pages to “lines” as long as the matcher can scan them.
- `close()` — release handles, buffers, or temporary resources. Use a no-op (`pass`) if nothing to clean up.

For streaming text files, follow `TextFileReader`. For document formats that load in bulk, follow `DocxFileReader` (buffer internally, advance an index in `_fetch_next_line()`).

### Step 3 — Register the reader in the factory

In `src/linx/readers/factory.py`, import your class and register it:

```python
from readers import MarkdownFileReader

ReaderFactory.register(".md", MarkdownFileReader)
```

`ReaderFactory.create(extension, file_path)` looks up the extension (case-insensitive) and instantiates the registered class.

### Step 4 — Add tests (recommended)

- **Unit test** the reader in `tests/unit/` (mock or small fixture file).
- **Integration test** in `tests/integration/test_scanner.py` if the format should participate in end-to-end scans.

No changes to `main.py` are required.

## Development

### Setup

```bash
uv sync --dev
```

### Run tests

```bash
uv run pytest
```

See [docs/test_plan.md](docs/test_plan.md) for the full test matrix (TP-1 through TP-7).

### Requirements

See [docs/requirements.md](docs/requirements.md).
