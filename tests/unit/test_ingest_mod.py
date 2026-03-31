from __future__ import annotations

import json

from src.config import settings
from src.data.ingest_mod import build_ingestion_report, ingest_to_artifacts, parse_mod_file
from src.data.schema import PROCESSED_COLUMNS


def test_parse_mod_file_builds_expected_shape() -> None:
    frame = parse_mod_file(settings.raw_data_path)
    assert list(frame.columns) == list(PROCESSED_COLUMNS)
    assert len(frame) == 303
    assert set(frame["target"].unique()) == {0, 1}


def test_parse_mod_file_tracks_missing_values() -> None:
    frame = parse_mod_file(settings.raw_data_path)
    assert frame["num_vessels"].isna().sum() > 0
    assert frame["thal"].isna().sum() > 0


def test_ingestion_report_contains_required_fields(tmp_path) -> None:
    frame = parse_mod_file(settings.raw_data_path)
    report = build_ingestion_report(frame, settings.raw_data_path)
    report_path = tmp_path / "report.json"
    processed_path = tmp_path / "processed.csv"

    _, exported_processed_path, exported_report_path = ingest_to_artifacts(
        processed_path=processed_path,
        report_path=report_path,
    )

    assert exported_processed_path.exists()
    assert exported_report_path.exists()
    payload = json.loads(exported_report_path.read_text(encoding="utf-8"))
    assert payload["file_hash_sha256"] == report["file_hash_sha256"]
    assert payload["record_count"] == 303
