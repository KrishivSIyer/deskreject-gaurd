import os

import fitz
import pytest


def test_bad_paper_flaws():
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "samples", "bad_paper.pdf")
    if not os.path.exists(pdf_path):
        pytest.skip("bad_paper.pdf not generated yet")
        
    doc = fitz.open(pdf_path)
    
    # Check metadata author
    assert doc.metadata["author"] == "Dr. Jane Rao"
    
    # Check repo URL in text and 'Table ??'
    text = ""
    for page in doc:
        text += page.get_text()
        
    assert "https://github.com/rao-lab/deskproject" in text
    assert "Table ??" in text
    
    # Check Figure 1 caption lacks (d)
    assert "Figure 1. Data distributions. (a) Train set. (b) Validation set. (c) Test set." in text
    assert "(d)" not in text.split("Figure 1.")[1].split("Figure 2.")[0]

def test_clean_paper_metadata():
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "samples", "clean_paper.pdf")
    if not os.path.exists(pdf_path):
        pytest.skip("clean_paper.pdf not generated yet")
        
    doc = fitz.open(pdf_path)
    
    # Check metadata author is empty
    assert doc.metadata["author"] == ""
