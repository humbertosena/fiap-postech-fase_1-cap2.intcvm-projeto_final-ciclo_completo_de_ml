from __future__ import annotations

from pathlib import Path

from src.serving.model_store import ApprovedModelUnavailableError, load_approved_model


def test_load_approved_model_reads_manifest(
    approved_manifest_files: tuple[Path, Path, Path],
) -> None:
    manifest_path, model_path, monitoring_reference_path = approved_manifest_files

    loaded = load_approved_model(manifest_path)

    assert loaded.run_id == "run-approved-123"
    assert loaded.run_label == "20260326T010000Z"
    assert loaded.model_name == "logistic_regression"
    assert loaded.model_path == model_path
    assert loaded.decision_threshold == 0.35
    assert loaded.monitoring_reference_path == monitoring_reference_path



def test_load_approved_model_raises_when_manifest_missing(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.json"

    try:
        load_approved_model(missing_path)
    except ApprovedModelUnavailableError as exc:
        assert "Approved model manifest not found" in str(exc)
    else:
        raise AssertionError("Expected ApprovedModelUnavailableError")
