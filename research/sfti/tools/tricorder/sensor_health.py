"""Read-only sensor health summaries shared by TRICORDER and SENTINEL."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable


def summarize_sensor_health(
    observations: Iterable[dict[str, Any]],
    *,
    now: datetime | None = None,
    stale_after_seconds: float = 300.0,
) -> dict[str, dict[str, Any]]:
    """Summarize latest known state per sensor; thresholds are advisory only."""
    if stale_after_seconds < 0:
        raise ValueError("stale_after_seconds must be non-negative")
    reference = now or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    latest: dict[str, dict[str, Any]] = {}
    for item in observations:
        sensor_id = item.get("sensor_id")
        if not isinstance(sensor_id, str) or not sensor_id:
            continue
        current = latest.get(sensor_id)
        if current is None or item.get("observed_at", "") > current.get("observed_at", ""):
            latest[sensor_id] = item

    summary: dict[str, dict[str, Any]] = {}
    for sensor_id, item in latest.items():
        timestamp = datetime.fromisoformat(item["observed_at"].replace("Z", "+00:00"))
        age = max(0.0, (reference - timestamp).total_seconds())
        source_status = item.get("quality_status", "sensor_fault")
        if source_status == "sensor_fault":
            health_status = "sensor_fault"
        elif source_status == "out_of_range":
            health_status = "out_of_range"
        elif source_status == "uncalibrated":
            health_status = "uncalibrated"
        elif source_status == "stale" or age > stale_after_seconds:
            health_status = "stale"
        else:
            health_status = "online"
        summary[sensor_id] = {
            "health_status": health_status,
            "last_observed_at": item["observed_at"],
            "age_seconds": round(age, 3),
            "measurement": item.get("measurement"),
            "unit": item.get("unit"),
            "value": item.get("value"),
        }
    return summary
