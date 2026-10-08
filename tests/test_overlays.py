"""Tests for page overlay rendering, crop extraction, and colorblind filters."""

from pathlib import Path

from PIL import Image

from deskreject.models import Finding, Report, Severity
from deskreject.patches.latex import apply_patches
from deskreject.presets import load_preset
from ui.components import (
    cluster_telemetry_html,
    get_global_css,
    offline_badge_html,
    pil_to_base64,
    render_risk_gauge,
    render_telemetry_bar,
    render_top_header,
)
from ui.overlays import apply_colorblind_filter, extract_figure_crop, render_page_overlay_image


def test_render_page_overlay_empty():
    """Verify empty input returns fallback placeholder without error."""
    img = render_page_overlay_image(None, 1, [])
    assert isinstance(img, Image.Image)
    assert img.size == (800, 1050)


def test_render_page_overlay_with_sample_pdf():
    """Verify rendering overlays on a real sample PDF."""
    sample_path = Path("samples/bad_paper.pdf")
    if not sample_path.exists():
        return

    pdf_bytes = sample_path.read_bytes()
    findings = [
        Finding(
            code="ANON_AUTHOR_BLOCK",
            check="anonymity",
            severity=Severity.fatal,
            title="Author name present",
            detail="Author name detected on title block",
            page=1,
            bbox=(50.0, 70.0, 250.0, 110.0),
            number=1,
        ),
        Finding(
            code="FIG_LABEL_DISCREPANCY",
            check="figure_caption",
            severity=Severity.warning,
            title="Figure label discrepancy",
            detail="Figure 1 panel mismatch",
            page=1,
            bbox=(50.0, 200.0, 300.0, 300.0),
            number=2,
        ),
    ]

    img = render_page_overlay_image(pdf_bytes, 1, findings, scale=1.5)
    assert isinstance(img, Image.Image)
    assert img.width > 0
    assert img.height > 0


def test_extract_figure_crop():
    """Verify figure region crop extraction."""
    sample_path = Path("samples/bad_paper.pdf")
    if not sample_path.exists():
        return

    pdf_bytes = sample_path.read_bytes()
    crop = extract_figure_crop(pdf_bytes, 1, (50.0, 200.0, 300.0, 300.0), scale=2.0)
    assert crop is not None
    assert isinstance(crop, Image.Image)
    assert crop.width > 0


def test_apply_colorblind_filter():
    """Verify color vision deficiency filter transformations."""
    base = Image.new("RGB", (100, 100), color=(200, 50, 50))
    deuter = apply_colorblind_filter(base, mode="deuteranopia")
    assert isinstance(deuter, Image.Image)
    assert deuter.size == (100, 100)

    grey = apply_colorblind_filter(base, mode="greyscale")
    assert isinstance(grey, Image.Image)

    normal = apply_colorblind_filter(base, mode="unknown")
    assert normal.size == (100, 100)


def test_ui_components_html_generators():
    """Verify design system HTML helper generators."""
    css = get_global_css()
    assert "--primary: #3ba4f6;" in css

    header = render_top_header()
    assert "DeskReject Guard" in header

    badge = offline_badge_html(blocked=0)
    assert "100% local" in badge

    telemetry = cluster_telemetry_html(endpoints=None, vision_stats={"per_endpoint": {}})
    assert "Vision Cluster Telemetry" in telemetry

    telemetry_bar = render_telemetry_bar(
        filename="test.pdf",
        risk="HIGH",
        score=85,
        fatal_count=3,
        warn_count=1,
        page_count=8,
    )
    assert "HIGH (85/100)" in telemetry_bar
    assert "3 Fatal" in telemetry_bar

    # Test risk gauge
    mock_report = Report(
        preset="neurips-style-double-blind",
        file_name="test.pdf",
        page_count=8,
        findings=[],
        risk="HIGH",
        counts={"fatal": 5, "warning": 2, "info": 0},
        timings={"parse": 0.1, "checks": 0.2, "total": 0.3},
        vision_stats={"calls": 4, "cache_hits": 2, "failures": 0, "per_endpoint": {}},
        external_requests_blocked=0,
    )
    gauge_html = render_risk_gauge(mock_report)
    assert "Desk-Reject Risk: HIGH" in gauge_html
    assert "5 Fatal" in gauge_html

    # Test base64 encoding
    b64 = pil_to_base64(Image.new("RGB", (10, 10), color=(255, 255, 255)))
    assert b64.startswith("data:image/png;base64,")


def test_apply_patches_helper():
    """Verify apply_patches generates modified LaTeX source."""
    tex_path = Path("samples/bad_paper.tex")
    if not tex_path.exists():
        return

    original_tex = tex_path.read_text(encoding="utf-8")
    preset = load_preset("neurips-style-double-blind")

    findings = [
        Finding(
            code="ANON_CLASS",
            check="anon",
            severity=Severity.fatal,
            title="",
            detail="",
            patch_key="anon_class",
        ),
        Finding(
            code="ANON_AUTHOR",
            check="anon",
            severity=Severity.fatal,
            title="",
            detail="",
            patch_key="anon_author",
        ),
        Finding(
            code="ANON_URL",
            check="anon",
            severity=Severity.fatal,
            title="",
            detail="",
            patch_key="anon_url",
            evidence="https://github.com/rao-lab/deskproject",
        ),
    ]

    patched = apply_patches(original_tex, findings, preset)
    assert patched != original_tex
    assert "anonymous" in patched
    assert "Anonymous Authors" in patched or preset.latex.author_placeholder in patched
    assert preset.latex.anonymous_repo_url in patched
