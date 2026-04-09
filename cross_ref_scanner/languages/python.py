"""Python language adapter."""

import ast
import os
from fnmatch import fnmatch
from pathlib import Path

from cross_ref_scanner.languages.base import LanguageAdapter, Symbol


class PythonAdapter(LanguageAdapter):
    """Extracts Python class/function names and module names."""

    @property
    def name(self) -> str:
        return "Python"

    def extract_symbols(self, source_dir: Path, include: str | None = None) -> list[Symbol]:
        symbols = []
        for root, _dirs, files in os.walk(source_dir):
            for f in files:
                if not f.endswith(".py"):
                    continue
                file_path = Path(root) / f
                rel = file_path.relative_to(source_dir)

                if include and not fnmatch(str(rel), include):
                    continue

                # Skip test files by default
                if not include and (f.startswith("test_") or f.startswith("conftest")):
                    continue

                # Module name (the .py file itself, excluding __init__)
                if f != "__init__.py":
                    symbols.append(Symbol(
                        name=file_path.stem,
                        file_path=file_path,
                        kind="module",
                    ))

                # Parse top-level classes and functions
                symbols.extend(self._parse_definitions(file_path))

        return sorted(symbols, key=lambda s: s.name)

    def _parse_definitions(self, file_path: Path) -> list[Symbol]:
        """Parse top-level class and function definitions from a Python file."""
        try:
            source = file_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source, filename=str(file_path))
        except (SyntaxError, ValueError):
            return []

        symbols = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                symbols.append(Symbol(name=node.name, file_path=file_path, kind="class"))
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                # Skip private functions (starting with _)
                if not node.name.startswith("_"):
                    symbols.append(Symbol(name=node.name, file_path=file_path, kind="function"))
        return symbols

    def search_extensions(self) -> list[str]:
        return [".py", ".pyi", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".txt"]
