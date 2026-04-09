"""Tests for report generation."""

import json
from pathlib import Path

from cross_ref_scanner.languages.base import Symbol
from cross_ref_scanner.scanner import ScanResult
from cross_ref_scanner.report import generate_report


def _make_result(source: Path) -> ScanResult:
    return ScanResult(
        used=[
            Symbol(name="UsedClass", file_path=source / "UsedClass.java", kind="class"),
        ],
        unused=[
            Symbol(name="DeadClass", file_path=source / "DeadClass.java", kind="class"),
            Symbol(name="OldHelper", file_path=source / "OldHelper.java", kind="class"),
        ],
    )


def test_console_format(tmp_path):
    result = _make_result(tmp_path)
    report = generate_report(result, tmp_path, "console")

    assert "1 used" in report
    assert "2 unused" in report
    assert "DeadClass" in report
    assert "OldHelper" in report


def test_json_format(tmp_path):
    result = _make_result(tmp_path)
    report = generate_report(result, tmp_path, "json")

    data = json.loads(report)
    assert data["summary"]["used"] == 1
    assert data["summary"]["unused"] == 2
    assert len(data["unused"]) == 2


def test_csv_format(tmp_path):
    result = _make_result(tmp_path)
    report = generate_report(result, tmp_path, "csv")

    lines = report.strip().splitlines()
    assert lines[0] == "name,kind,status,path"
    assert "DeadClass" in lines[1]
    assert "unused" in lines[1]


def test_write_to_file(tmp_path):
    result = _make_result(tmp_path)
    output = tmp_path / "out.json"
    generate_report(result, tmp_path, "json", str(output))

    assert output.exists()
    data = json.loads(output.read_text())
    assert data["summary"]["total"] == 3
