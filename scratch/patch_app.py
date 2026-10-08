
with open('ui/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace from # Main Workspace Header to end
new_end = '''# Main Workspace Header
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
'''

parts = content.split('# Main Workspace Header')
content = parts[0] + new_end

with open('ui/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
