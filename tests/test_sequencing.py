from deskreject.checks.base import Context
from deskreject.checks.sequencing import run_sequencing
from deskreject.models import Caption, FrontMatter, ParsedDoc, TextBlock
from deskreject.presets import load_preset


def make_doc(blocks_text=None, captions_data=None, references_start=None) -> ParsedDoc:
    blocks_text = blocks_text or []
    captions_data = captions_data or []  # list of tuples (kind, number)
    
    blocks = [
        TextBlock(page=1, bbox=(0, i*10, 10, i*10+10), text=t, size=10, bold=False, column=0)
        for i, t in enumerate(blocks_text)
    ]
    
    captions = [
        Caption(kind=k, number=n, page=1, bbox=(0, 100+i*10, 10, 100+i*10+10), text=f"{k.title()} {n}")
        for i, (k, n) in enumerate(captions_data)
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
        headings=[],
        captions=captions,
        figures=[],
        mentions=[],
        front_matter=FrontMatter(title="Title", author_blocks=[], abstract_start=None),
        references_start=references_start
    )

def test_sequencing_ranges_and_unresolved():
    preset = load_preset("neurips-style-double-blind")
    doc = make_doc(
        blocks_text=[
            "See Figs. 2-4 for details.",
            "Also look at Fig. 3(b).",
            "This is Table ??, oops."
        ],
        captions_data=[("figure", 2), ("figure", 3), ("figure", 4)]
    )
    # 2-4 expanded into 2, 3, 4
    # "Table ??" generates SEQ_UNRESOLVED_REF
    # Since 2,3,4 are out of order relative to 1 (which doesn't exist), we will get out of order and gap and orphan?
    # Actually wait, Fig 1 is missing, so SEQ_NUMBER_GAP for figure.
    # Figs 2, 3, 4 are mentioned before 1. So out of order? The highest seen logic: highest seen is 0, so mention of 2 before 1 triggers OUT_OF_ORDER.
    findings = run_sequencing(doc, preset, Context(vision=None))
    codes = [f.code for f in findings]
    
    assert "SEQ_UNRESOLVED_REF" in codes
    assert "SEQ_NUMBER_GAP" in codes
    assert "SEQ_OUT_OF_ORDER" in codes

def test_caption_mention_exclusion():
    preset = load_preset("neurips-style-double-blind")
    # A block that overlaps with caption should be marked in_caption and ignored by sequencing checks
    doc = make_doc(
        blocks_text=["Figure 1: This mentions Figure 2 in the caption"],
        captions_data=[("figure", 1)]
    )
    # force the block to overlap with caption 1
    doc.blocks[0].bbox = doc.captions[0].bbox
    
    findings = run_sequencing(doc, preset, Context(vision=None))
    codes = [f.code for f in findings]
    
    # Since Figure 2 is mentioned IN a caption, it shouldn't trigger SEQ_ORPHAN_REF.
    # Figure 1 has a caption but is never mentioned in the body, so it triggers SEQ_GHOST.
    assert "SEQ_ORPHAN_REF" not in codes
    assert "SEQ_GHOST" in codes

def test_bad_paper_flaws():
    preset = load_preset("neurips-style-double-blind")
    doc = make_doc(
        blocks_text=[
            "We present Figure 1.",
            "Then we jump to Figure 3.",  # out of order
            "We mention Figure 7 which doesn't exist.", # orphan ref
        ],
        captions_data=[
            ("figure", 1),
            ("figure", 3),
            ("figure", 4) # ghost
        ]
    )
    findings = run_sequencing(doc, preset, Context(vision=None))
    codes = [f.code for f in findings]
    assert "SEQ_OUT_OF_ORDER" in codes
    assert "SEQ_GHOST" in codes  # Fig 4
    assert "SEQ_ORPHAN_REF" in codes # Fig 7
    assert "SEQ_NUMBER_GAP" in codes # missing Fig 2

def test_clean_paper():
    preset = load_preset("neurips-style-double-blind")
    doc = make_doc(
        blocks_text=[
            "We present Figure 1.",
            "And here is Table 1.",
            "This is Figure 2.",
            "Finally, Table 2."
        ],
        captions_data=[
            ("figure", 1),
            ("figure", 2),
            ("table", 1),
            ("table", 2)
        ]
    )
    findings = run_sequencing(doc, preset, Context(vision=None))
    assert len(findings) == 0
