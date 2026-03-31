from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from src.config import settings
from src.data.schema import (
    CATEGORICAL_COLUMNS,
    EXPECTED_TOKEN_COUNT,
    NUMERIC_COLUMNS,
    PROCESSED_COLUMNS,
    RAW_COLUMNS,
    TARGET_NEGATIVE_LABEL,
    TARGET_POSITIVE_LABEL,
)


def _normalize_token(token: str) -> str | None:
    value = token.strip()
    if value == "?":
        return None
    return value.lower()


def _read_data_lines(source_path: Path) -> list[str]:
    lines = source_path.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.lstrip().startswith("%")]


def parse_mod_line(line: str) -> dict[str, str | None]:
    tokens = line.split()
    if len(tokens) != EXPECTED_TOKEN_COUNT:
        raise ValueError(
            "Expected "
            f"{EXPECTED_TOKEN_COUNT} tokens per line, found {len(tokens)} in line: {line!r}"
        )

    return {
        column: _normalize_token(token)
        for column, token in zip(RAW_COLUMNS, tokens, strict=True)
    }


def _apply_types(frame: pd.DataFrame) -> pd.DataFrame:
    typed = frame.copy()
    for column in NUMERIC_COLUMNS:
        typed[column] = pd.to_numeric(typed[column], errors="coerce")

    for column in CATEGORICAL_COLUMNS:
        typed[column] = typed[column].astype("string")

    target_map = {TARGET_NEGATIVE_LABEL: 0, TARGET_POSITIVE_LABEL: 1}
    typed["target"] = typed["diagnosis_label"].map(target_map)

    if typed["target"].isna().any():
        unknown_labels = sorted(
            set(typed.loc[typed["target"].isna(), "diagnosis_label"].dropna().tolist())
        )
        raise ValueError(f"Unknown diagnosis labels found: {unknown_labels}")

    typed["target"] = typed["target"].astype("int64")
    return typed[list(PROCESSED_COLUMNS)]


def parse_mod_file(source_path: Path) -> pd.DataFrame:
    parsed_rows = [parse_mod_line(line) for line in _read_data_lines(source_path)]
    frame = pd.DataFrame(parsed_rows, columns=list(RAW_COLUMNS))
    return _apply_types(frame)


def _compute_file_hash(source_path: Path) -> str:
    return hashlib.sha256(source_path.read_bytes()).hexdigest()


def build_ingestion_report(frame: pd.DataFrame, source_path: Path) -> dict[str, object]:
    missing_summary = {column: int(frame[column].isna().sum()) for column in frame.columns}
    return {
        "source_path": str(source_path),
        "file_hash_sha256": _compute_file_hash(source_path),
        "record_count": int(len(frame)),
        "column_count": int(len(frame.columns)),
        "missing_values_by_column": missing_summary,
        "parser_version": settings.parser_version,
        "target_definition": settings.target_definition,
    }


def write_processed_dataset(frame: pd.DataFrame, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(destination, index=False)
    return destination


def write_ingestion_report(report: dict[str, object], destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return destination


def ingest_to_artifacts(
    source_path: Path | None = None,
    processed_path: Path | None = None,
    report_path: Path | None = None,
) -> tuple[pd.DataFrame, Path, Path]:
    source = source_path or settings.raw_data_path
    processed = processed_path or settings.processed_data_path
    report_destination = report_path or settings.ingestion_report_path

    frame = parse_mod_file(source)
    report = build_ingestion_report(frame, source)
    write_processed_dataset(frame, processed)
    write_ingestion_report(report, report_destination)
    return frame, processed, report_destination


def load_processed_dataset(path: Path | None = None) -> pd.DataFrame:
    dataset_path = path or settings.processed_data_path
    return pd.read_csv(dataset_path)


def main() -> None:
    frame, processed_path, report_path = ingest_to_artifacts()
    print(
        json.dumps(
            {
                "records": len(frame),
                "processed_path": str(processed_path),
                "report_path": str(report_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
