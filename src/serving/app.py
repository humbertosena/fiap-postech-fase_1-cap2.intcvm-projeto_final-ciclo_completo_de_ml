from __future__ import annotations

import time
from typing import Any, Callable

import pandas as pd
from flask import Flask, Response, jsonify, request

from src.monitoring.contracts import (
    ApiMonitoringEvent,
    InferenceMonitoringEvent,
    sanitize_features_for_monitoring,
)
from src.serving.model_store import (
    ApprovedModelUnavailableError,
    LoadedApprovedModel,
    load_approved_model,
)
from src.serving.monitoring import (
    generate_request_id,
    record_api_event,
    record_inference_event,
    utc_now_iso,
)
from src.serving.openapi import SWAGGER_UI_HTML, build_openapi_spec
from src.serving.schemas import (
    ErrorResponse,
    HealthResponse,
    PayloadValidationError,
    PredictionRequest,
    PredictionResponse,
)

LoadApprovedModelFn = Callable[[], LoadedApprovedModel]



def _build_prediction_response(
    approved_model: LoadedApprovedModel,
    prediction_request: PredictionRequest,
) -> PredictionResponse:
    model_frame = pd.DataFrame([prediction_request.to_model_payload()])
    positive_probability: float | None = None
    if hasattr(approved_model.model, "predict_proba"):
        probabilities = approved_model.model.predict_proba(model_frame)
        positive_probability = float(probabilities[0][1])
        predicted_label = int(positive_probability >= approved_model.decision_threshold)
    else:
        predicted_label = int(approved_model.model.predict(model_frame)[0])

    return PredictionResponse(
        prediction=predicted_label,
        prediction_label="sick" if predicted_label == 1 else "buff",
        positive_class_probability=positive_probability,
        decision_threshold=float(approved_model.decision_threshold),
        model_name=approved_model.model_name,
        model_run_id=approved_model.run_id,
        model_run_label=approved_model.run_label,
    )



def create_app(*, model_loader: LoadApprovedModelFn = load_approved_model) -> Flask:
    app = Flask(__name__)

    @app.get("/openapi.json")
    def openapi() -> tuple[Response, int]:
        return jsonify(build_openapi_spec()), 200

    @app.get("/docs")
    def docs() -> Response:
        return Response(SWAGGER_UI_HTML, mimetype="text/html")

    @app.get("/health")
    def health() -> tuple[dict[str, Any], int]:
        request_id = generate_request_id()
        started_at = time.perf_counter()
        try:
            approved_model = model_loader()
            response = HealthResponse(
                status="ok",
                model_available=True,
                model_name=approved_model.model_name,
                model_run_id=approved_model.run_id,
                model_run_label=approved_model.run_label,
            )
            status_code = 200
        except ApprovedModelUnavailableError:
            approved_model = None
            response = HealthResponse(
                status="degraded",
                model_available=False,
                model_name=None,
                model_run_id=None,
                model_run_label=None,
            )
            status_code = 200

        record_api_event(
            ApiMonitoringEvent(
                timestamp_utc=utc_now_iso(),
                event_type="health_checked",
                request_id=request_id,
                endpoint="/health",
                status_code=status_code,
                latency_ms=(time.perf_counter() - started_at) * 1000,
                model_name=approved_model.model_name if approved_model else None,
                model_run_id=approved_model.run_id if approved_model else None,
                model_run_label=approved_model.run_label if approved_model else None,
            )
        )
        return response.to_dict(), status_code

    @app.post("/predict")
    def predict() -> tuple[Response, int]:
        request_id = generate_request_id()
        started_at = time.perf_counter()
        payload = request.get_json(silent=True) or {}
        record_api_event(
            ApiMonitoringEvent(
                timestamp_utc=utc_now_iso(),
                event_type="request_received",
                request_id=request_id,
                endpoint="/predict",
                status_code=0,
                latency_ms=0.0,
                model_name=None,
                model_run_id=None,
                model_run_label=None,
            )
        )

        try:
            approved_model = model_loader()
        except ApprovedModelUnavailableError as exc:
            record_api_event(
                ApiMonitoringEvent(
                    timestamp_utc=utc_now_iso(),
                    event_type="model_unavailable",
                    request_id=request_id,
                    endpoint="/predict",
                    status_code=503,
                    latency_ms=(time.perf_counter() - started_at) * 1000,
                    model_name=None,
                    model_run_id=None,
                    model_run_label=None,
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )
            )
            return jsonify(ErrorResponse(error=str(exc)).to_dict()), 503

        try:
            prediction_request = PredictionRequest.from_dict(payload)
            response = _build_prediction_response(approved_model, prediction_request)
        except PayloadValidationError as exc:
            record_api_event(
                ApiMonitoringEvent(
                    timestamp_utc=utc_now_iso(),
                    event_type="prediction_failed",
                    request_id=request_id,
                    endpoint="/predict",
                    status_code=400,
                    latency_ms=(time.perf_counter() - started_at) * 1000,
                    model_name=approved_model.model_name,
                    model_run_id=approved_model.run_id,
                    model_run_label=approved_model.run_label,
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                )
            )
            return jsonify(ErrorResponse(error=str(exc)).to_dict()), 400

        latency_ms = (time.perf_counter() - started_at) * 1000
        record_api_event(
            ApiMonitoringEvent(
                timestamp_utc=utc_now_iso(),
                event_type="prediction_completed",
                request_id=request_id,
                endpoint="/predict",
                status_code=200,
                latency_ms=latency_ms,
                model_name=approved_model.model_name,
                model_run_id=approved_model.run_id,
                model_run_label=approved_model.run_label,
            )
        )
        record_inference_event(
            InferenceMonitoringEvent(
                timestamp_utc=utc_now_iso(),
                request_id=request_id,
                endpoint="/predict",
                model_name=approved_model.model_name,
                model_run_id=approved_model.run_id,
                model_run_label=approved_model.run_label,
                prediction=response.prediction,
                prediction_label=response.prediction_label,
                positive_class_probability=response.positive_class_probability,
                decision_threshold=response.decision_threshold,
                features=sanitize_features_for_monitoring(prediction_request.to_model_payload()),
            )
        )
        body = {
            "request": prediction_request.to_dict(),
            "response": response.to_dict(),
            "request_id": request_id,
        }
        return jsonify(body), 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
