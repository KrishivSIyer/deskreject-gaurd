from pathlib import Path

import pytest
from PIL import Image

from deskreject.checks.base import Context
from deskreject.checks.legibility import check_legibility
from deskreject.models import Figure, ImageRef, LegibilityPreset, ParsedDoc, Preset, Span


@pytest.fixture
def fake_doc_legibility(tmp_path: Path):
    import fitz
    pdf_path = tmp_path / "test.pdf"
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    
    # Insert a low res image
    img = Image.new("RGB", (100, 100), color="blue")
    img_path = tmp_path / "img.png"
    img.save(img_path)
    page.insert_image(fitz.Rect(100, 100, 300, 300), filename=str(img_path))
    
    doc.save(str(pdf_path))
    doc.close()
    
    # 200 pt = 2.77 in. 100 px / 2.77 in = 36 dpi
    return ParsedDoc(
        path=str(pdf_path),
        page_sizes=[(612, 792)],
        metadata={},
        body_font_size=10,
        two_column=False,
        blocks=[],
        spans=[],
        images=[
            ImageRef(page=1, bbox=(100, 100, 300, 300), px_w=100, px_h=100, xref=1)
        ],
        links=[],
        headings=[],
        captions=[],
        figures=[
            Figure(
                id="Figure 1",
                number=1,
                page=1,
                region=(100, 400, 300, 500),
                caption={"kind": "figure", "number": 1, "page": 1, "bbox": (100, 510, 200, 520), "text": "test"},
                spans=[
                    Span(page=1, text="tiny", size=5.0, bold=False, bbox=(110, 410, 120, 420)),
                    Span(page=1, text="large", size=10.0, bold=False, bbox=(130, 410, 150, 420)),
                ]
            )
        ],
        mentions=[],
        front_matter={"title": "test", "author_blocks": [], "abstract_start": None},
        references_start=None,
    )

@pytest.fixture
def legibility_preset():
    from deskreject.models import SequencingPreset, StatementRule, StatementsPreset
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

def test_legibility_checks(fake_doc_legibility, legibility_preset):
    findings = check_legibility(fake_doc_legibility, legibility_preset, Context())
    assert len(findings) == 2
    
    dpi_finding = next(f for f in findings if f.code == "LEG_RASTER_LOW_DPI")
    assert dpi_finding.severity.value == "fatal"
    
    font_finding = next(f for f in findings if f.code == "LEG_FONT_TOO_SMALL")
    assert font_finding.severity.value == "warning"
    assert "Smallest is 5.0 pt" in font_finding.evidence
