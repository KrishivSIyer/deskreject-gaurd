import os
import time

from deskreject.ingest.parse import parse_pdf


def test_parse_bad_paper():
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "samples", "bad_paper.pdf")
    
    t0 = time.time()
    doc = parse_pdf(pdf_path)
    t1 = time.time()
    
    assert (t1 - t0) < 3.0, "Parsing took too long"
    
    assert doc.metadata.get("author") == "Dr. Jane Rao"
    
    heading_norms = [h.norm for h in doc.headings]
    assert any("abstract" in h for h in heading_norms)
    assert any("introduction" in h for h in heading_norms)
    assert any("references" in h for h in heading_norms)
    
    assert len(doc.front_matter.author_blocks) > 0
    
    # 3 raster images expected in bad_paper.pdf (Fig 2, Fig 3, and maybe another placed one)
    assert len(doc.images) == 2
    
    assert doc.references_start is not None

def test_parse_clean_paper():
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "samples", "clean_paper.pdf")
    doc = parse_pdf(pdf_path)
    
    assert doc.metadata.get("author") == ""
