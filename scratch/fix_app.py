
with open('ui/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('                st.session_state.ai_summary = None\n            st.session_state.report = audit(', '                st.session_state.ai_summary = None\n                st.session_state.report = audit(')
content = content.replace('            st.session_state.ai_summary = None\n            st.session_state.report = audit(', '            st.session_state.ai_summary = None\n            st.session_state.report = audit(') # 12 spaces is correct for the first one

with open('ui/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
