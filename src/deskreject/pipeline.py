from deskreject.models import Report
from deskreject.report import finalize


def audit(pdf_path: str, preset_id: str, tex_text: str | None = None, use_cache: bool = True) -> Report:
    # Stub pipeline for M0
    findings = []
    timings = {}
    vision_stats = {"calls": 0, "cache_hits": 0, "failures": 0, "per_endpoint": {}}
    external_requests_blocked = 0
    page_count = 1  # Stub
    
    return finalize(
        findings=findings,
        preset=preset_id,
        file_name=pdf_path,
        page_count=page_count,
        timings=timings,
        vision_stats=vision_stats,
        external_requests_blocked=external_requests_blocked
    )
