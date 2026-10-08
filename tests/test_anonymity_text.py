from deskreject.checks.anonymity_text import run_anonymity_text
from deskreject.checks.base import Context
from deskreject.models import FrontMatter, Heading, LinkRef, ParsedDoc, TextBlock
from deskreject.presets import load_preset


def make_doc(
    metadata=None,
    author_text="Anonymous Authors",
    blocks_text=None,
    links=None,
    headings=None
) -> ParsedDoc:
    metadata = metadata or {}
    blocks_text = blocks_text or []
    links = links or []
    headings = headings or []
    
    blocks = [
        TextBlock(page=1, bbox=(0,0,10,10), text=t, size=10, bold=False, column=0)
        for t in blocks_text
    ]
    author_blocks = [
        TextBlock(page=1, bbox=(0,0,10,10), text=author_text, size=10, bold=False, column=0)
    ]
    
    h_objs = [
        Heading(page=1, bbox=(0,0,10,10), text=h, norm=h.lower())
        for h in headings
    ]
    
    l_objs = [
        LinkRef(page=1, bbox=(0,0,10,10), uri=u)
        for u in links
    ]

    return ParsedDoc(
        path="test.pdf",
        page_sizes=[(600, 800)],
        metadata=metadata,
        body_font_size=10.0,
        two_column=False,
        blocks=blocks,
        spans=[],
        images=[],
        links=l_objs,
        headings=h_objs,
        captions=[],
        figures=[],
        mentions=[],
        front_matter=FrontMatter(title="Title", author_blocks=author_blocks, abstract_start=None),
        references_start=None
    )

def test_anonymity_text_disabled():
    preset = load_preset("neurips-style-double-blind")
    preset.anonymous = False
    doc = make_doc(metadata={"author": "John Doe"})
    findings = run_anonymity_text(doc, preset, Context(vision=None))
    assert len(findings) == 0

def test_anon_metadata_author():
    preset = load_preset("neurips-style-double-blind")
    doc = make_doc(metadata={"author": "John Doe"})
    findings = run_anonymity_text(doc, preset, Context(vision=None))
    codes = [f.code for f in findings]
    assert "ANON_METADATA_AUTHOR" in codes

def test_anon_author_block():
    preset = load_preset("neurips-style-double-blind")
    doc = make_doc(author_text="Jane Rao")
    findings = run_anonymity_text(doc, preset, Context(vision=None))
    codes = [f.code for f in findings]
    assert "ANON_AUTHOR_BLOCK" in codes

def test_anon_email():
    preset = load_preset("neurips-style-double-blind")
    doc = make_doc(blocks_text=["Contact us at jane.rao@example.edu for info."])
    findings = run_anonymity_text(doc, preset, Context(vision=None))
    codes = [f.code for f in findings]
    assert "ANON_EMAIL" in codes

def test_anon_affiliation():
    preset = load_preset("neurips-style-double-blind")
    doc = make_doc(author_text="Example University")
    findings = run_anonymity_text(doc, preset, Context(vision=None))
    codes = [f.code for f in findings]
    assert "ANON_AFFILIATION" in codes

def test_anon_repo_url():
    preset = load_preset("neurips-style-double-blind")
    doc = make_doc(links=["https://github.com/rao-lab/deskproject"])
    findings = run_anonymity_text(doc, preset, Context(vision=None))
    codes = [f.code for f in findings]
    assert "ANON_REPO_URL" in codes

def test_anon_self_cite():
    preset = load_preset("neurips-style-double-blind")
    doc = make_doc(blocks_text=["In our previous work [3], we introduced..."])
    findings = run_anonymity_text(doc, preset, Context(vision=None))
    codes = [f.code for f in findings]
    assert "ANON_SELF_CITE" in codes

def test_anon_ack():
    preset = load_preset("neurips-style-double-blind")
    doc = make_doc(headings=["Acknowledgements"])
    findings = run_anonymity_text(doc, preset, Context(vision=None))
    codes = [f.code for f in findings]
    assert "ANON_ACK" in codes

def test_clean_paper():
    preset = load_preset("neurips-style-double-blind")
    doc = make_doc(
        metadata={"creator": "LaTeX"},
        author_text="Anonymous Authors",
        blocks_text=["This is a clean paper.", "We refer to [4]."],
        links=["https://anonymous.4open.science/r/ANON"],
        headings=["Introduction"]
    )
    findings = run_anonymity_text(doc, preset, Context(vision=None))
    assert len(findings) == 0
