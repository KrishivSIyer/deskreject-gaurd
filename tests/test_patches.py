from pathlib import Path

from deskreject.models import Finding, Severity
from deskreject.patches.latex import check_braces, generate_patches
from deskreject.presets import load_preset


def test_latex_patches():
    tex_path = Path(__file__).parent.parent / "samples" / "bad_paper.tex"
    with open(tex_path, "r", encoding="utf-8") as f:
        original_tex = f.read()
        
    preset = load_preset("neurips-style-double-blind")
    
    findings = [
        Finding(code="ANON_CLASS", check="anon", severity=Severity.fatal, title="", detail="", patch_key="anon_class"),
        Finding(code="ANON_AUTHOR", check="anon", severity=Severity.fatal, title="", detail="", patch_key="anon_author"),
        Finding(code="ANON_URL", check="anon", severity=Severity.fatal, title="", detail="", patch_key="anon_url", evidence="https://github.com/rao-lab/deskproject"),
        Finding(code="ANON_ACK", check="anon", severity=Severity.fatal, title="", detail="", patch_key="anon_ack"),
        Finding(code="STMT_MISSING_DATA", check="stmt", severity=Severity.fatal, title="", detail="", patch_key="add_statement:data_availability"),
        Finding(code="LEG_FONT_TOO_SMALL", check="leg", severity=Severity.fatal, title="", detail="", patch_key="fig_width"),
    ]
    
    patches = generate_patches(original_tex, findings, preset)
    
    # Verify patches were generated
    assert len(patches) > 0
    
    # We can reconstruct the patched text by looking at the diffs or just modifying the text
    # Let's apply the replacements directly in the test to check the final text, 
    # or rely on a patch application library.
    # Actually, a simpler way to test the result is to write a simple patch applier.
    # But difflib unified_diff is meant for humans/patch tool.
    # We can just run generate_patches again on subsets to check individual changes.
    
    # 1. anon_class
    p_class = generate_patches(original_tex, [findings[0]], preset)
    assert len(p_class) == 1
    assert "anonymous" in p_class[0].diff # assuming neurips preset adds 'anonymous'
    
    # 2. anon_author
    p_author = generate_patches(original_tex, [findings[1]], preset)
    assert len(p_author) == 1
    assert "\\author{\\textless Anonymous Authors\\textgreater}" in p_author[0].diff or "Anonymous" in p_author[0].diff
    
    # 3. anon_url
    p_url = generate_patches(original_tex, [findings[2]], preset)
    assert len(p_url) == 1
    assert preset.latex.anonymous_repo_url in p_url[0].diff
    
    # 4. anon_ack
    p_ack = generate_patches(original_tex, [findings[3]], preset)
    assert len(p_ack) == 1
    assert "% \\section{Acknowledgements}" in p_ack[0].diff or "% \\section*{Acknowledgement" in p_ack[0].diff
    
    # 5. add_statement
    p_stmt = generate_patches(original_tex, [findings[4]], preset)
    assert len(p_stmt) == 1
    assert "\\section*{Data Availability}" in p_stmt[0].diff
    
    # 6. fig_width
    p_fig = generate_patches(original_tex, [findings[5]], preset)
    assert len(p_fig) == 1
    assert "\\columnwidth" in p_fig[0].diff
    
    # Check braces on the final tex after applying all patches
    
    # Actually, a simpler way is just to sequentially apply the replacements 
    # to original_tex to simulate patch application, or write a patch applier.
    # Since unified_diff is standard, we can use patch utility if available, 
    # but Windows might not have `patch`.
    # Let's just modify latex.py to export a helper `apply_all(tex, findings, preset)` 
    # or we can just run the same logic here to get the final text.
    final_tex = original_tex
    
    # 1. anon_class
    import re
    match = re.search(r"\\documentclass(?:\[(.*?)\])?\{(.*?)\}", final_tex)
    if match:
        old = match.group(0)
        existing = match.group(1)
        cls = match.group(2)
        added = ",".join(preset.latex.class_options_add)
        opts = existing + "," + added if existing else added
        final_tex = final_tex.replace(old, f"\\documentclass[{opts}]{{{cls}}}")
        
    # 2. anon_author
    from deskreject.patches.latex import replace_balanced_braces
    final_tex = replace_balanced_braces(final_tex, "\\author", preset.latex.author_placeholder)
    
    # 3. anon_url
    final_tex = final_tex.replace("https://github.com/rao-lab/deskproject", preset.latex.anonymous_repo_url)
    
    # 4. anon_ack
    lines = final_tex.splitlines(keepends=True)
    new_lines = []
    in_ack = False
    for line in lines:
        if re.search(r"\\section\*?\{Acknowledgements?\}", line, re.IGNORECASE):
            in_ack = True
            new_lines.append("% " + line)
            continue
        if in_ack:
            if line.strip() == "" or line.startswith(("\\section", "\\begin")):
                in_ack = False
                new_lines.append(line)
            else:
                new_lines.append("% " + line)
        else:
            new_lines.append(line)
    final_tex = "".join(new_lines)
    
    # 5. add_statement
    match = re.search(r"\\begin\{thebibliography\}|\\bibliography\{", final_tex)
    if match:
        idx = match.start()
        final_tex = final_tex[:idx] + "\n\\section*{Data Availability}\n[Add Data Availability here]\n\n" + final_tex[idx:]
        
    # 6. fig_width
    final_tex = re.sub(
        r"\\includegraphics\[width=[^\]]+\]",
        r"\\includegraphics[width=\\columnwidth]",
        final_tex
    )
    
    assert check_braces(final_tex)
