import os
import time

from deskreject.checks.base import Context, run_all
from deskreject.ingest.parse import parse_pdf
from deskreject.models import Report
from deskreject.presets import load_preset
from deskreject.report import finalize


def audit(
    pdf_path: str, preset_id: str, tex_text: str | None = None, use_cache: bool = True
) -> Report:
    t0 = time.time()
    timings = {}

    preset = load_preset(preset_id)

    t_parse_0 = time.time()
    doc = parse_pdf(pdf_path)
    timings["parse"] = time.time() - t_parse_0

    vision_pool = None
    try:
        from deskreject.config import settings
        from deskreject.vision.pool import VisionPool

        vision_pool = VisionPool(
            endpoints=settings.ollama_vision_endpoints,
            cache_dir=settings.cache_dir,
            use_cache=use_cache
        )
    except (ImportError, NotImplementedError):
        pass

    ctx = Context(vision=vision_pool, use_cache=use_cache, tex=tex_text)

    t_checks_0 = time.time()
    findings = run_all(doc, preset, ctx)
    timings["checks"] = time.time() - t_checks_0

    patches = []
    if tex_text:
        try:
            from deskreject.patches.latex import generate_patches

            patches = generate_patches(findings, tex_text, preset)
        except (ImportError, NotImplementedError):
            pass

    page_count = len(doc.page_sizes)
    file_name = os.path.basename(pdf_path)

    vision_stats = {"calls": 0, "cache_hits": 0, "failures": 0, "per_endpoint": {}}
    if vision_pool:
        vision_stats = getattr(vision_pool, "stats", vision_stats)

    external_requests_blocked = 0  # No telemetry

    timings["total"] = time.time() - t0

    return finalize(
        findings=findings,
        preset=preset_id,
        file_name=file_name,
        page_count=page_count,
        timings=timings,
        vision_stats=vision_stats,
        external_requests_blocked=external_requests_blocked,
        patches=patches,
    )
