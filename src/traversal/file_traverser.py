import os
from pathlib import Path


class FileTraverser:
    def __init__(
        self,
        initial_path: str,
        max_depth: int | None,
        supported_extensions: list[str],
    ) -> None:
        self._initial_path = os.path.abspath(initial_path)
        self._max_depth = max_depth
        self._supported_extensions = {ext.lower() for ext in supported_extensions}
        self._stack: list[tuple[str, int]] = []
        self._initialized = False

    def get_next_valid_file(self) -> str | None:
        if not self._initialized:
            self._initialize()
            self._initialized = True

        while self._stack:
            current_path, depth = self._stack.pop()

            if os.path.isfile(current_path):
                if self._is_valid_file(current_path):
                    return current_path
                continue

            if not os.path.isdir(current_path):
                continue

            try:
                entries = sorted(os.scandir(current_path), key=lambda e: e.name)
            except OSError:
                continue

            for entry in reversed(entries):
                if entry.is_dir(follow_symlinks=False):
                    if self._max_depth is None or depth < self._max_depth:
                        self._stack.append((entry.path, depth + 1))
                elif entry.is_file(follow_symlinks=False):
                    self._stack.append((entry.path, depth))

        return None

    def _initialize(self) -> None:
        if os.path.isfile(self._initial_path):
            if self._is_valid_file(self._initial_path):
                self._stack.append((self._initial_path, 0))
            return

        if os.path.isdir(self._initial_path):
            self._stack.append((self._initial_path, 0))
            return

    def _is_valid_file(self, file_path: str) -> bool:
        if os.path.getsize(file_path) == 0:
            return False
        extension = Path(file_path).suffix.lower()
        return extension in self._supported_extensions
