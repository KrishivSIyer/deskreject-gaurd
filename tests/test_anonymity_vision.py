from pathlib import Path

import pytest

from deskreject.checks.anonymity_vision import check_anonymity_vision
from deskreject.checks.base import Context
from deskreject.models import Figure, ImageRef, ParsedDoc, Preset
from deskreject.vision.pool import VisionJob, VisionResult


class FakeVisionPool:
    def __init__(self, responses):
        self.responses = responses

    def ask_many(self, jobs: list[VisionJob]) -> list[VisionResult]:
        results = []
        for j in jobs:
            res_data = self.responses.get(j.tag, {"found": False})
            if res_data is None:
                results.append(VisionResult(ok=False, data=None, endpoint=None, model=None, seconds=0, cached=False, error="fail"))
            else:
                results.append(VisionResult(ok=True, data=res_data, endpoint="test", model="test", seconds=0, cached=False, error=None))
        return results

@pytest.fixture
def fake_doc(tmp_path: Path):
    import fitz
    pdf_path = tmp_path / "test.pdf"
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    # Add some drawings so there's something to render
    page.draw_rect(fitz.Rect(100, 100, 200, 200), color=(1, 0, 0), fill=(1, 0, 0))
    page.draw_rect(fitz.Rect(300, 300, 400, 400), color=(0, 1, 0), fill=(0, 1, 0))
    doc.save(str(pdf_path))
    doc.close()
    
    return ParsedDoc(
        path=str(pdf_path),
        page_sizes=[(612, 792)],
        metadata={},
        body_font_size=10,
        two_column=False,
        blocks=[],
        spans=[],
        images=[
            ImageRef(page=1, bbox=(300, 300, 400, 400), px_w=100, px_h=100, xref=1)
        ],
        links=[],
        headings=[],
        captions=[],
        figures=[
            Figure(id="Figure 1", number=1, page=1, region=(100, 100, 200, 200), caption={"kind": "figure", "number": 1, "page": 1, "bbox": (100, 210, 200, 220), "text": "test"})
        ],
        mentions=[],
        front_matter={"title": "test", "author_blocks": [], "abstract_start": None},
        references_start=None,
    )

@pytest.fixture
def preset():
    from deskreject.models import (
        LegibilityPreset,
        SequencingPreset,
        StatementRule,
        StatementsPreset,
    )
    return Preset(
        id="test",
        label="Test",
        anonymous=True,
        min_figure_font_pt=6.0,
        min_raster_dpi=LegibilityPreset(line_art=300, photo=150, fatal_below=72),
        column_width_in=3.3,
        sequencing=SequencingPreset(require_in_order=True),
        statements=StatementsPreset(
            data_availability=StatementRule(required=False, position="any"),
            code_availability=StatementRule(required=False, position="any"),
            conflict_of_interest=StatementRule(required=False, position="any"),
            ethics=StatementRule(required=False, position="any"),
            ai_use=StatementRule(required=False, position="any"),
        ),
    )

def test_anonymity_vision_finds_logo(fake_doc, preset):
    pool = FakeVisionPool({
        "0": {
            "found": True,
            "items": [{"kind": "logo", "description": "A crest", "confidence": 0.9}]
        },
        "1": {
            "found": False,
        }
    })
    ctx = Context(vision=pool)
    findings = check_anonymity_vision(fake_doc, preset, ctx)
    assert len(findings) == 1
    assert findings[0].code == "ANON_LOGO_IN_FIGURE"

def test_anonymity_vision_finds_text(fake_doc, preset):
    pool = FakeVisionPool({
        "0": {
            "found": True,
            "items": [{"kind": "text", "text": "MIT Laboratory", "description": "Lab text", "confidence": 0.9}]
        },
        "1": {
            "found": False,
        }
    })
    ctx = Context(vision=pool)
    findings = check_anonymity_vision(fake_doc, preset, ctx)
    assert len(findings) == 1
    assert findings[0].code == "ANON_LOGO_IN_FIGURE"

def test_anonymity_vision_unavailable(fake_doc, preset):
    pool = FakeVisionPool({"0": None, "1": None})
    ctx = Context(vision=pool)
    findings = check_anonymity_vision(fake_doc, preset, ctx)
    assert len(findings) == 1
    assert findings[0].code == "SYS_VISION_UNAVAILABLE"
