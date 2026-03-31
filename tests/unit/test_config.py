from __future__ import annotations

from src.config import settings


def test_project_root_exists() -> None:
    assert settings.project_root.exists()



def test_raw_data_path_exists() -> None:
    assert settings.raw_data_path.exists()



def test_processed_data_path_parent_exists() -> None:
    assert settings.processed_data_path.parent.exists()



def test_training_artifact_dir_parent_exists() -> None:
    assert settings.training_artifact_dir.parent.exists()



def test_monitoring_artifact_dir_parent_exists() -> None:
    assert settings.monitoring_artifact_dir.parent.exists()



def test_mlflow_experiment_name_is_configured() -> None:
    assert settings.mlflow_experiment_name



def test_monitoring_experiment_name_is_configured() -> None:
    assert settings.monitoring_experiment_name
