import pymupdf


def render_region(pdf_path: str, page_num: int, bbox: tuple[float, float, float, float], dpi: int = 150) -> bytes:
    doc = pymupdf.open(pdf_path)
    page = doc[page_num - 1]
    zoom = dpi / 72.0
    mat = pymupdf.Matrix(zoom, zoom)
    clip = pymupdf.Rect(bbox)
    pix = page.get_pixmap(matrix=mat, clip=clip)
    return pix.tobytes("png")
