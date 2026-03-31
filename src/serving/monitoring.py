from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from src.monitoring.contracts import ApiMonitoringEvent, InferenceMonitoringEvent
from src.monitoring.store import append_jsonl, get_api_events_path, get_inference_events_path


def utc_now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")



def generate_request_id() -> str:
    return str(uuid4())



def record_api_event(event: ApiMonitoringEvent) -> None:
    append_jsonl(get_api_events_path(), event.to_dict())



def record_inference_event(event: InferenceMonitoringEvent) -> None:
    append_jsonl(get_inference_events_path(), event.to_dict())
