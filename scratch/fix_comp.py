
with open('ui/components.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('errors_text = "\\n".join', 'errors_text = "\\\n".join')
content = content.replace('errors_text = "\n".join', 'errors_text = "\\n".join')

with open('ui/components.py', 'w', encoding='utf-8') as f:
    f.write(content)
