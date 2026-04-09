"""Tests for YAML config loading."""

from pathlib import Path

from cross_ref_scanner.config import load_config


def test_load_config(tmp_path):
    config_file = tmp_path / "scan.yml"
    config_file.write_text("""
source:
  path: ./my-lib
  include: "src/main/java/**/*.java"
targets:
  - path: ./app1
  - path: ./app2
language: java
report:
  format: json
  output: report.json
workers: 4
""")
    # Create the directories so resolve works
    (tmp_path / "my-lib").mkdir()
    (tmp_path / "app1").mkdir()
    (tmp_path / "app2").mkdir()

    config = load_config(config_file)

    assert config.source_path == (tmp_path / "my-lib").resolve()
    assert len(config.target_paths) == 2
    assert config.language == "java"
    assert config.include == "src/main/java/**/*.java"
    assert config.report_format == "json"
    assert config.output_file == "report.json"
    assert config.workers == 4


def test_load_config_defaults(tmp_path):
    config_file = tmp_path / "scan.yml"
    config_file.write_text("""
source:
  path: ./lib
targets:
  - path: ./app
language: python
""")
    (tmp_path / "lib").mkdir()
    (tmp_path / "app").mkdir()

    config = load_config(config_file)

    assert config.report_format == "console"
    assert config.output_file is None
    assert config.workers == 8
    assert config.include is None
