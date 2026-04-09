"""Tests for the Java language adapter."""

from pathlib import Path

from cross_ref_scanner.languages.java import JavaAdapter

FIXTURES = Path(__file__).parent / "fixtures"


class TestJavaAdapter:

    def test_extracts_class_names(self):
        adapter = JavaAdapter()
        symbols = adapter.extract_symbols(FIXTURES / "source_java")

        names = {s.name for s in symbols}
        assert names == {"UsedService", "UnusedHelper", "SharedModel"}

    def test_all_symbols_are_class_kind(self):
        adapter = JavaAdapter()
        symbols = adapter.extract_symbols(FIXTURES / "source_java")

        for s in symbols:
            assert s.kind == "class"

    def test_include_filter(self):
        adapter = JavaAdapter()
        symbols = adapter.extract_symbols(
            FIXTURES / "source_java",
            include="src/main/java/com/example/Used*.java",
        )

        names = {s.name for s in symbols}
        assert "UsedService" in names
        assert "UnusedHelper" not in names

    def test_search_extensions(self):
        adapter = JavaAdapter()
        exts = adapter.search_extensions()

        assert ".java" in exts
        assert ".xml" in exts
        assert ".properties" in exts

    def test_empty_directory(self, tmp_path):
        adapter = JavaAdapter()
        symbols = adapter.extract_symbols(tmp_path)
        assert symbols == []
