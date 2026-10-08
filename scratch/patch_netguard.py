import re

with open('src/deskreject/netguard.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('if settings.text_model and', 'if getattr(settings, "text_model", None) and')
content = content.replace('if settings.coder_model and', 'if getattr(settings, "coder_model", None) and')

with open('src/deskreject/netguard.py', 'w', encoding='utf-8') as f:
    f.write(content)
