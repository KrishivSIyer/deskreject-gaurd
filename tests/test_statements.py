from deskreject.checks.base import Context
from deskreject.checks.statements import run_statements
from deskreject.models import FrontMatter, Heading, ParsedDoc, TextBlock
from deskreject.presets import load_preset


def make_doc(headings_text=None, blocks_text=None) -> ParsedDoc:
    headings_text = headings_text or []
    blocks_text = blocks_text or []
    
    h_objs = [
        Heading(page=1, bbox=(0, i*10, 10, i*10+10), text=h, norm=h.lower())
        for i, h in enumerate(headings_text)
    ]
    
    blocks = [
        TextBlock(page=1, bbox=(0, i*10, 10, i*10+10), text=t, size=10, bold=False, column=0)
        for i, t in enumerate(blocks_text)
    ]

    return ParsedDoc(
        path="test.pdf",
        page_sizes=[(600, 800)],
        metadata={},
        body_font_size=10.0,
        two_column=False,
        blocks=blocks,
        spans=[],
        images=[],
        links=[],
        headings=h_objs,
        captions=[],
        figures=[],
        mentions=[],
        front_matter=FrontMatter(title="Title", author_blocks=[], abstract_start=None),
        references_start=None
    )

def test_missing_statements():
    preset = load_preset("neurips-style-double-blind")
    doc = make_doc()
    findings = run_statements(doc, preset, Context(vision=None))
    codes = [f.code for f in findings]
    assert "STMT_MISSING_DATA_AVAILABILITY" in codes
    assert "STMT_MISSING_CONFLICT_OF_INTEREST" in codes
    assert "STMT_MISSING_AI_USE" in codes

def test_found_statements():
    preset = load_preset("neurips-style-double-blind")
    doc = make_doc(
        headings_text=["Data Availability", "Conflict of Interest", "AI disclosure", "References"],
        blocks_text=["Data is available.", "No conflict.", "We used an LLM.", "Ref 1", "Ref 2"]
    )
    findings = run_statements(doc, preset, Context(vision=None))
    codes = [f.code for f in findings]
    assert "STMT_MISSING_DATA_AVAILABILITY" not in codes
    assert "STMT_MISSING_CONFLICT_OF_INTEREST" not in codes
    assert "STMT_MISSING_AI_USE" not in codes
    assert "STMT_MISPLACED_DATA_AVAILABILITY" not in codes

def test_misplaced_statements():
    preset = load_preset("neurips-style-double-blind")
    # In statements.py, finding blocks belonging to headings is tricky without exact bbox matching.
    # So we test finding it in blocks after references.
    doc = make_doc(
        headings_text=["References"],
        blocks_text=["Ref 1", "Ref 2", "Data availability statement here.", "Conflict of interest here.", "We used an LLM."]
    )
    findings = run_statements(doc, preset, Context(vision=None))
    codes = [f.code for f in findings]
    # They should be found but misplaced
    assert "STMT_MISPLACED_DATA_AVAILABILITY" in codes
    assert "STMT_MISPLACED_CONFLICT_OF_INTEREST" in codes
    assert "STMT_MISPLACED_AI_USE" in codes
