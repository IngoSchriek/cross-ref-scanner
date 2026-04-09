# cross-ref-scanner

[![CI](https://github.com/ingo/cross-ref-scanner/actions/workflows/ci.yml/badge.svg)](https://github.com/ingo/cross-ref-scanner/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
Find unused symbols (classes, functions, modules) in a source project by scanning target projects for references. Supports Java, Python, TypeScript, and Kotlin.

## The Problem

You have a shared library used by multiple projects. Over time, some classes become unused by any consumer -- but they stay in the codebase because nobody knows if they're still needed. Manually checking each class across multiple projects is tedious and error-prone.

**cross-ref-scanner** automates this: it extracts every symbol from your library and searches for references across all consumer projects, reporting which symbols are dead code.

## Installation

```bash
pip install cross-ref-scanner
```

Or from source:

```bash
git clone https://github.com/ingo/cross-ref-scanner.git
cd cross-ref-scanner
pip install -e .
```

## Quick Start

```bash
# Scan a Java library against two consumer projects
cross-ref-scan --source ./my-lib --targets ./app1 ./app2 --lang java

# Scan a Python package
cross-ref-scan --source ./my-package --targets ./webapp --lang python

# Scan TypeScript exports
cross-ref-scan --source ./shared-lib --targets ./frontend ./backend --lang typescript
```

## Usage

### CLI Flags

```bash
cross-ref-scan \
  --source ./my-lib \              # Where symbols are extracted from
  --targets ./app1 ./app2 \        # Where to search for references
  --lang java \                    # Language: java, python, typescript, kotlin
  --include "src/main/java/**/*.java" \  # Optional: filter source files
  --format json \                  # Output: console (default), json, csv
  --output report.json \           # Optional: write to file
  --workers 8 \                    # Parallel workers (default: 8)
  --delete                         # Actually delete unused files (default: dry-run)
```

### YAML Config

For repeated scans, use a config file:

```yaml
# scan.yml
source:
  path: ./my-lib
  include: "src/main/java/**/*.java"

targets:
  - path: ./app1
  - path: ./app2
  - path: ./app3

language: java

report:
  format: console
  output: report.json

workers: 8
```

```bash
cross-ref-scan --config scan.yml
```

## Supported Languages

| Language   | Symbols Extracted           | Files Searched                              |
|------------|-----------------------------|---------------------------------------------|
| Java       | Class names from `.java`    | `.java`, `.xml`, `.properties`, `.yml`, ...  |
| Kotlin     | Class names from `.kt`      | `.kt`, `.java`, `.xml`, `.properties`, ...   |
| Python     | Classes, functions, modules | `.py`, `.pyi`, `.yml`, `.toml`, ...          |
| TypeScript | Exported symbols            | `.ts`, `.tsx`, `.js`, `.jsx`, `.json`, ...   |

### How It Works

1. **Extract** -- The language adapter walks the source directory and extracts symbol names (e.g., Java class names from `.java` filenames).
2. **Search** -- For each symbol, `grep -rFl` searches all target projects in parallel for any reference to that name.
3. **Report** -- Symbols not found in any target are reported as unused.

## Examples

### Java multi-module project

```bash
# Find classes in shared-objects not used by any service
cross-ref-scan \
  --source ./shared-objects \
  --targets ./service-a ./service-b ./service-c \
  --lang java \
  --include "src/main/java/**/*.java"
```

Output:
```
Source:   /home/user/project/shared-objects
Targets:  service-a, service-b, service-c
Language: Java
Mode:     dry-run (report only)

  [1/150]    USED  UserService
  [2/150]  UNUSED  LegacyHelper
  ...

======================================================================
RESULT: 120 used, 30 unused (out of 150)
======================================================================

Unused symbols:

  - LegacyHelper          src/main/java/com/example/LegacyHelper.java
  - OldConverter           src/main/java/com/example/OldConverter.java
  ...
```

### Export JSON for further processing

```bash
cross-ref-scan -s ./lib -t ./app -l java -f json -o unused.json
```

```json
{
  "summary": { "total": 150, "used": 120, "unused": 30 },
  "unused": [
    { "name": "LegacyHelper", "kind": "class", "path": "src/main/java/com/example/LegacyHelper.java" }
  ],
  "used": [ ... ]
}
```

## Adding a New Language

Create a new adapter in `cross_ref_scanner/languages/`:

```python
from cross_ref_scanner.languages.base import LanguageAdapter, Symbol

class GoAdapter(LanguageAdapter):
    @property
    def name(self) -> str:
        return "Go"

    def extract_symbols(self, source_dir, include=None):
        # Walk .go files and extract type/func names
        ...

    def search_extensions(self):
        return [".go", ".yml", ".yaml"]
```

Then register it in `cross_ref_scanner/languages/__init__.py`.

## Development

```bash
git clone https://github.com/ingo/cross-ref-scanner.git
cd cross-ref-scanner
pip install -e ".[dev]"
pytest -v
```

