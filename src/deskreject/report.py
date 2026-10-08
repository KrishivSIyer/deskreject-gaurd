from typing import Any

from deskreject.models import Finding, Report


def finalize(findings: list[Finding], preset_id: str, file_name: str, page_count: int, timings: dict[str, float], vision_stats: dict[str, Any], external_requests_blocked: int) -> Report:
    """Stub for report finalization."""
    return Report(
        preset=preset_id,
        file_name=file_name,
        page_count=page_count,
        findings=findings,
        risk="LOW",
        counts={"fatal": 0, "warning": 0, "info": 0},
        timings=timings,
        vision_stats=vision_stats,
        external_requests_blocked=external_requests_blocked,
    )
