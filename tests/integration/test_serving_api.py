from __future__ import annotations

from pathlib import Path

from src.monitoring.store import read_jsonl
from src.serving.app import create_app
from src.serving.model_store import ApprovedModelUnavailableError, LoadedApprovedModel


def test_health_returns_model_metadata(approved_model_bundle: LoadedApprovedModel) -> None:
    app = create_app(model_loader=lambda: approved_model_bundle)
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["model_available"] is True
    assert payload["model_run_id"] == approved_model_bundle.run_id


def test_docs_route_returns_swagger_ui() -> None:
    app = create_app()
    client = app.test_client()

    response = client.get("/docs")

    assert response.status_code == 200
    assert "swagger-ui" in response.get_data(as_text=True)


def test_openapi_route_returns_spec() -> None:
    app = create_app()
    client = app.test_client()

    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["openapi"] == "3.0.3"
    assert "/predict" in payload["paths"]
    assert "/health" in payload["paths"]



def test_predict_returns_real_inference(
    approved_model_bundle: LoadedApprovedModel,
    valid_prediction_payload: dict[str, object],
) -> None:
    app = create_app(model_loader=lambda: approved_model_bundle)
    client = app.test_client()

    response = client.post("/predict", json=valid_prediction_payload)

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["response"]["prediction"] == 1
    assert payload["response"]["prediction_label"] == "sick"
    assert payload["response"]["positive_class_probability"] == 0.82
    assert payload["response"]["decision_threshold"] == 0.35
    assert payload["request_id"]



def test_predict_returns_400_for_invalid_payload(
    approved_model_bundle: LoadedApprovedModel,
) -> None:
    app = create_app(model_loader=lambda: approved_model_bundle)
    client = app.test_client()

    response = client.post("/predict", json={"input_data": {"age": 63}})

    assert response.status_code == 400
    payload = response.get_json()
    assert "Missing required input fields" in payload["error"]



def test_predict_returns_503_without_approved_model(
    valid_prediction_payload: dict[str, object],
) -> None:
    def missing_model_loader() -> LoadedApprovedModel:
        raise ApprovedModelUnavailableError("Approved model manifest not found.")

    app = create_app(model_loader=missing_model_loader)
    client = app.test_client()

    response = client.post("/predict", json=valid_prediction_payload)

    assert response.status_code == 503
    payload = response.get_json()
    assert "Approved model manifest not found" in payload["error"]



def test_predict_persists_monitoring_events(
    approved_model_bundle: LoadedApprovedModel,
    valid_prediction_payload: dict[str, object],
    monkeypatch,
    tmp_path: Path,
) -> None:
    api_events_path = tmp_path / "api_events.jsonl"
    inference_events_path = tmp_path / "inference_events.jsonl"
    monkeypatch.setattr("src.serving.monitoring.get_api_events_path", lambda: api_events_path)
    monkeypatch.setattr(
        "src.serving.monitoring.get_inference_events_path",
        lambda: inference_events_path,
    )

    app = create_app(model_loader=lambda: approved_model_bundle)
    client = app.test_client()

    response = client.post("/predict", json=valid_prediction_payload)

    assert response.status_code == 200
    api_events = read_jsonl(api_events_path)
    inference_events = read_jsonl(inference_events_path)
    assert api_events[-1]["event_type"] == "prediction_completed"
    assert inference_events[-1]["model_run_id"] == approved_model_bundle.run_id
    assert inference_events[-1]["features"]["age"] == 63.0
