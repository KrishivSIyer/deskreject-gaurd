
with open('src/deskreject/patches/latex.py', 'r') as f:
    content = f.read()

content = content.replace('class Patch(BaseModel):\n    file: str\n    diff: str', '')
content = content.replace('from deskreject.models import Finding', 'from deskreject.models import Finding, Patch')

content = content.replace('patches.append(Patch(file="main.tex", diff=diff))', 'patches.append(Patch(key="", title="LaTeX Patch", applies_to=[], before="", after="", diff=diff))')

content = content.replace('patches.append(Patch(key="", title="LaTeX Patch", applies_to=[], before="", after="", diff=diff))', 'patches.append(Patch(key="anon_class", title="Anonymize Document Class", applies_to=["ANON_CLASS"], before="", after="", diff=diff))', 1)
content = content.replace('patches.append(Patch(key="", title="LaTeX Patch", applies_to=[], before="", after="", diff=diff))', 'patches.append(Patch(key="anon_author", title="Anonymize Author", applies_to=["ANON_AUTHOR_BLOCK"], before="", after="", diff=diff))', 1)
content = content.replace('patches.append(Patch(key="", title="LaTeX Patch", applies_to=[], before="", after="", diff=diff))', 'patches.append(Patch(key="anon_url", title="Anonymize URLs", applies_to=["ANON_REPO_URL"], before="", after="", diff=diff))', 1)
content = content.replace('patches.append(Patch(key="", title="LaTeX Patch", applies_to=[], before="", after="", diff=diff))', 'patches.append(Patch(key="anon_ack", title="Anonymize Acknowledgements", applies_to=["ANON_ACK"], before="", after="", diff=diff))', 1)
content = content.replace('patches.append(Patch(key="", title="LaTeX Patch", applies_to=[], before="", after="", diff=diff))', 'patches.append(Patch(key=k, title=f"Add {title} Statement", applies_to=["STMT_MISSING_" + stmt_id.upper()], before="", after="", diff=diff))', 1)
content = content.replace('patches.append(Patch(key="", title="LaTeX Patch", applies_to=[], before="", after="", diff=diff))', 'patches.append(Patch(key="fig_width", title="Fix Figure Width", applies_to=["FIG_WIDTH"], before="", after="", diff=diff))', 1)

with open('src/deskreject/patches/latex.py', 'w') as f:
    f.write(content)
