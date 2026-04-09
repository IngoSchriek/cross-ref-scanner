"""Tests for the core scanner."""

from pathlib import Path

from cross_ref_scanner.languages import get_adapter
from cross_ref_scanner.scanner import scan

FIXTURES = Path(__file__).parent / "fixtures"


class TestJavaScanner:
    """Test scanning Java projects."""

    def test_finds_unused_class(self):
        adapter = get_adapter("java")
        source = FIXTURES / "source_java"
        targets = [FIXTURES / "target_app"]

        result = scan(adapter, source, targets)

        unused_names = {s.name for s in result.unused}
        used_names = {s.name for s in result.used}

        assert "UnusedHelper" in unused_names
        assert "UsedService" in used_names
        assert "SharedModel" in used_names

    def test_all_unused_when_no_targets_reference(self):
        adapter = get_adapter("java")
        source = FIXTURES / "source_java"
        targets = [FIXTURES / "empty_target"]

        result = scan(adapter, source, targets)

        assert len(result.unused) == 3
        assert len(result.used) == 0

    def test_empty_source(self, tmp_path):
        adapter = get_adapter("java")
        source = tmp_path / "empty"
        source.mkdir()

        result = scan(adapter, source, [tmp_path])

        assert result.total == 0


class TestPythonScanner:
    """Test scanning Python projects."""

    def test_finds_unused_symbols(self):
        adapter = get_adapter("python")
        source = FIXTURES / "source_py" / "mylib"
        targets = [FIXTURES / "source_py" / "app"]

        result = scan(adapter, source, targets)

        unused_names = {s.name for s in result.unused}
        used_names = {s.name for s in result.used}

        assert "UnusedUtil" in unused_names
        assert "orphan_function" in unused_names
        assert "UsedUtil" in used_names
        assert "used_function" in used_names


class TestAdapterRegistry:
    """Test language adapter loading."""

    def test_get_known_adapter(self):
        adapter = get_adapter("java")
        assert adapter.name == "Java"

    def test_get_unknown_adapter_raises(self):
        try:
            get_adapter("cobol")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "cobol" in str(e)

    def test_all_adapters_have_name_and_extensions(self):
        for lang in ["java", "python", "typescript", "kotlin"]:
            adapter = get_adapter(lang)
            assert adapter.name
            assert len(adapter.search_extensions()) > 0
