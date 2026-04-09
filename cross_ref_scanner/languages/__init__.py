"""Language adapters for symbol extraction and reference searching."""

from cross_ref_scanner.languages.base import LanguageAdapter, Symbol
from cross_ref_scanner.languages.java import JavaAdapter
from cross_ref_scanner.languages.python import PythonAdapter
from cross_ref_scanner.languages.typescript import TypeScriptAdapter
from cross_ref_scanner.languages.kotlin import KotlinAdapter

ADAPTERS: dict[str, type[LanguageAdapter]] = {
    "java": JavaAdapter,
    "python": PythonAdapter,
    "typescript": TypeScriptAdapter,
    "kotlin": KotlinAdapter,
}

def get_adapter(language: str) -> LanguageAdapter:
    """Get a language adapter by name."""
    key = language.lower()
    if key not in ADAPTERS:
        available = ", ".join(sorted(ADAPTERS))
        raise ValueError(f"Unknown language '{language}'. Available: {available}")
    return ADAPTERS[key]()
