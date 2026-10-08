import re

import fitz

from deskreject.checks.base import Context, register_check
from deskreject.config import settings
from deskreject.models import BBox, Finding, ParsedDoc, Preset, Severity
from deskreject.vision.pool import VisionJob
from deskreject.vision.prompts import ANONYMITY_PROMPT
from deskreject.vision.schemas import ANONYMITY_SCHEMA


def get_area(bbox: BBox) -> float:
    return (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])


def is_inside(inner: BBox, outer: BBox) -> bool:
    """Check if inner bbox center is inside outer bbox."""
    cx = (inner[0] + inner[2]) / 2
    cy = (inner[1] + inner[3]) / 2
    return (outer[0] <= cx <= outer[2]) and (outer[1] <= cy <= outer[3])


@register_check
def check_anonymity_vision(doc: ParsedDoc, preset: Preset, ctx: Context) -> list[Finding]:
    if not preset.anonymous or not ctx.vision:
        return []

    candidates = []

    # 1. Figure regions
    for fig in doc.figures:
        candidates.append({
            "page": fig.page,
            "bbox": fig.region,
            "area": get_area(fig.region),
            "id": fig.id,
        })

    # 2. ImageRefs >= 40x40 pt not inside a figure region
    for img in doc.images:
        w = img.bbox[2] - img.bbox[0]
        h = img.bbox[3] - img.bbox[1]
        if w >= 40 and h >= 40:
            # Check if inside any figure region on the same page
            inside_fig = False
            for fig in doc.figures:
                if fig.page == img.page and is_inside(img.bbox, fig.region):
                    inside_fig = True
                    break
            
            if not inside_fig:
                candidates.append({
                    "page": img.page,
                    "bbox": img.bbox,
                    "area": get_area(img.bbox),
                    "id": f"Image (page {img.page})",
                })

    # Sort by area descending and cap
    candidates.sort(key=lambda c: c["area"], reverse=True)
    candidates = candidates[:settings.vision_max_crops]

    if not candidates:
        return []

    # Render crops
    jobs = []
    pdf = None
    if candidates:
        pdf = fitz.open(doc.path)

    for i, c in enumerate(candidates):
        page = pdf.load_page(c["page"] - 1)
        # 150 dpi means zoom factor 150/72
        mat = fitz.Matrix(150 / 72, 150 / 72)
        pix = page.get_pixmap(matrix=mat, clip=fitz.Rect(c["bbox"]))
        img_bytes = pix.tobytes("png")
        
        job = VisionJob(
            image_png=img_bytes,
            prompt=ANONYMITY_PROMPT,
            schema_dict=ANONYMITY_SCHEMA,
            tag=str(i),
        )
        jobs.append((job, c))

    if pdf:
        pdf.close()

    if not jobs:
        return []

    # Submit batch
    job_list = [j[0] for j in jobs]
    results = ctx.vision.ask_many(job_list)

    findings = []
    vision_failed = False
    
    text_pattern = re.compile(
        r"(University|Institute|Laboratory|Lab\b|College|Inc\.|Ltd|GmbH|"
        r"[\w\.-]+@[\w\.-]+\.\w+|https?://\S+|www\.\S+)",
        re.IGNORECASE
    )
    
    bad_kinds = {"logo", "crest", "badge", "watermark"}

    for res, (_, c) in zip(results, jobs):
        if not res.ok:
            vision_failed = True
            continue
            
        data = res.data or {}
        if not data.get("found"):
            continue
            
        items = data.get("items", [])
        for item in items:
            conf = item.get("confidence", 0.0)
            if conf < 0.6:
                continue
                
            kind = item.get("kind", "")
            text = item.get("text") or ""
            desc = item.get("description", "")
            
            is_bad = False
            if kind in bad_kinds or text_pattern.search(text):
                is_bad = True
                
            if is_bad:
                findings.append(Finding(
                    code="ANON_LOGO_IN_FIGURE",
                    check="anonymity",
                    severity=Severity.fatal,
                    title="Identifying visual element in figure",
                    detail="A visual element or text in an image could identify the authors or institution.",
                    page=c["page"],
                    bbox=c["bbox"],
                    evidence=desc,
                    source="vision",
                    confidence=conf,
                    figure_id=c["id"] if c["id"].startswith("Figure") else None,
                ))

    if vision_failed:
        findings.append(Finding(
            code="SYS_VISION_UNAVAILABLE",
            check="system",
            severity=Severity.info,
            title="Vision check unavailable",
            detail="One or more vision API calls failed.",
            source="system",
        ))

    return findings
