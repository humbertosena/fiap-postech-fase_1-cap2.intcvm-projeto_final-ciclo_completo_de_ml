from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.config import settings
from src.models.io import load_json, load_model
from src.models.registry import APPROVED_MODEL_NAME


class ApprovedModelUnavailableError(RuntimeError):
    pass


@dataclass(slots=True, frozen=True)
class LoadedApprovedModel:
    model: Any
    model_name: str
    run_id: str
    run_label: str
    decision_threshold: float
    model_path: Path
    manifest_path: Path
    monitoring_reference_path: Path | None = None

    @property
    def model_version(self) -> str:
        return self.run_label



def _resolve_artifact_path(
    manifest: dict[str, Any],
    *,
    absolute_key: str,
    relative_key: str,
) -> Path | None:
    relative_value = manifest.get(relative_key)
    if relative_value is not None:
        return (settings.project_root / str(relative_value)).resolve()

    absolute_value = manifest.get(absolute_key)
    if absolute_value is None:
        return None
    return Path(str(absolute_value))



def get_approved_manifest_path() -> Path:
    return settings.model_registry_dir / APPROVED_MODEL_NAME



def load_approved_model(manifest_path: Path | None = None) -> LoadedApprovedModel:
    target_manifest = manifest_path or get_approved_manifest_path()
    if not target_manifest.exists():
        raise ApprovedModelUnavailableError(
            f"Approved model manifest not found at {target_manifest}."
        )

    manifest = load_json(target_manifest)
    model_path = _resolve_artifact_path(
        manifest,
        absolute_key="model_path",
        relative_key="project_relative_model_path",
    )
    if model_path is None or not model_path.exists():
        raise ApprovedModelUnavailableError(f"Approved model artifact not found at {model_path}.")

    metadata = manifest.get("model_metadata", {})
    decision_threshold = float(
        metadata.get(
            "decision_threshold",
            manifest.get("metrics", {}).get("decision_threshold", 0.5),
        )
    )
    monitoring_reference_path = _resolve_artifact_path(
        manifest,
        absolute_key="monitoring_reference_path",
        relative_key="project_relative_monitoring_reference_path",
    )

    return LoadedApprovedModel(
        model=load_model(model_path),
        model_name=str(manifest["model_name"]),
        run_id=str(manifest["run_id"]),
        run_label=str(manifest["run_label"]),
        decision_threshold=decision_threshold,
        model_path=model_path,
        manifest_path=target_manifest,
        monitoring_reference_path=monitoring_reference_path,
    )
