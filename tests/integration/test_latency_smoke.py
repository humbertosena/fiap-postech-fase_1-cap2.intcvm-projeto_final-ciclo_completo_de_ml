from __future__ import annotations

from time import perf_counter

from src.serving.app import create_app
from src.serving.model_store import LoadedApprovedModel


def test_prediction_latency_smoke(
    approved_model_bundle: LoadedApprovedModel,
    valid_prediction_payload: dict[str, object],
) -> None:
    app = create_app(model_loader=lambda: approved_model_bundle)
    client = app.test_client()

    durations_ms: list[float] = []
    for _ in range(15):
        started_at = perf_counter()
        response = client.post("/predict", json=valid_prediction_payload)
        durations_ms.append((perf_counter() - started_at) * 1000)
        assert response.status_code == 200

    p95_ms = sorted(durations_ms)[-1]
    assert p95_ms < 100.0
