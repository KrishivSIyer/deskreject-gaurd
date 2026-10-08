"""UI components and design system tokens for DeskReject Guard."""

from __future__ import annotations

import base64
from io import BytesIO
from typing import TYPE_CHECKING, Any

import streamlit as st
from PIL import Image

from deskreject.config import Endpoint, settings

if TYPE_CHECKING:
    from deskreject.models import Report


def pil_to_base64(img: Image.Image, format: str = "PNG") -> str:
    """Encodes a PIL Image to a base64 data-URI string."""
    buffered = BytesIO()
    img.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/{format.lower()};base64,{img_str}"


def get_global_css() -> str:
    """Returns the Auditor Clinical Light design system stylesheet."""
    return """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #3ba4f6;
            --primary-hover: #258cdb;
            --primary-container: #e0f2fe;
            --on-primary-container: #0369a1;
            --secondary: #64748b;
            --secondary-container: #f1f5f9;
            --tertiary: #10b981;
            --tertiary-container: #d1fae5;
            --on-tertiary-container: #065f46;
            --error: #ef4444;
            --error-container: #fee2e2;
            --on-error-container: #991b1b;
            --warn: #f59e0b;
            --warn-container: #fef3c7;
            --surface: #ffffff;
            --surface-dim: #f8fafc;
            --surface-container-low: #f8fafc;
            --surface-container: #f1f5f9;
            --surface-container-high: #e2e8f0;
            --surface-container-highest: #cbd5e1;
            --on-surface: #0f172a;
            --on-surface-variant: #475569;
            --outline: #cbd5e1;
            --outline-variant: #e2e8f0;
            --radius-sm: 0.125rem;
            --radius-md: 0.25rem;
            --radius-lg: 0.5rem;
            --radius-xl: 0.75rem;
            --radius-full: 9999px;
            --font-ui: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --font-code: 'JetBrains Mono', monospace;
        }

        /* Base app layout styling */
        html, body, [data-testid="stAppViewContainer"] {
            font-family: var(--font-ui) !important;
            background-color: var(--surface) !important;
            color: var(--on-surface) !important;
        }

        [data-testid="stHeader"] {
            background-color: transparent !important;
        }

        [data-testid="stSidebar"] {
            background-color: var(--surface-container-low) !important;
            border-right: 1px solid var(--outline-variant) !important;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            font-size: 13px !important;
            color: var(--on-surface-variant) !important;
        }

        /* Streamlit typography overrides */
        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-ui) !important;
            color: var(--on-surface) !important;
            font-weight: 600 !important;
            letter-spacing: -0.015em !important;
        }

        code, pre, .font-mono {
            font-family: var(--font-code) !important;
        }

        /* Primary and secondary button overrides */
        .stButton > button {
            font-family: var(--font-ui) !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            border-radius: var(--radius-lg) !important;
            padding: 0.45rem 0.9rem !important;
            transition: all 0.15s ease-in-out !important;
            border: 1px solid var(--outline) !important;
            background-color: var(--surface) !important;
            color: var(--on-surface) !important;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
        }

        .stButton > button:hover {
            border-color: var(--primary) !important;
            background-color: var(--surface-container) !important;
            color: var(--primary) !important;
        }

        .stButton > button[kind="primary"] {
            background-color: var(--primary) !important;
            color: #ffffff !important;
            border: 1px solid var(--primary) !important;
            box-shadow: 0 1px 3px 0 rgba(59, 164, 246, 0.3) !important;
        }

        .stButton > button[kind="primary"]:hover {
            background-color: var(--primary-hover) !important;
            border-color: var(--primary-hover) !important;
            color: #ffffff !important;
        }

        /* Radio buttons horizontal filters */
        [data-testid="stRadio"] > div {
            flex-direction: row !important;
            gap: 12px !important;
            align-items: center !important;
        }

        [data-testid="stRadio"] label {
            font-size: 13px !important;
            font-weight: 500 !important;
            cursor: pointer !important;
        }

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px !important;
            background-color: var(--surface-container-low) !important;
            padding: 6px 12px !important;
            border-radius: var(--radius-lg) !important;
            border: 1px solid var(--outline-variant) !important;
            margin-bottom: 1.25rem !important;
        }

        .stTabs [data-baseweb="tab"] {
            font-family: var(--font-ui) !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            color: var(--on-surface-variant) !important;
            background-color: transparent !important;
            border-radius: var(--radius-md) !important;
            padding: 6px 14px !important;
            border: none !important;
        }

        .stTabs [aria-selected="true"] {
            font-weight: 600 !important;
            color: var(--primary) !important;
            background-color: var(--surface) !important;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.08) !important;
            border: 1px solid var(--outline-variant) !important;
        }

        /* Expanders styling */
        [data-testid="stExpander"] {
            border: 1px solid var(--outline-variant) !important;
            border-radius: var(--radius-lg) !important;
            background-color: var(--surface) !important;
            margin-bottom: 10px !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
        }

        [data-testid="stExpander"]:hover {
            border-color: var(--outline) !important;
        }

        /* File uploader styling */
        [data-testid="stFileUploader"] {
            background-color: var(--surface) !important;
            border: 1px dashed var(--outline) !important;
            border-radius: var(--radius-lg) !important;
            padding: 8px !important;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: var(--primary) !important;
        }

        /* Custom badge, pill, & card styling */
        .dg-card {
            background-color: var(--surface);
            border: 1px solid var(--outline-variant);
            border-radius: var(--radius-lg);
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            margin-bottom: 1rem;
        }

        .dg-telemetry-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #ffffff;
            border: 1px solid var(--outline-variant);
            border-radius: var(--radius-full);
            padding: 6px 16px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
            font-family: var(--font-code);
            font-size: 12px;
        }

        .dg-badge {
            display: inline-flex;
            align-items: center;
            padding: 2px 8px;
            border-radius: var(--radius-sm);
            font-size: 11px;
            font-weight: 600;
            font-family: var(--font-code);
            text-transform: uppercase;
        }
        .dg-badge-success {
            background-color: var(--tertiary-container);
            color: var(--on-tertiary-container);
        }
        .dg-badge-fatal {
            background-color: var(--error-container);
            color: var(--on-error-container);
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        .dg-badge-warn {
            background-color: var(--warn-container);
            color: #b45309;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        .dg-badge-neutral {
            background-color: var(--surface-container-high);
            color: var(--secondary);
        }

        /* Pulse animation for active nodes */
        @keyframes dg-pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        .dg-dot-active {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--tertiary);
            display: inline-block;
            animation: dg-pulse 2s infinite ease-in-out;
        }
        .dg-dot-fail {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--error);
            display: inline-block;
        }

        /* Figure card styling */
        .dg-fig-card {
            background: #ffffff;
            border: 1px solid var(--outline-variant);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 16px;
            transition: all 0.2s ease;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .dg-fig-card:hover {
            border-color: var(--primary);
            box-shadow: 0 4px 12px rgba(59, 164, 246, 0.08);
        }

        /* Finding box styling inside expanders */
        .dg-evidence-box {
            background: #f8fafc;
            border-left: 3px solid #64748b;
            padding: 8px 12px;
            border-radius: 0 4px 4px 0;
            font-family: var(--font-code);
            font-size: 12px;
            color: #0f172a;
            margin: 6px 0;
            overflow-x: auto;
        }
        .dg-fix-box {
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-left: 3px solid #10b981;
            padding: 8px 12px;
            border-radius: 0 4px 4px 0;
            font-size: 13px;
            color: #166534;
            margin: 6px 0;
        }
    </style>
    """


def render_top_header() -> str:
    """Renders the top navigation and brand ribbon HTML."""
    return """
    <div style="display: flex; align-items: center; justify-content: space-between;
                padding: 12px 24px; background: #ffffff; border-bottom: 1px solid #e2e8f0;
                margin: -4rem -4rem 1.5rem -4rem; position: sticky; top: 0; z-index: 100;">
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span class="material-symbols-outlined"
                      style="color: #3ba4f6; font-size: 28px;">verified_user</span>
                <span style="font-family: 'Inter', sans-serif; font-size: 18px;
                             font-weight: 700; color: #0f172a; letter-spacing: -0.02em;">
                    DeskReject Guard
                </span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px; margin-left: 16px;">
                <span style="font-size: 13px; font-weight: 600; color: #3ba4f6;
                             background: rgba(59, 164, 246, 0.1); padding: 4px 10px;
                             border-radius: 6px;">Inspector</span>
                <span style="font-size: 13px; color: #64748b; padding: 4px 10px;">Diagnostics</span>
                <span style="font-size: 13px; color: #64748b; padding: 4px 10px;">Nodes</span>
                <span style="font-size: 13px; color: #64748b; padding: 4px 10px;">Venues</span>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="display: inline-flex; align-items: center; gap: 6px;
                        background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0;
                        padding: 4px 12px; border-radius: 9999px; font-family: 'JetBrains Mono',
                        monospace; font-size: 11px; font-weight: 600;">
                <span class="material-symbols-outlined" style="font-size: 14px;">lock</span>
                100% LOCAL AUDIT
            </div>
        </div>
    </div>
    """


def cluster_telemetry_html(
    endpoints: list[Endpoint] | None = None,
    vision_stats: dict[str, Any] | None = None,
) -> str:
    """Renders the Vision Cluster Telemetry card for the sidebar."""
    if endpoints is None:
        endpoints = settings.ollama_vision_endpoints

    node_count = len(endpoints) if endpoints else 1
    per_endpoint_stats = vision_stats.get("per_endpoint", {}) if vision_stats else {}
    rows_html = []

    if endpoints:
        for idx, ep in enumerate(endpoints):
            name = "Host" if idx == 0 else f"Worker {idx}"
            model_tag = ep.model.split(":")[0] if ":" in ep.model else ep.model
            calls = per_endpoint_stats.get(ep.url, 0) if per_endpoint_stats else 0
            status_text = f"{calls} calls" if calls > 0 else "Ready"
            rows_html.append(f"""
            <div style="display: flex; align-items: center; justify-content: space-between;
                        padding: 4px 0; border-bottom: 1px solid #f1f5f9;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span class="dg-dot-active"></span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px;
                                 font-weight: 600; color: #0f172a;">{name}</span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px;
                                 color: #64748b;">({model_tag})</span>
                </div>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px;
                             color: #10b981; font-weight: 500;">{status_text}</span>
            </div>
            """)
    else:
        rows_html.append("""
        <div style="display: flex; align-items: center; justify-content: space-between;
                    padding: 4px 0;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <span class="dg-dot-active"></span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px;
                             font-weight: 600; color: #0f172a;">Host</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px;
                             color: #64748b;">(standalone)</span>
            </div>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px;
                         color: #10b981; font-weight: 500;">Ready</span>
        </div>
        """)

    content = "".join(rows_html)
    return f"""
    <div style="margin-top: 10px; margin-bottom: 14px;">
        <div style="display: flex; align-items: center; justify-content: space-between;
                    margin-bottom: 6px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px;
                         font-weight: 600; text-transform: uppercase; color: #64748b;
                         letter-spacing: 0.06em;">Vision Cluster Telemetry</span>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px;
                         color: #10b981; font-weight: 700;">{node_count} Nodes</span>
        </div>
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px;
                    padding: 8px 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.04);">
            {content}
        </div>
    </div>
    """


def offline_badge_html(blocked: int = 0) -> str:
    """Renders the offline guarantee badge."""
    return f"""
    <div style="margin-top: 16px; padding-top: 12px; border-top: 1px solid #e2e8f0;
                display: flex; align-items: center; justify-content: center;">
        <div style="display: inline-flex; align-items: center; gap: 6px;
                    padding: 4px 10px; border-radius: 9999px; background: rgba(16, 185, 129, 0.1);
                    color: #065f46; border: 1px solid rgba(16, 185, 129, 0.2);
                    font-family: 'JetBrains Mono', monospace; font-size: 11px;">
            <span class="material-symbols-outlined" style="font-size: 14px;">lock</span>
            <span>100% local. external requests blocked: <strong>{blocked}</strong></span>
        </div>
    </div>
    """


def render_telemetry_bar(
    filename: str,
    risk: str,
    score: int,
    fatal_count: int,
    warn_count: int,
    page_count: int,
) -> str:
    """Renders the top summary telemetry pill bar matching Stitch UI."""
    risk_color = (
        "#ef4444" if risk.upper() == "HIGH" else "#f59e0b" if risk.upper() == "MED" or risk.upper() == "MEDIUM" else "#10b981"
    )
    risk_bg = (
        "#fee2e2" if risk.upper() == "HIGH" else "#fef3c7" if risk.upper() == "MED" or risk.upper() == "MEDIUM" else "#d1fae5"
    )
    risk_text = (
        "#991b1b" if risk.upper() == "HIGH" else "#92400e" if risk.upper() == "MED" or risk.upper() == "MEDIUM" else "#065f46"
    )

    return f"""
    <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 12px;
                background: #ffffff; border: 1px solid #e2e8f0; padding: 8px 16px;
                border-radius: 9999px; box-shadow: 0 1px 2px rgba(0,0,0,0.04);
                margin-bottom: 1rem;">
        <div style="display: flex; align-items: center; gap: 6px;
                    font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #0f172a;">
            <span class="material-symbols-outlined" style="color: #64748b; font-size: 16px;">
                picture_as_pdf
            </span>
            <span style="font-weight: 600;">{filename}</span>
        </div>
        <span style="width: 1px; height: 14px; background: #e2e8f0;"></span>
        <div style="display: flex; align-items: center; gap: 6px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px;
                         color: #64748b; text-transform: uppercase; font-weight: 600;">
                Desk-Reject Risk
            </span>
            <span style="padding: 2px 8px; border-radius: 4px; background: {risk_bg};
                         color: {risk_text}; font-family: 'JetBrains Mono', monospace;
                         font-size: 11px; font-weight: 700;">
                {risk.upper()} ({score}/100)
            </span>
        </div>
        <span style="width: 1px; height: 14px; background: #e2e8f0;"></span>
        <div style="display: flex; align-items: center; gap: 6px;
                    font-family: 'JetBrains Mono', monospace; font-size: 11px;">
            <span style="color: {risk_color}; font-weight: 700; display: inline-flex;
                         align-items: center; gap: 4px;">
                <span style="width: 6px; height: 6px; border-radius: 50%;
                             background: {risk_color};"></span>
                {fatal_count} Fatal
            </span>
            <span style="color: #cbd5e1;">•</span>
            <span style="color: #64748b; font-weight: 700; display: inline-flex;
                         align-items: center; gap: 4px;">
                <span style="width: 6px; height: 6px; border-radius: 50%;
                             background: #f59e0b;"></span>
                {warn_count} Warn
            </span>
        </div>
        <span style="width: 1px; height: 14px; background: #e2e8f0;"></span>
        <div style="font-size: 12px; color: #64748b;">
            <span style="color: #3ba4f6; font-weight: 600;">{page_count} Pages</span>
        </div>
    </div>
    """


def render_findings_tab(report: Report | None) -> None:
    """Renders the interactive High-Risk Findings diagnostic table with inline evidence."""
    if not report or not report.findings:
        st.info("No findings reported. Run an audit to inspect the manuscript for desk-reject flaws.")
        return

    # Severity and Category Filters
    filter_col1, filter_col2 = st.columns([3, 2])
    with filter_col1:
        sev_counts = report.counts
        severity_filter = st.radio(
            "Filter by Severity",
            options=["All", "Fatal", "Warning", "Info"],
            format_func=lambda x: {
                "All": f"All ({len(report.findings)})",
                "Fatal": f"Fatal ({sev_counts.get('fatal', 0)})",
                "Warning": f"Warning ({sev_counts.get('warning', 0)})",
                "Info": f"Info ({sev_counts.get('info', 0)})",
            }.get(x, x),
            horizontal=True,
            label_visibility="collapsed",
        )

    with filter_col2:
        checks = sorted({f.check for f in report.findings if f.check})
        check_options = ["All Checks"] + checks
        selected_check = st.selectbox(
            "Filter by Check Category",
            options=check_options,
            label_visibility="collapsed",
        )

    # Filter findings
    filtered_findings = []
    for f in report.findings:
        f_sev = f.severity.value.lower() if hasattr(f.severity, "value") else str(f.severity).lower()
        if severity_filter != "All" and f_sev != severity_filter.lower():
            continue
        if selected_check != "All Checks" and f.check != selected_check:
            continue
        filtered_findings.append(f)

    st.markdown(
        f"<div style='font-size: 12px; color: #64748b; margin-top: 4px; margin-bottom: 12px;'>"
        f"Showing <strong>{len(filtered_findings)}</strong> of {len(report.findings)} diagnostic findings"
        f"</div>",
        unsafe_allow_html=True,
    )

    if not filtered_findings:
        st.success("No findings match the selected filters.")
        return

    # Render finding cards
    for f in filtered_findings:
        sev_val = f.severity.value if hasattr(f.severity, "value") else str(f.severity)
        sev_badge_class = (
            "dg-badge-fatal" if sev_val == "fatal" else "dg-badge-warn" if sev_val == "warning" else "dg-badge-neutral"
        )
        sev_label = sev_val.upper()

        page_str = f"Page {f.page}" if f.page else "Document Level"
        num_str = f"#{f.number} " if f.number is not None else ""
        expander_title = f"{num_str}[{f.code}] {f.title}"

        is_fatal = sev_val == "fatal"
        with st.expander(expander_title, expanded=is_fatal):
            # Header info strip
            st.markdown(
                f"""
                <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
                            gap: 8px; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid #f1f5f9;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="dg-badge {sev_badge_class}">{sev_label}</span>
                        <span style="font-size: 12px; font-weight: 600; color: #475569;
                                     font-family: 'JetBrains Mono', monospace;">{page_str}</span>
                        <span style="font-size: 12px; color: #64748b;">•</span>
                        <span style="font-size: 12px; color: #64748b;">Category: <strong>{f.check}</strong></span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px; font-size: 11px;
                                font-family: 'JetBrains Mono', monospace; color: #64748b;">
                        <span>Source: <strong>{f.source}</strong></span>
                        <span>Confidence: <strong>{int(f.confidence * 100)}%</strong></span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Detail text
            st.markdown(f"<div style='font-size: 13px; color: #1e293b; margin-bottom: 8px;'>{f.detail}</div>", unsafe_allow_html=True)

            # Evidence block
            if f.evidence:
                st.markdown(
                    "<div style='font-size: 11px; font-weight: 600; text-transform: uppercase; "
                    "color: #64748b; font-family: JetBrains Mono; margin-top: 6px;'>Evidence</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(f"<div class='dg-evidence-box'>{f.evidence}</div>", unsafe_allow_html=True)

            # Fix hint block
            if f.fix_hint:
                st.markdown(
                    "<div style='font-size: 11px; font-weight: 600; text-transform: uppercase; "
                    "color: #15803d; font-family: JetBrains Mono; margin-top: 6px;'>Recommended Fix</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(f"<div class='dg-fix-box'>💡 {f.fix_hint}</div>", unsafe_allow_html=True)

            # Patch tag if available
            if f.patch_key:
                st.markdown(
                    f"<div style='display: inline-flex; align-items: center; gap: 4px; margin-top: 6px; "
                    f"background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 4px; "
                    f"font-size: 11px; font-family: JetBrains Mono; font-weight: 600;'>"
                    f"🛠 LaTeX Patch Ready: <code>{f.patch_key}</code></div>",
                    unsafe_allow_html=True,
                )


def render_figures_tab(report: Report | None, pdf_bytes: bytes | None) -> None:
    """Renders the Figure card grid, sub-panel crops, and figure visual audit."""
    if not report:
        st.info("No audit data available. Run an audit to inspect figures.")
        return

    from ui.overlays import extract_figure_crop

    # Collect all figures mentioned or found in findings
    fig_map: dict[str, dict[str, Any]] = {}

    for f in report.findings:
        if f.figure_id:
            fig_id = f.figure_id
            if fig_id not in fig_map:
                fig_map[fig_id] = {
                    "id": fig_id,
                    "page": f.page or 1,
                    "findings": [],
                    "bbox": f.bbox,
                }
            fig_map[fig_id]["findings"].append(f)
            if not fig_map[fig_id]["bbox"] and f.bbox:
                fig_map[fig_id]["bbox"] = f.bbox

    # Fallback to general figures if specific figure findings are empty
    if not fig_map:
        fig_findings = [f for f in report.findings if f.check in ("figure_caption", "legibility", "accessibility") or "FIG" in f.code or "LEG" in f.code]
        for idx, f in enumerate(fig_findings, 1):
            fid = f"Figure Region #{idx}"
            fig_map[fid] = {
                "id": fid,
                "page": f.page or 1,
                "findings": [f],
                "bbox": f.bbox,
            }

    if not fig_map:
        st.success("No figure discrepancies or visual layer issues detected.")
        return

    # Filter strip
    filter_choice = st.radio(
        "Figure Filter",
        options=["All Figures", "Has Issues", "Clean"],
        horizontal=True,
        label_visibility="collapsed",
    )

    items = list(fig_map.values())
    if filter_choice == "Has Issues":
        items = [item for item in items if item["findings"]]
    elif filter_choice == "Clean":
        items = [item for item in items if not item["findings"]]

    st.markdown(
        f"<div style='font-size: 12px; color: #64748b; margin-bottom: 16px;'>"
        f"Inspecting <strong>{len(items)}</strong> figure structures across the manuscript"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Render figure grid in 2 or 3 columns
    cols_per_row = 3
    rows = [items[i:i + cols_per_row] for i in range(0, len(items), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row)
        for col, fig in zip(cols, row):
            with col:
                n_fatal = sum(1 for f in fig["findings"] if (f.severity.value if hasattr(f.severity, "value") else f.severity) == "fatal")
                n_warn = sum(1 for f in fig["findings"] if (f.severity.value if hasattr(f.severity, "value") else f.severity) == "warning")

                status_badge = (
                    f"<span class='dg-badge dg-badge-fatal'>{n_fatal} FATAL</span>"
                    if n_fatal > 0
                    else f"<span class='dg-badge dg-badge-warn'>{n_warn} WARN</span>"
                    if n_warn > 0
                    else "<span class='dg-badge dg-badge-success'>CLEAN</span>"
                )

                crop_img = None
                if pdf_bytes and fig.get("bbox") and fig.get("page"):
                    crop_img = extract_figure_crop(pdf_bytes, fig["page"], fig["bbox"])

                with st.container():
                    st.markdown(
                        f"""
                        <div class="dg-fig-card">
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                                <span style="font-weight: 700; font-size: 14px; color: #0f172a;">{fig['id']}</span>
                                <div>{status_badge}</div>
                            </div>
                            <div style="font-size: 11px; color: #64748b; font-family: 'JetBrains Mono', monospace; margin-bottom: 8px;">
                                Located on Page {fig['page']}
                            </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if crop_img:
                        st.image(crop_img, use_container_width=True)
                    else:
                        st.markdown(
                            "<div style='height: 100px; background: #f1f5f9; border: 1px dashed #cbd5e1; "
                            "border-radius: 4px; display: flex; align-items: center; justify-content: center; "
                            "color: #94a3b8; font-size: 12px;'>Figure Region Preview</div>",
                            unsafe_allow_html=True,
                        )

                    # List issue tags
                    if fig["findings"]:
                        tags_html = "".join([
                            f"<span style='display: inline-block; background: #fee2e2; color: #991b1b; "
                            f"font-size: 10px; font-family: JetBrains Mono; padding: 2px 6px; "
                            f"border-radius: 3px; margin: 2px;'>{f.code}</span>"
                            for f in fig["findings"]
                        ])
                        st.markdown(f"<div style='margin-top: 8px;'>{tags_html}</div>", unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)


def render_overlays_tab(report: Report | None, pdf_bytes: bytes | None) -> None:
    """Renders the Page Overlays tab with rasterized page viewer, bbox annotations, and sidebar."""
    if not report:
        st.info("No audit report loaded. Run an audit to inspect manuscript page overlays.")
        return

    from ui.overlays import apply_colorblind_filter, render_page_overlay_image

    page_count = report.page_count or 1

    # Initialize selected page in session state
    if "selected_page" not in st.session_state:
        first_fatal_page = next((f.page for f in report.findings if f.page and (f.severity.value if hasattr(f.severity, "value") else f.severity) == "fatal"), 1)
        st.session_state.selected_page = first_fatal_page

    # Page Selector Strip
    st.markdown(
        "<div style='font-size: 11px; font-weight: 600; text-transform: uppercase; "
        "color: #64748b; font-family: JetBrains Mono; margin-bottom: 6px;'>Select Page to Inspect</div>",
        unsafe_allow_html=True,
    )

    page_cols = st.columns(min(page_count, 10))
    for p_num in range(1, page_count + 1):
        col_idx = (p_num - 1) % len(page_cols)
        p_fatal = sum(1 for f in report.findings if f.page == p_num and (f.severity.value if hasattr(f.severity, "value") else f.severity) == "fatal")
        p_warn = sum(1 for f in report.findings if f.page == p_num and (f.severity.value if hasattr(f.severity, "value") else f.severity) == "warning")

        label = f"P{p_num}"
        if p_fatal > 0:
            label += f" ({p_fatal}🔴)"
        elif p_warn > 0:
            label += f" ({p_warn}🟡)"

        is_current = st.session_state.selected_page == p_num
        btn_type = "primary" if is_current else "secondary"

        with page_cols[col_idx]:
            if st.button(label, key=f"page_btn_{p_num}", type=btn_type, use_container_width=True):
                st.session_state.selected_page = p_num
                st.rerun()

    sel_page = st.session_state.selected_page

    # Controls Row (Scale, Colorblind mode)
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 2, 2])
    with ctrl_col1:
        scale_option = st.selectbox(
            "Resolution Scale",
            options=[1.5, 2.0, 2.5, 3.0],
            index=1,
            format_func=lambda x: f"{int(x * 72)} DPI ({int(x * 100)}%)",
        )
    with ctrl_col2:
        cb_mode = st.selectbox(
            "Color Vision Simulation",
            options=["normal", "deuteranopia", "protanopia", "tritanopia", "greyscale"],
            format_func=lambda x: x.capitalize(),
        )
    with ctrl_col3:
        findings_on_page = [f for f in report.findings if f.page == sel_page]
        st.markdown(
            f"""
            <div style="padding-top: 24px; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #475569;">
                Annotations on Page {sel_page}: <strong>{len(findings_on_page)}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Main Split View: Viewport (left 70%) and Page Findings Panel (right 30%)
    view_col, side_col = st.columns([3, 1])

    with view_col:
        overlay_img = render_page_overlay_image(
            pdf_bytes=pdf_bytes,
            page_num=sel_page,
            findings=report.findings,
            scale=scale_option,
        )

        if cb_mode != "normal":
            overlay_img = apply_colorblind_filter(overlay_img, mode=cb_mode)

        st.image(
            overlay_img,
            caption=f"Page {sel_page} of {page_count} — Diagnostic Overlays & Flaw Boundaries",
            use_container_width=True,
        )

    with side_col:
        st.markdown(
            f"""
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 700;
                        color: #0f172a; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 1px solid #e2e8f0;">
                Page {sel_page} Findings
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not findings_on_page:
            st.markdown(
                "<div style='font-size: 13px; color: #10b981; padding: 12px; background: #d1fae5; "
                "border-radius: 6px; border: 1px solid #a7f3d0;'>✓ No desk-reject flaws detected on this page.</div>",
                unsafe_allow_html=True,
            )
        else:
            for f in findings_on_page:
                sev = f.severity.value if hasattr(f.severity, "value") else str(f.severity)
                chip_class = (
                    "dg-badge-fatal" if sev == "fatal" else "dg-badge-warn" if sev == "warning" else "dg-badge-neutral"
                )
                tag = f"#{f.number} " if f.number is not None else ""

                st.markdown(
                    f"""
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px;
                                padding: 10px; margin-bottom: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; color: #0f172a;">
                                {tag}{f.code}
                            </span>
                            <span class="dg-badge {chip_class}">{sev.upper()}</span>
                        </div>
                        <div style="font-size: 12px; color: #334155; margin-bottom: 4px;">
                            {f.title}
                        </div>
                        <div style="font-size: 11px; color: #64748b; font-family: 'JetBrains Mono', monospace;">
                            Check: {f.check}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
