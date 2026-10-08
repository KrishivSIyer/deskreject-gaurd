from deskreject.checks.base import Context
from deskreject.checks.figure_caption import caption_panel_refs, run_figure_caption
from deskreject.models import Caption, Figure, FrontMatter, ImageRef, ParsedDoc, Span
from deskreject.presets import load_preset


def test_caption_panel_refs():
    # 4 required parser test cases
    assert caption_panel_refs("(a)") == {"a"}
    assert caption_panel_refs("(a)-(c)") == {"a", "b", "c"}
    assert caption_panel_refs("(a-c)") == {"a", "b", "c"}
    assert caption_panel_refs("(a), (b) and (d)") == {"a", "b", "d"}
    assert caption_panel_refs("(a) - (c)") == {"a", "b", "c"}

def make_doc(figures: list[Figure]) -> ParsedDoc:
    return ParsedDoc(
        path="test.pdf",
        page_sizes=[(600, 800)],
        metadata={},
        body_font_size=10.0,
        two_column=False,
        blocks=[],
        spans=[],
        images=[],
        links=[],
        headings=[],
        captions=[],
        figures=figures,
        mentions=[],
        front_matter=FrontMatter(title="Title", author_blocks=[], abstract_start=None),
        references_start=None
    )

def test_unreferenced_and_mismatch():
    preset = load_preset("neurips-style-double-blind")
    
    # Figure with (a), (b) visible, but caption says (a), (b), (c) => Missing (c)
    # Figure with (d) visible, but caption says nothing => Unreferenced (d)
    # Since caption mentions nothing for Fig 2, severity is warning for unreferenced
    fig1 = Figure(
        id="Figure 1",
        number=1,
        page=1,
        region=(0, 0, 100, 100),
        caption=Caption(kind="figure", number=1, page=1, bbox=(0, 110, 100, 120), text="Caption with (a)-(c)."),
        images=[],
        spans=[
            Span(page=1, text="(a)", size=10, bold=False, bbox=(10, 10, 20, 20)),
            Span(page=1, text="(b)", size=10, bold=False, bbox=(50, 10, 60, 20))
        ]
    )
    
    fig2 = Figure(
        id="Figure 2",
        number=2,
        page=1,
        region=(0, 200, 100, 300),
        caption=Caption(kind="figure", number=2, page=1, bbox=(0, 310, 100, 320), text="Caption without panels."),
        images=[],
        spans=[
            Span(page=1, text="(d)", size=10, bold=False, bbox=(10, 210, 20, 220))
        ]
    )

    doc = make_doc([fig1, fig2])
    findings = run_figure_caption(doc, preset, Context(vision=None))
    
    codes = [(f.code, f.figure_id, f.evidence) for f in findings]
    
    assert ("FIG_PANEL_COUNT_MISMATCH", "Figure 1", "(c)") in codes
    # FIG_PANEL_UNREFERENCED on Figure 2 with evidence (d)
    assert ("FIG_PANEL_UNREFERENCED", "Figure 2", "(d)") in codes

def test_panel_order():
    preset = load_preset("neurips-style-double-blind")
    # b is above a
    fig1 = Figure(
        id="Figure 1",
        number=1,
        page=1,
        region=(0, 0, 100, 100),
        caption=Caption(kind="figure", number=1, page=1, bbox=(0, 110, 100, 120), text="Caption with (a) and (b)."),
        images=[],
        spans=[
            Span(page=1, text="(b)", size=10, bold=False, bbox=(10, 10, 20, 20)),
            Span(page=1, text="(a)", size=10, bold=False, bbox=(10, 50, 20, 60))
        ]
    )
    doc = make_doc([fig1])
    findings = run_figure_caption(doc, preset, Context(vision=None))
    codes = [f.code for f in findings]
    
    assert "FIG_PANEL_ORDER" in codes

class FakeVisionPool:
    def read_panels(self, doc_path, page, region):
        return [{"label": "a", "confidence": 0.9, "bbox": (10, 10, 20, 20)}]

def test_vision_fallback():
    preset = load_preset("neurips-style-double-blind")
    fig1 = Figure(
        id="Figure 1",
        number=1,
        page=1,
        region=(0, 0, 100, 100),
        caption=Caption(kind="figure", number=1, page=1, bbox=(0, 110, 100, 120), text="Caption with (a) and (b)."),
        images=[ImageRef(page=1, bbox=(0,0,100,100), px_w=100, px_h=100, xref=1)],
        spans=[]
    )
    doc = make_doc([fig1])
    findings = run_figure_caption(doc, preset, Context(vision=FakeVisionPool()))
    
    # Fake vision found "a", caption has "a" and "b" -> Missing "b"
    codes = [(f.code, f.evidence) for f in findings]
    assert ("FIG_PANEL_COUNT_MISMATCH", "(b)") in codes

def test_clean_paper():
    preset = load_preset("neurips-style-double-blind")
    fig1 = Figure(
        id="Figure 1",
        number=1,
        page=1,
        region=(0, 0, 100, 100),
        caption=Caption(kind="figure", number=1, page=1, bbox=(0, 110, 100, 120), text="Caption with (a) and (b)."),
        images=[],
        spans=[
            Span(page=1, text="(a)", size=10, bold=False, bbox=(10, 10, 20, 20)),
            Span(page=1, text="(b)", size=10, bold=False, bbox=(50, 10, 60, 20))
        ]
    )
    doc = make_doc([fig1])
    findings = run_figure_caption(doc, preset, Context(vision=None))
    assert len(findings) == 0
