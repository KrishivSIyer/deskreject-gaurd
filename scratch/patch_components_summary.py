import re

with open('ui/components.py', 'r', encoding='utf-8') as f:
    content = f.read()

summary_func = '''
def generate_findings_summary(report: Report) -> str:
    from deskreject.config import settings
    from deskreject.netguard import make_client
    
    if not report.findings:
        return "No errors found. The manuscript is good to go!"
    
    errors_text = "\\n".join([f"- {f.code} ({f.severity}): {f.title}. {f.detail}" for f in report.findings])
    prompt = f\"\"\"You are an assistant for DeskReject Guard. Summarize the following manuscript errors in layman's terms. 
Your summary should be one paragraph explaining these errors simply and ending by saying that these are the errors to be fixed and then you are good to go.

Errors:
{errors_text}
\"\"\"
    
    try:
        model_tag, url = settings.text_model.split("@", 1)
        client = make_client(settings, timeout=30.0)
        response = client.post(
            f"{url}/api/generate",
            json={
                "model": model_tag,
                "prompt": prompt,
                "stream": False,
                "system": "You are a helpful assistant.",
            }
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:  # noqa: BLE001
        return f"Could not generate AI summary: {e}"

def render_findings_tab(report: Report | None) -> None:
    \"\"\"Renders the interactive High-Risk Findings diagnostic table with inline evidence.\"\"\"
    if not report or not report.findings:
        st.info("No findings reported. Run an audit to inspect the manuscript for desk-reject flaws.")
        return

    # AI Summary
    st.subheader("AI Summary")
    if "ai_summary" not in st.session_state:
        st.session_state.ai_summary = None
        
    if st.session_state.ai_summary is None:
        with st.spinner("AI is generating a summary of findings..."):
            st.session_state.ai_summary = generate_findings_summary(report)
            
    if st.session_state.ai_summary:
        st.info(st.session_state.ai_summary)
        
    st.divider()

    # Severity and Category Filters
'''

content = re.sub(r'def render_findings_tab\(report: Report \| None\) -> None:\n\s+"""Renders.*?return\n\n\s+# Severity and Category Filters', summary_func.strip(), content, flags=re.DOTALL)

with open('ui/components.py', 'w', encoding='utf-8') as f:
    f.write(content)
