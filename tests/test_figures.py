import os

from deskreject.ingest.parse import parse_pdf
from deskreject.ingest.render import render_region


def test_figures_and_render():
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "samples", "bad_paper.pdf")
    doc = parse_pdf(pdf_path)

    # 5 figure captions and 1 table caption
    # Find number of figures and tables in doc.captions
    figures = [c for c in doc.captions if c.kind == "figure"]
    tables = [c for c in doc.captions if c.kind == "table"]

    assert len(figures) == 5
    assert len(tables) == 1

    # Figure 3 contains the placed PNG (so images count >= 1)
    fig3 = next(f for f in doc.figures if f.id == "Figure 3")
    assert len(fig3.images) >= 1

    # Figure 1 contains at least 4 single-letter label spans
    fig1 = next(f for f in doc.figures if f.id == "Figure 1")
    single_letters = [s for s in fig1.spans if len(s.text.strip()) == 1]
    assert len(single_letters) >= 4

    # render_region returns valid PNG bytes
    png_bytes = render_region(pdf_path, fig1.page, fig1.region)
    assert png_bytes.startswith(b"\x89PNG")
