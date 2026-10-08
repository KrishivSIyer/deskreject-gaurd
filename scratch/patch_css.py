import re

with open('ui/components.py', 'r', encoding='utf-8') as f:
    content = f.read()

def repl(match):
    css = match.group(0)
    return '\n'.join(line.strip() for line in css.splitlines() if line.strip())

# Find the entire return string of get_global_css
content = re.sub(r'def get_global_css\(\) -> str:\n\s+"""Returns.*?stylesheet."""\n\s+return """(.*?)"""', 
                 lambda m: 'def get_global_css() -> str:\n    """Returns the Auditor Clinical Light design system stylesheet."""\n    return """' + repl(m) + '"""', 
                 content, flags=re.DOTALL)

with open('ui/components.py', 'w', encoding='utf-8') as f:
    f.write(content)
