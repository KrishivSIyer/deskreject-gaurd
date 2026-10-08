from deskreject.models import Finding, Report


def finalize(
    findings: list[Finding],
    preset: str,
    file_name: str,
    page_count: int,
    timings: dict[str, float],
    vision_stats: dict,
    external_requests_blocked: int,
    patches: list | None = None
) -> Report:
    seen = set()
    unique_findings = []
    for f in findings:
        bbox_tuple = tuple(f.bbox) if f.bbox else None
        key = (f.code, f.page, bbox_tuple, f.evidence)
        if key not in seen:
            seen.add(key)
            unique_findings.append(f)

    severity_order = {"fatal": 0, "warning": 1, "info": 2}

    def sort_key(f: Finding) -> tuple[int, int, float]:
        y = f.bbox[1] if f.bbox else 0.0
        return (severity_order.get(f.severity.value, 3), f.page or 0, y)

    sorted_findings = sorted(unique_findings, key=sort_key)

    counts = {"fatal": 0, "warning": 0, "info": 0}
    num = 1
    for f in sorted_findings:
        if f.bbox and f.page:
            f.number = num
            num += 1
        else:
            f.number = None
        counts[f.severity.value] += 1

    risk = "LOW"
    if counts["fatal"] > 0:
        risk = "HIGH"
    elif counts["warning"] > 0:
        risk = "MEDIUM"

    return Report(
        preset=preset,
        file_name=file_name,
        page_count=page_count,
        findings=sorted_findings,
        risk=risk,
        counts=counts,
        timings=timings,
        vision_stats=vision_stats,
        external_requests_blocked=external_requests_blocked,
        patches=patches or []
    )
