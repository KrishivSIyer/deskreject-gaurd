import time
from pathlib import Path

from deskreject.models import ParsedDoc, Report
from deskreject.netguard import blocked_count
from deskreject.report import finalize


def parse_stub(pdf_path: Path) -> ParsedDoc:
    """Stub for PDF parsing."""
    # This will be replaced by actual parse.py in T1.1
    from deskreject.models import FrontMatter
    return ParsedDoc(
        path=str(pdf_path),
        page_sizes=[(612.0, 792.0)],
        metadata={},
        body_font_size=10.0,
        two_column=False,
        blocks=[],
        spans=[],
        images=[],
        links=[],
        headings=[],
        captions=[],
        figures=[],
        mentions=[],
        front_matter=FrontMatter(title="Stub", author_blocks=[], abstract_start=None),
        references_start=None,
    )

def audit(pdf_path: str | Path, preset_id: str, tex_text: str | None = None, use_cache: bool = True) -> Report:
    """Run the audit pipeline."""
    t0 = time.time()
    pdf_path = Path(pdf_path)
    
    # Stub parse
    doc = parse_stub(pdf_path)
    
    # Findings stub
    findings = []
    
    t1 = time.time()
    timings = {"parse": t1 - t0, "checks": 0.0, "total": t1 - t0}
    vision_stats = {"calls": 0, "cache_hits": 0, "failures": 0, "per_endpoint": {}}
    
    return finalize(
        findings=findings,
        preset_id=preset_id,
        file_name=pdf_path.name,
        page_count=len(doc.page_sizes),
        timings=timings,
        vision_stats=vision_stats,
        external_requests_blocked=blocked_count()
    )
