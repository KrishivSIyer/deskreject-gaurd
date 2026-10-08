import os
import tempfile
from pathlib import Path

import streamlit as st


def st_markdown(body, unsafe_allow_html=False, **kwargs):
    if unsafe_allow_html and isinstance(body, str):
        body = "\n".join(line.lstrip() for line in body.splitlines())
    return st.markdown(body, unsafe_allow_html=unsafe_allow_html, **kwargs)

import sys

# Add project root and src to sys.path so modules can be resolved
_root_dir = Path(__file__).resolve().parent.parent
if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))
if str(_root_dir / "src") not in sys.path:
    sys.path.insert(0, str(_root_dir / "src"))

from deskreject.config import settings
from deskreject.pipeline import audit
from deskreject.presets import load_preset
from ui.components import (
    cluster_telemetry_html,
    get_global_css,
    offline_badge_html,
    render_figures_tab,
    render_findings_tab,
    render_overlays_tab,
    render_patches_tab,
    render_run_log_tab,
    render_telemetry_bar,
    render_top_header,
)

# Page configuration
st.set_page_config(
    page_title="DeskReject Guard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject Auditor Clinical Light styling
st_markdown(get_global_css(), unsafe_allow_html=True)

# Initialize Session State
if "ai_summary" not in st.session_state:
    st.session_state.ai_summary = None
if "report" not in st.session_state:
    st.session_state.report = None
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""
if "tex_text" not in st.session_state:
    st.session_state.tex_text = None
if "preset_id" not in st.session_state:
    st.session_state.preset_id = settings.default_preset
if "bypass_cache" not in st.session_state:
    st.session_state.bypass_cache = False
if "selected_page" not in st.session_state:
    st.session_state.selected_page = 1

# Discover available presets
presets_dir = Path(__file__).resolve().parent.parent / "presets"
preset_files = list(presets_dir.glob("*.yaml")) if presets_dir.exists() else []
preset_options = [p.stem for p in preset_files] or [settings.default_preset]

# Sidebar
with st.sidebar:
    st_markdown(
        """
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span class="material-symbols-outlined"
                  style="color: #3ba4f6; font-size: 26px;">shield</span>
            <span style="font-family: 'Inter', sans-serif; font-size: 17px;
                         font-weight: 700; color: #0f172a;">DeskReject Guard</span>
        </div>
        <p style="font-size: 12px; color: #64748b; margin-top: 0; margin-bottom: 16px;">
            Catch it before the desk does.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st_markdown(
        "<div style='font-size: 11px; font-weight: 600; text-transform: uppercase; "
        "color: #64748b; font-family: JetBrains Mono; margin-bottom: 4px;'>Venue Preset</div>",
        unsafe_allow_html=True,
    )

    default_idx = (
        preset_options.index(st.session_state.preset_id)
        if st.session_state.preset_id in preset_options
        else 0
    )
    selected_preset = st.selectbox(
        "Select Preset",
        options=preset_options,
        index=default_idx,
        label_visibility="collapsed",
    )
    st.session_state.preset_id = selected_preset

    # Load preset details to show anonymity status badge
    try:
        current_preset = load_preset(selected_preset)
        anon_label = "Anonymity: ON" if current_preset.anonymous else "Anonymity: OFF"
        badge_class = (
            "dg-badge-success" if current_preset.anonymous else "dg-badge-neutral"
        )
    except (OSError, ValueError, KeyError):
        anon_label = "Anonymity: ON"
        badge_class = "dg-badge-success"

    st_markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between;
                    margin-top: 4px; margin-bottom: 14px;">
            <span style="font-size: 11px; color: #64748b;">Editable venue rule preset</span>
            <span class="dg-badge {badge_class}">{anon_label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st_markdown(
        "<div style='font-size: 11px; font-weight: 600; text-transform: uppercase; "
        "color: #64748b; font-family: JetBrains Mono; margin-bottom: 4px;'>"
        "Target Manuscript</div>",
        unsafe_allow_html=True,
    )

    uploaded_pdf = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        help="Target manuscript PDF to inspect.",
        label_visibility="collapsed",
    )
    if uploaded_pdf is not None:
        st.session_state.pdf_bytes = uploaded_pdf.read()
        st.session_state.pdf_name = uploaded_pdf.name

    uploaded_tex = st.file_uploader(
        "Upload LaTeX Source (optional)",
        type=["tex"],
        help="Optional .tex source file to generate precision diff patches.",
        label_visibility="collapsed",
    )
    if uploaded_tex is not None:
        st.session_state.tex_text = uploaded_tex.read().decode("utf-8", errors="ignore")

    bypass_cache = st.checkbox(
        "Bypass vision cache",
        value=st.session_state.bypass_cache,
        help="Forces fresh Gemma 4 calls to observe multi-node worker fan-out.",
    )
    st.session_state.bypass_cache = bypass_cache

    # Dynamic Cluster Telemetry
    vision_stats = st.session_state.report.vision_stats if st.session_state.report else None
    st_markdown(cluster_telemetry_html(vision_stats=vision_stats), unsafe_allow_html=True)

    # Action Buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        run_audit_clicked = st.button("Run audit", type="primary", use_container_width=True)
    with col2:
        load_sample_clicked = st.button("Load sample", use_container_width=True)

    # Offline guarantee badge
    blocked_reqs = (
        st.session_state.report.external_requests_blocked
        if st.session_state.report is not None
        else 0
    )
    st_markdown(offline_badge_html(blocked=blocked_reqs), unsafe_allow_html=True)

# Main Workspace Header
st_markdown(render_top_header(), unsafe_allow_html=True)

# Sample loading handler
if load_sample_clicked:
    sample_pdf_path = Path("samples/bad_paper.pdf")
    sample_tex_path = Path("samples/bad_paper.tex")

    if sample_pdf_path.exists():
        st.session_state.pdf_bytes = sample_pdf_path.read_bytes()
        st.session_state.pdf_name = "bad_paper.pdf"
        st.session_state.selected_page = 1
        if sample_tex_path.exists():
            st.session_state.tex_text = sample_tex_path.read_text(encoding="utf-8")

        with st.spinner("Running pre-flight audit on sample manuscript..."):
            st.session_state.ai_summary = None
            st.session_state.report = audit(
                pdf_path=str(sample_pdf_path),
                preset_id=st.session_state.preset_id,
                tex_text=st.session_state.tex_text,
                use_cache=not st.session_state.bypass_cache,
            )
        st.rerun()
    else:
        st.error(f"Sample PDF not found at {sample_pdf_path}")

# Audit execution handler
if run_audit_clicked:
    if st.session_state.pdf_bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(st.session_state.pdf_bytes)
            tmp_path = tmp_file.name

        try:
            with st.spinner("Running pre-flight audit..."):
                st.session_state.ai_summary = None
                st.session_state.report = audit(
                    pdf_path=tmp_path,
                    preset_id=st.session_state.preset_id,
                    tex_text=st.session_state.tex_text,
                    use_cache=not st.session_state.bypass_cache,
                )
                st.session_state.selected_page = 1
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        st.rerun()
    else:
        st.warning("Please upload a PDF manuscript or click 'Load sample' to run an audit.")


# Main Workspace Content
report = st.session_state.report

if report:
    fatal_count = report.counts.get("fatal", 0)
    warn_count = report.counts.get("warning", 0)
    risk_score = max(0, min(100, int(fatal_count * 15 + warn_count * 5))) if fatal_count or warn_count else 0
    filename = st.session_state.pdf_name or report.file_name or "manuscript.pdf"

    # Telemetry and summary ribbon
    summary_col, export_col = st.columns([4, 1])
    with summary_col:
        st_markdown(
            render_telemetry_bar(
                filename=filename,
                risk=report.risk,
                score=risk_score,
                fatal_count=fatal_count,
                warn_count=warn_count,
                page_count=report.page_count,
            ),
            unsafe_allow_html=True,
        )
    with export_col:
        st.download_button(
            label="Export Report (JSON)",
            data=report.model_dump_json(indent=2),
            file_name=f"deskreject_report_{filename}.json",
            mime="application/json",
            use_container_width=True,
        )

# Navigation Tabs (Phase 3 Full Integration)
if report:
    tab_overlays, tab_findings, tab_figures, tab_patches, tab_run_log = st.tabs(
        ["Page overlays", "Findings", "Figures", "LaTeX Patches", "Run Log"]
    )
    
    with tab_overlays:
        render_overlays_tab(report, st.session_state.pdf_bytes)
    
    with tab_findings:
        render_findings_tab(report)
    
    with tab_figures:
        render_figures_tab(report, st.session_state.pdf_bytes)
    
    with tab_patches:
        render_patches_tab(report, st.session_state.tex_text, st.session_state.preset_id)
    
    with tab_run_log:
        render_run_log_tab(report)
