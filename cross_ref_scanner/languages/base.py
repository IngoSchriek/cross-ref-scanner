"""Base class for language adapters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Symbol:
    """A symbol extracted from source code."""
    name: str
    file_path: Path
    kind: str  # "class", "function", "module", etc.

    def __str__(self) -> str:
        return f"{self.kind}:{self.name} ({self.file_path})"


class LanguageAdapter(ABC):
    """Abstract base for language-specific symbol extraction and search."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable language name."""

    @abstractmethod
    def extract_symbols(self, source_dir: Path, include: str | None = None) -> list[Symbol]:
        """Extract symbols (classes, functions, modules) from source files.

        Args:
            source_dir: Root directory to scan.
            include: Optional glob pattern to filter source files
                     (e.g. "src/main/java/**/*.java").

        Returns:
            List of Symbol objects found in the source directory.
        """

    @abstractmethod
    def search_extensions(self) -> list[str]:
        """File extensions to search for references in target projects.

        Returns:
            List of extensions including the dot (e.g. [".java", ".xml"]).
        """
