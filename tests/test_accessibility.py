from pathlib import Path

import pytest
from PIL import Image

from deskreject.checks.accessibility import check_accessibility
from deskreject.checks.base import Context
from deskreject.models import Figure, ParsedDoc, Preset


@pytest.fixture
def fake_doc_accessibility(tmp_path: Path):
    import fitz
    pdf_path = tmp_path / "test.pdf"
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    
    # We need a figure with red and green (protanopia indistinguishable)
    # Red: (255, 0, 0)
    # Green: (0, 255, 0)
    img = Image.new("RGB", (200, 200), color="white")
    # Draw large red and green blocks to pass 1.5% threshold
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 100, 200], fill=(229, 193, 212))    # Color 1
    draw.rectangle([100, 0, 200, 200], fill=(16, 205, 214))  # Color 2
    
    img_path = tmp_path / "img.png"
    img.save(img_path)
    page.insert_image(fitz.Rect(100, 100, 300, 300), filename=str(img_path))
    
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
        images=[],
        links=[],
        headings=[],
        captions=[],
        figures=[
            Figure(
                id="Figure 1",
                number=1,
                page=1,
                region=(100, 100, 300, 300),
                caption={"kind": "figure", "number": 1, "page": 1, "bbox": (100, 310, 200, 320), "text": "test"}
            )
        ],
        mentions=[],
        front_matter={"title": "test", "author_blocks": [], "abstract_start": None},
        references_start=None,
    )

@pytest.fixture
def preset_acc():
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

def test_accessibility_checks(fake_doc_accessibility, preset_acc):
    ctx = Context()
    findings = check_accessibility(fake_doc_accessibility, preset_acc, ctx)
    
    assert len(findings) == 1
    assert findings[0].code == "ACC_CB_INDISTINGUISHABLE"
    assert "Figure 1" in ctx.figure_previews
    assert "protanopia" in ctx.figure_previews["Figure 1"]
