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
current_nav = st.query_params.get("nav", "Inspector")
st_markdown(render_top_header(current_nav), unsafe_allow_html=True)

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
if current_nav == "Inspector":
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

elif current_nav == "Diagnostics":
    st.header("Diagnostics")
    st.write("A clean Clinical Light view showing pipeline stage timings, registered checks, cache file count, and offline status.")
    
    # 1. Pipeline stage timings
    if st.session_state.report and st.session_state.report.timings:
        st.subheader("Pipeline Timings")
        st.json(st.session_state.report.timings)
    else:
        st.info("Run an audit to see pipeline timings.")
        
    # 2. Registered checks
    from deskreject.checks.base import get_all_checks, run_all
    st.subheader("Registered Checks")
    # To force lazy-load
    try:
        from deskreject.models import ParsedDoc
        run_all(ParsedDoc(file_name=""), None, None)
    except Exception:  # noqa: BLE001, S110
        pass
        
    checks = get_all_checks()
    if checks:
        for c in checks:
            name = getattr(c, "name", getattr(c, "__name__", str(c)))
            prio = getattr(c, "priority", "Unknown")
            st.text(f"{name} (Priority: {prio})")
    else:
        st.info("No checks registered yet (run an audit to lazy-load them).")
        
    # 3. Vision cache file count
    st.subheader("Vision Cache")
    cache_dir = Path(".cache/vision")
    if cache_dir.exists():
        count = len(list(cache_dir.glob("*.json")))
        st.write(f"Cached items: {count}")
    else:
        st.write("Cache directory not found.")
        
    # 4. netguard.blocked_count()
    from deskreject.netguard import blocked_count
    st.subheader("Network Guard")
    st.write(f"External requests blocked: {blocked_count()}")

elif current_nav == "Nodes":
    st.header("Nodes (Vision Cluster)")
    
    if st.button("Re-check endpoints"):
        st.rerun()
        
    import httpx
    
    st.subheader("Configured Endpoints")
    for ep in settings.ollama_vision_endpoints:
        # Check health
        try:
            res = httpx.get(f"{ep.url}/api/tags", timeout=2.0)
            healthy = res.status_code == 200
        except Exception:  # noqa: BLE001
            healthy = False
            
        status_text = "✅ Ready" if healthy else "❌ Offline"
        st.write(f"**Host:** {ep.url}")
        st.write(f"**Model:** {ep.model}")
        st.write(f"**Status:** {status_text}")
        
        # If we have run an audit, show call counts
        if st.session_state.report and st.session_state.report.vision_stats:
            stats = st.session_state.report.vision_stats.get("per_endpoint", {}).get(ep.url, {})
            calls = stats.get("calls", 0)
            seconds = stats.get("seconds", 0.0)
            st.write(f"**Calls:** {calls}")
            st.write(f"**Time:** {seconds:.2f}s")
        st.divider()

elif current_nav == "Venues":
    st.header("Venue Presets")
    
    import yaml
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("neurips-style-double-blind")
        path1 = Path("presets/neurips-style-double-blind.yaml")
        if path1.exists():
            data1 = yaml.safe_load(path1.read_text())
            st.json(data1)
            
    with col2:
        st.subheader("ieee-journal")
        path2 = Path("presets/ieee-journal.yaml")
        if path2.exists():
            data2 = yaml.safe_load(path2.read_text())
            st.json(data2)
