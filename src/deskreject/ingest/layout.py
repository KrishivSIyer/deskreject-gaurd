from deskreject.models import Heading, TextBlock


def detect_two_column(blocks: list[TextBlock], page_width: float, body_font_size: float) -> bool:
    body_blocks = [b for b in blocks if abs(b.size - body_font_size) < 0.5]
    if not body_blocks:
        return False
    narrow_count = sum(1 for b in body_blocks if (b.bbox[2] - b.bbox[0]) < 0.55 * page_width)
    return (narrow_count / len(body_blocks)) >= 0.6

def assign_reading_order(blocks: list[TextBlock], two_column: bool, page_width: float) -> list[TextBlock]:
    if not two_column:
        for b in blocks:
            b.column = 0
        return sorted(blocks, key=lambda b: (b.page, b.bbox[1], b.bbox[0]))
    
    mid_x = page_width / 2
    for b in blocks:
        b_mid = (b.bbox[0] + b.bbox[2]) / 2
        b.column = 0 if b_mid < mid_x else 1
        
    return sorted(blocks, key=lambda b: (b.page, b.column, b.bbox[1], b.bbox[0]))

def find_body_font_size(blocks: list[TextBlock]) -> float:
    counts = {}
    for b in blocks:
        s = round(b.size, 1)
        counts[s] = counts.get(s, 0) + len(b.text)
    if not counts:
        return 10.0
    return max(counts.items(), key=lambda x: x[1])[0]

def extract_headings(blocks: list[TextBlock], body_font_size: float) -> list[Heading]:
    known_names = {"abstract", "introduction", "method", "results", "conclusion", "acknowledgements", "acknowledgments", "references"}
    headings = []
    for b in blocks:
        t = b.text.strip()
        norm = "".join(c.lower() for c in t if c.isalpha() or c.isspace()).strip()
        
        is_heading = False
        if any(k in norm.split() for k in known_names) and len(t) < 80 or len(t) < 80 and b.bold and (b.size >= body_font_size + 0.5):
            is_heading = True
            
        if is_heading:
            headings.append(Heading(page=b.page, bbox=b.bbox, text=t, norm=norm))
    return headings

def extract_front_matter_and_refs(blocks: list[TextBlock], headings: list[Heading]):
    abstract_heading = next((h for h in headings if h.page == 1 and "abstract" in h.norm), None)
    abstract_y = abstract_heading.bbox[1] if abstract_heading else 9999
    
    page1_above = [b for b in blocks if b.page == 1 and b.bbox[3] <= abstract_y + 2]
    
    title = ""
    author_blocks = []
    if page1_above:
        title_block = max(page1_above, key=lambda b: b.size)
        title = title_block.text.strip()
        author_blocks = [b for b in page1_above if b != title_block]
        
    refs_heading = next((h for h in headings if "references" in h.norm), None)
    refs_start = (refs_heading.page, refs_heading.bbox[1]) if refs_heading else None
    
    return title, author_blocks, abstract_y, refs_start
