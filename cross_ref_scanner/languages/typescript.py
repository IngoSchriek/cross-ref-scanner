"""TypeScript/JavaScript language adapter."""

import os
import re
from fnmatch import fnmatch
from pathlib import Path

from cross_ref_scanner.languages.base import LanguageAdapter, Symbol

# Patterns for exported symbols
_EXPORT_PATTERNS = [
    # export class Foo / export abstract class Foo
    re.compile(r'export\s+(?:abstract\s+)?class\s+(\w+)'),
    # export interface Foo
    re.compile(r'export\s+interface\s+(\w+)'),
    # export type Foo
    re.compile(r'export\s+type\s+(\w+)'),
    # export enum Foo
    re.compile(r'export\s+enum\s+(\w+)'),
    # export function foo / export async function foo
    re.compile(r'export\s+(?:async\s+)?function\s+(\w+)'),
    # export const foo / export let foo / export var foo
    re.compile(r'export\s+(?:const|let|var)\s+(\w+)'),
    # export default class Foo
    re.compile(r'export\s+default\s+class\s+(\w+)'),
    # export default function foo
    re.compile(r'export\s+default\s+(?:async\s+)?function\s+(\w+)'),
]

_TS_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".mts", ".mjs"}


class TypeScriptAdapter(LanguageAdapter):
    """Extracts TypeScript/JavaScript exported symbols."""

    @property
    def name(self) -> str:
        return "TypeScript"

    def extract_symbols(self, source_dir: Path, include: str | None = None) -> list[Symbol]:
        symbols = []
        for root, _dirs, files in os.walk(source_dir):
            for f in files:
                if Path(f).suffix not in _TS_EXTENSIONS:
                    continue
                file_path = Path(root) / f
                rel = file_path.relative_to(source_dir)

                if include and not fnmatch(str(rel), include):
                    continue

                # Skip test files and node_modules
                str_path = str(file_path)
                if not include and ("node_modules" in str_path or ".test." in f or ".spec." in f):
                    continue

                # Module name
                symbols.append(Symbol(
                    name=file_path.stem,
                    file_path=file_path,
                    kind="module",
                ))

                # Exported symbols
                symbols.extend(self._parse_exports(file_path))

        return sorted(symbols, key=lambda s: s.name)

    def _parse_exports(self, file_path: Path) -> list[Symbol]:
        """Extract exported symbols using regex patterns."""
        try:
            source = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return []

        symbols = []
        seen = set()
        for pattern in _EXPORT_PATTERNS:
            for match in pattern.finditer(source):
                name = match.group(1)
                if name not in seen:
                    seen.add(name)
                    kind = "class" if "class" in pattern.pattern else "function"
                    symbols.append(Symbol(name=name, file_path=file_path, kind=kind))
        return symbols

    def search_extensions(self) -> list[str]:
        return [".ts", ".tsx", ".js", ".jsx", ".mts", ".mjs", ".json", ".yml", ".yaml", ".html"]
