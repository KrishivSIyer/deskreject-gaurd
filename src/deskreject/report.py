from deskreject.models import Report


def finalize(findings, preset, file_name, page_count, timings, vision_stats, external_requests_blocked) -> Report:
    return Report(
        preset=preset,
        file_name=file_name,
        page_count=page_count,
        findings=findings,
        risk="LOW",
        counts={"fatal": 0, "warning": 0, "info": 0},
        timings=timings,
        vision_stats=vision_stats,
        external_requests_blocked=external_requests_blocked
    )
