
with open('ui/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('st.session_state.report = audit(', 'st.session_state.ai_summary = None\n            st.session_state.report = audit(')

# Also add ai_summary init at top
content = content.replace('if "report" not in st.session_state:', 'if "ai_summary" not in st.session_state:\n    st.session_state.ai_summary = None\nif "report" not in st.session_state:')

with open('ui/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
