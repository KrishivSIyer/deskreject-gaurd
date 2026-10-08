import re

with open('ui/components.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace render_top_header
new_header = '''def render_top_header() -> str:
    \"\"\"Renders the top navigation and brand ribbon HTML.\"\"\"
    return f\"\"\"
    <div style=\"display: flex; align-items: center; justify-content: space-between;
                padding: 12px 24px; background: #ffffff; border-bottom: 1px solid #e2e8f0;
                margin: -4rem -4rem 1.5rem -4rem; position: sticky; top: 0; z-index: 100;\">
        <div style=\"display: flex; align-items: center; gap: 16px;\">
            <div style=\"display: flex; align-items: center; gap: 8px;\">
                <span class=\"material-symbols-outlined\"
                      style=\"color: #3ba4f6; font-size: 28px;\">verified_user</span>
                <span style=\"font-family: 'Inter', sans-serif; font-size: 18px;
                             font-weight: 700; color: #0f172a; letter-spacing: -0.02em;\">
                    DeskReject Guard
                </span>
            </div>
        </div>
        <div style=\"display: flex; align-items: center; gap: 12px;\">
            <div style=\"display: inline-flex; align-items: center; gap: 6px;
                        background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0;
                        padding: 4px 12px; border-radius: 9999px; font-family: 'JetBrains Mono',
                        monospace; font-size: 11px; font-weight: 600;\">
                <span class=\"material-symbols-outlined\" style=\"font-size: 14px;\">lock</span>
                100% LOCAL AUDIT
            </div>
        </div>
    </div>
    \"\"\"
'''
content = re.sub(r'def render_top_header\(.*?</div>\s+</div>\s+"""', new_header, content, flags=re.DOTALL)

def repl(match):
    css_content = match.group(1)
    cleaned_css = '\n'.join(line.strip() for line in css_content.splitlines() if line.strip())
    return 'def get_global_css() -> str:\n    """Returns the Auditor Clinical Light design system stylesheet."""\n    return """\n' + cleaned_css + '\n    """'

# Find the entire return string of get_global_css
content = re.sub(r'def get_global_css\(\) -> str:\n\s+"""Returns.*?stylesheet."""\n\s+return """(.*?)"""', 
                 repl, 
                 content, flags=re.DOTALL)

with open('ui/components.py', 'w', encoding='utf-8') as f:
    f.write(content)
