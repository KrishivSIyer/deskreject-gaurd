"""Overlay rendering stubs for DeskReject Guard page and finding visualization."""

from PIL import Image


def render_page_overlay_image(
    pdf_bytes: bytes,
    page_num: int,
    findings: list | None = None,
    scale: float = 2.0,
) -> Image.Image:
    """Renders a PDF page with bounding box highlight overlays for findings.

    Args:
        pdf_bytes: Raw bytes of the uploaded PDF file.
        page_num: 1-based page number to render.
        findings: List of Finding objects to draw on the page.
        scale: Resolution scale factor for rendering.

    Returns:
        PIL Image with rendered page and bounding box overlays.
    """
    # Stub implementation for Phase 1
    return Image.new("RGB", (600, 800), color=(255, 255, 255))


def apply_colorblind_filter(img: Image.Image, mode: str = "deuteranopia") -> Image.Image:
    """Applies a color vision deficiency simulation filter to an image.

    Args:
        img: Input PIL Image.
        mode: Simulation type ('deuteranopia', 'protanopia', 'tritanopia', 'greyscale').

    Returns:
        Filtered PIL Image simulating the chosen vision profile.
    """
    # Stub implementation for Phase 1
    return img.copy()
