import re
import unicodedata

import pymupdf

from deskreject.ingest.layout import (
    assign_reading_order,
    detect_two_column,
    extract_front_matter_and_refs,
    extract_headings,
    find_body_font_size,
)
from deskreject.models import FrontMatter, ImageRef, LinkRef, ParsedDoc, Span, TextBlock


def normalize_text(text: str) -> str:
    t = unicodedata.normalize("NFKC", text)
    t = re.sub(r'-\n\s*', '', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

def parse_pdf(path: str) -> ParsedDoc:
    doc = pymupdf.open(path)
    page_sizes = []
    blocks_list = []
    spans_list = []
    images_list = []
    links_list = []
    drawings = []
    
    for page_num, page in enumerate(doc, 1):
        try:
            page_sizes.append((page.rect.width, page.rect.height))
            
            text_dict = page.get_text("dict")
            for b in text_dict.get("blocks", []):
                if b.get("type") == 0:
                    b_text = ""
                    b_size = 0
                    b_bold = False
                    for line in b.get("lines", []):
                        for span in line.get("spans", []):
                            txt = span["text"]
                            if txt.strip():
                                # Try to reconstruct spaced words or just simple concat
                                b_text += txt + " "
                                sz = span["size"]
                                bold = bool(span["flags"] & 16)
                                spans_list.append(Span(page=page_num, text=normalize_text(txt), size=sz, bold=bold, bbox=span["bbox"]))
                                if sz > b_size:
                                    b_size = sz
                                    b_bold = bold
                    b_text = normalize_text(b_text)
                    if b_text:
                        blocks_list.append(TextBlock(
                            page=page_num, bbox=b["bbox"], text=b_text, 
                            size=b_size, bold=b_bold, column=0
                        ))
            
            for img in page.get_image_info(xrefs=True):
                images_list.append(ImageRef(
                    page=page_num, bbox=img["bbox"], px_w=img["width"], px_h=img["height"], xref=img["xref"]
                ))
                
            for lnk in page.get_links():
                if lnk["kind"] == pymupdf.LINK_URI:
                    links_list.append(LinkRef(page=page_num, bbox=lnk["from"], uri=lnk["uri"]))
                    
            drawings.extend([(page_num, d) for d in page.get_drawings()])
            
        except Exception as e:  # noqa: BLE001
            import logging
            logging.getLogger(__name__).error(f"Error parsing page {page_num}: {e}")

    if not page_sizes:
        # Prevent completely empty failure
        page_sizes.append((612.0, 792.0))

    body_font_size = find_body_font_size(blocks_list)
    page_width = page_sizes[0][0]
    two_column = detect_two_column(blocks_list, page_width, body_font_size)
    blocks_list = assign_reading_order(blocks_list, two_column, page_width)
    
    headings = extract_headings(blocks_list, body_font_size)
    title, author_blocks, abstract_y, refs_start = extract_front_matter_and_refs(blocks_list, headings)
    
    front_matter = FrontMatter(
        title=title, 
        author_blocks=author_blocks, 
        abstract_start=(1, abstract_y) if abstract_y != 9999 else None
    )
    
    captions = []
    figures = []
    mentions = []
    try:
        from deskreject.ingest.figures import find_captions, find_figures
        captions = find_captions(blocks_list)
        figures = find_figures(doc, captions, images_list, spans_list, drawings)
    except (ImportError, NotImplementedError):
        pass
        
    try:
        from deskreject.ingest.mentions import find_mentions
        mentions = find_mentions(blocks_list, captions, refs_start)
    except (ImportError, NotImplementedError):
        pass

    clean_metadata = {k: str(v) if v is not None else "" for k, v in doc.metadata.items()}

    return ParsedDoc(
        path=path,
        page_sizes=page_sizes,
        metadata=clean_metadata,
        body_font_size=body_font_size,
        two_column=two_column,
        blocks=blocks_list,
        spans=spans_list,
        images=images_list,
        links=links_list,
        headings=headings,
        captions=captions,
        figures=figures,
        mentions=mentions,
        front_matter=front_matter,
        references_start=refs_start
    )
