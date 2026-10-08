"""Overlay rendering and visual highlighting for DeskReject Guard page viewer."""

from typing import Any

import pymupdf
from PIL import Image, ImageDraw, ImageFont

SEVERITY_COLORS = {
    "fatal": {
        "stroke": (239, 68, 68, 255),       # #ef4444
        "fill": (239, 68, 68, 45),          # #ef4444 semi-transparent
        "badge_bg": (239, 68, 68, 240),
        "badge_text": (255, 255, 255, 255),
    },
    "warning": {
        "stroke": (245, 158, 11, 255),      # #f59e0b
        "fill": (245, 158, 11, 45),         # #f59e0b semi-transparent
        "badge_bg": (245, 158, 11, 240),
        "badge_text": (255, 255, 255, 255),
    },
    "info": {
        "stroke": (100, 116, 139, 255),     # #64748b
        "fill": (100, 116, 139, 35),
        "badge_bg": (100, 116, 139, 220),
        "badge_text": (255, 255, 255, 255),
    },
}


def render_page_overlay_image(
    pdf_bytes: bytes | None,
    page_num: int,
    findings: list[Any] | None = None,
    scale: float = 2.0,
) -> Image.Image:
    """Renders a PDF page with bounding box highlight overlays for findings.

    Args:
        pdf_bytes: Raw bytes of the PDF file.
        page_num: 1-based page number to render.
        findings: List of Finding objects to draw on the page.
        scale: Resolution scale factor for rendering (default 2.0 = ~144-150 DPI).

    Returns:
        PIL Image with rendered page and bounding box overlays.
    """
    if not pdf_bytes:
        img = Image.new("RGB", (800, 1050), color=(248, 250, 252))
        draw = ImageDraw.Draw(img)
        draw.text((320, 500), "No manuscript loaded", fill=(100, 116, 139))
        return img

    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    except Exception:  # noqa: BLE001
        img = Image.new("RGB", (800, 1050), color=(254, 242, 242))
        draw = ImageDraw.Draw(img)
        draw.text((300, 500), "Failed to open PDF document", fill=(239, 68, 68))
        return img

    if len(doc) == 0:
        return Image.new("RGB", (800, 1050), color=(248, 250, 252))

    idx = max(0, min(page_num - 1, len(doc) - 1))
    page = doc[idx]

    # Render base page at given DPI scale
    dpi = int(72 * scale)
    pix = page.get_pixmap(dpi=dpi)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    if not findings:
        return img

    # Overlay layer with RGBA transparency
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    page_w = page.rect.width
    page_h = page.rect.height
    scale_x = pix.width / page_w if page_w > 0 else 1.0
    scale_y = pix.height / page_h if page_h > 0 else 1.0

    try:
        font = ImageFont.load_default()
    except Exception:  # noqa: BLE001
        font = None

    for f in findings:
        f_page = getattr(f, "page", None)
        f_bbox = getattr(f, "bbox", None)

        if f_bbox and f_page == page_num:
            x0, y0, x1, y1 = f_bbox
            rx0 = min(x0, x1) * scale_x
            ry0 = min(y0, y1) * scale_y
            rx1 = max(x0, x1) * scale_x
            ry1 = max(y0, y1) * scale_y

            # Ensure minimum height/width so small points are clearly visible
            if rx1 - rx0 < 6 * scale:
                rx1 = rx0 + 6 * scale
            if ry1 - ry0 < 6 * scale:
                ry1 = ry0 + 6 * scale

            # Slight padding
            pad = 2 * scale
            rx0 = max(0, rx0 - pad)
            ry0 = max(0, ry0 - pad)
            rx1 = min(pix.width, rx1 + pad)
            ry1 = min(pix.height, ry1 + pad)

            sev = getattr(f, "severity", "info")
            sev_key = sev.value if hasattr(sev, "value") else str(sev)
            colors = SEVERITY_COLORS.get(sev_key, SEVERITY_COLORS["info"])

            # Draw highlighted rectangle
            line_w = max(2, int(2.5 * (scale / 2.0)))
            draw.rectangle([rx0, ry0, rx1, ry1], fill=colors["fill"], outline=colors["stroke"], width=line_w)

            # Draw small finding badge on top-left of box
            num = getattr(f, "number", None)
            code = getattr(f, "code", "")
            tag = f"#{num} {code}" if num is not None else code

            if tag:
                badge_w = len(tag) * 6 + 10
                badge_h = 16
                bx0 = rx0
                by0 = max(0, ry0 - badge_h)
                bx1 = bx0 + badge_w
                by1 = by0 + badge_h

                draw.rectangle([bx0, by0, bx1, by1], fill=colors["badge_bg"])
                if font:
                    draw.text((bx0 + 4, by0 + 2), tag, font=font, fill=colors["badge_text"])

    # Composite overlay onto base page
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def extract_figure_crop(
    pdf_bytes: bytes,
    page_num: int,
    bbox: tuple[float, float, float, float],
    scale: float = 2.0,
) -> Image.Image | None:
    """Extracts a cropped image of a specific region on a PDF page."""
    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        if page_num < 1 or page_num > len(doc):
            return None
        page = doc[page_num - 1]
        x0, y0, x1, y1 = bbox
        rect = pymupdf.Rect(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
        # Add 6pt margin around the figure
        rect = pymupdf.Rect(rect.x0 - 6, rect.y0 - 6, rect.x1 + 6, rect.y1 + 6) & page.rect
        pix = page.get_pixmap(dpi=int(72 * scale), clip=rect)
        return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    except Exception:  # noqa: BLE001
        return None


def apply_colorblind_filter(img: Image.Image, mode: str = "deuteranopia") -> Image.Image:
    """Applies a color vision deficiency simulation filter to an image.

    Args:
        img: Input PIL Image.
        mode: Simulation type ('deuteranopia', 'protanopia', 'tritanopia', 'greyscale').

    Returns:
        Filtered PIL Image simulating the chosen vision profile.
    """
    if mode == "greyscale":
        return img.convert("L").convert("RGB")

    # Transformation matrices for color blindness simulation
    matrices = {
        "deuteranopia": [
            0.625, 0.375, 0.0, 0.0,
            0.700, 0.300, 0.0, 0.0,
            0.0,   0.300, 0.700, 0.0,
        ],
        "protanopia": [
            0.567, 0.433, 0.0, 0.0,
            0.558, 0.442, 0.0, 0.0,
            0.0,   0.242, 0.758, 0.0,
        ],
        "tritanopia": [
            0.950, 0.050, 0.0, 0.0,
            0.0,   0.433, 0.567, 0.0,
            0.0,   0.475, 0.525, 0.0,
        ],
    }

    matrix = matrices.get(mode)
    if not matrix:
        return img.copy()

    try:
        return img.convert("RGB", matrix)
    except Exception:  # noqa: BLE001
        return img.copy()
