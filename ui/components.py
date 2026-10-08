"""UI components and design system tokens for DeskReject Guard."""

from deskreject.config import Endpoint, settings


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
            font-size: 14px !important;
            border-radius: var(--radius-lg) !important;
            padding: 0.5rem 1rem !important;
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
        }
        .dg-badge-warn {
            background-color: var(--warn-container);
            color: #b45309;
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

        /* Streamlit info alert overrides */
        [data-testid="stAlert"] {
            border-radius: var(--radius-lg) !important;
            border: 1px solid var(--outline-variant) !important;
            font-family: var(--font-ui) !important;
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


def cluster_telemetry_html(endpoints: list[Endpoint] | None = None) -> str:
    """Renders the Vision Cluster Telemetry card for the sidebar."""
    if endpoints is None:
        endpoints = settings.ollama_vision_endpoints

    node_count = len(endpoints) if endpoints else 1
    rows_html = []

    if endpoints:
        for idx, ep in enumerate(endpoints):
            name = "Host" if idx == 0 else f"Worker {idx}"
            model_tag = ep.model.split(":")[0] if ":" in ep.model else ep.model
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
                             color: #10b981; font-weight: 500;">Ready</span>
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
    filename: str, risk: str, score: int, fatal_count: int, warn_count: int, page_count: int
) -> str:
    """Renders the top summary telemetry pill bar matching Stitch UI."""
    risk_color = (
        "#ef4444" if risk.upper() == "HIGH" else "#f59e0b" if risk.upper() == "MED" else "#10b981"
    )
    risk_bg = (
        "#fee2e2" if risk.upper() == "HIGH" else "#fef3c7" if risk.upper() == "MED" else "#d1fae5"
    )
    risk_text = (
        "#991b1b" if risk.upper() == "HIGH" else "#92400e" if risk.upper() == "MED" else "#065f46"
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
