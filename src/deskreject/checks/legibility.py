import io

import fitz
from PIL import Image

from deskreject.checks.base import Context, register_check
from deskreject.models import Finding, ParsedDoc, Preset, Severity


@register_check
def check_legibility(doc: ParsedDoc, preset: Preset, ctx: Context) -> list[Finding]:
    findings = []
    pdf = None

    # Check raster image DPI
    for img in doc.images:
        w_pt = img.bbox[2] - img.bbox[0]
        h_pt = img.bbox[3] - img.bbox[1]
        if w_pt < 20 or h_pt < 20:
            continue

        w_in = w_pt / 72.0
        h_in = h_pt / 72.0
        
        dpi_w = img.px_w / w_in
        dpi_h = img.px_h / h_in
        dpi = min(dpi_w, dpi_h)

        if pdf is None:
            pdf = fitz.open(doc.path)

        try:
            img_info = pdf.extract_image(img.xref)
            pil_img = Image.open(io.BytesIO(img_info["image"]))
            if pil_img.mode != "RGB":
                pil_img = pil_img.convert("RGB")
            colors = pil_img.getcolors(65)
            is_line_art = colors is not None and len(colors) <= 64
        except Exception:  # noqa: BLE001
            is_line_art = False

        fatal_below = preset.min_raster_dpi.fatal_below
        line_art_min = preset.min_raster_dpi.line_art
        photo_min = preset.min_raster_dpi.photo

        severity = None
        if dpi < fatal_below:
            severity = Severity.fatal
        elif is_line_art and dpi < line_art_min or not is_line_art and dpi < photo_min:
            severity = Severity.warning

        if severity:
            kind_str = "Line art" if is_line_art else "Photo"
            evidence = f"{min(img.px_w, img.px_h)} px over {min(w_in, h_in):.1f} in = {int(dpi)} dpi"
            findings.append(Finding(
                code="LEG_RASTER_LOW_DPI",
                check="legibility",
                severity=severity,
                title="Low resolution image",
                detail=f"{kind_str} has very low resolution.",
                page=img.page,
                bbox=img.bbox,
                evidence=evidence,
                source="rule",
            ))

    if pdf:
        pdf.close()

    # Check font sizes in figures
    for fig in doc.figures:
        small_spans = [s for s in fig.spans if s.size < preset.min_figure_font_pt]
        if small_spans:
            min_size = min(s.size for s in small_spans)
            count = len(small_spans)
            fig_w_in = (fig.region[2] - fig.region[0]) / 72.0
            
            findings.append(Finding(
                code="LEG_FONT_TOO_SMALL",
                check="legibility",
                severity=Severity.warning,
                title="Small text in figure",
                detail=f"Found {count} text elements smaller than {preset.min_figure_font_pt} pt.",
                page=fig.page,
                bbox=fig.region,
                evidence=f"Smallest is {min_size:.1f} pt. Figure printed at {fig_w_in:.1f} in wide.",
                source="rule",
                figure_id=fig.id,
            ))

    return findings
