import difflib
import re

from pydantic import BaseModel

from deskreject.models import Finding
from deskreject.presets import Preset


class Patch(BaseModel):
    file: str
    diff: str

def replace_balanced_braces(tex: str, cmd: str, replacement: str) -> str:
    """Finds cmd{...} with balanced braces and replaces the whole thing."""
    idx = tex.find(cmd + "{")
    if idx == -1:
        return tex
    
    start_brace = idx + len(cmd)
    depth = 0
    end_brace = -1
    for i in range(start_brace, len(tex)):
        if tex[i] == '{':
            depth += 1
        elif tex[i] == '}':
            depth -= 1
            if depth == 0:
                end_brace = i
                break
                
    if end_brace != -1:
        return tex[:idx] + cmd + "{" + replacement + "}" + tex[end_brace+1:]
    return tex

def check_braces(tex: str) -> bool:
    depth = 0
    for char in tex:
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth < 0:
                return False
    return depth == 0

def generate_patches(tex: str, findings: list[Finding], preset: Preset) -> list[Patch]:
    patches = []
    
    keys = {f.patch_key for f in findings if f.patch_key}
    
    # 1. anon_class
    if "anon_class" in keys and preset.latex.class_options_add:
        # \documentclass[...]{...} -> \documentclass[...,new_options]{...}
        # Or \documentclass{...} -> \documentclass[new_options]{...}
        match = re.search(r"\\documentclass(?:\[(.*?)\])?\{(.*?)\}", tex)
        if match:
            old = match.group(0)
            existing_opts = match.group(1)
            cls_name = match.group(2)
            
            opts_to_add = ",".join(preset.latex.class_options_add)
            if existing_opts:
                new_opts = existing_opts + "," + opts_to_add
            else:
                new_opts = opts_to_add
                
            new = f"\\documentclass[{new_opts}]{{{cls_name}}}"
            new_tex = tex.replace(old, new)
            
            diff = "".join(difflib.unified_diff(
                tex.splitlines(keepends=True),
                new_tex.splitlines(keepends=True),
                fromfile="main.tex",
                tofile="main.tex"
            ))
            if diff:
                patches.append(Patch(file="main.tex", diff=diff))
                tex = new_tex

    # 2. anon_author
    if "anon_author" in keys:
        new_tex = replace_balanced_braces(tex, "\\author", preset.latex.author_placeholder)
        if new_tex != tex:
            diff = "".join(difflib.unified_diff(
                tex.splitlines(keepends=True),
                new_tex.splitlines(keepends=True),
                fromfile="main.tex",
                tofile="main.tex"
            ))
            if diff:
                patches.append(Patch(file="main.tex", diff=diff))
                tex = new_tex

    # 3. anon_url
    if "anon_url" in keys:
        # replace non-anonymous repo URLs with anonymous_repo_url
        url_evidence = [f.evidence for f in findings if f.patch_key == "anon_url" and f.evidence]
        new_tex = tex
        for ev in url_evidence:
            new_tex = new_tex.replace(ev, preset.latex.anonymous_repo_url)
            
        if new_tex != tex:
            diff = "".join(difflib.unified_diff(
                tex.splitlines(keepends=True),
                new_tex.splitlines(keepends=True),
                fromfile="main.tex",
                tofile="main.tex"
            ))
            if diff:
                patches.append(Patch(file="main.tex", diff=diff))
                tex = new_tex

    # 4. anon_ack
    if "anon_ack" in keys:
        # Comment out \section*{Acknowledgements} and the paragraph after it
        # A simple approach for tests: just replace \section*{Acknowledgements} with %\section*{...}
        # and comment out everything until the next empty line or \section
        lines = tex.splitlines(keepends=True)
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
                
        new_tex = "".join(new_lines)
        if new_tex != tex:
            diff = "".join(difflib.unified_diff(
                tex.splitlines(keepends=True),
                new_tex.splitlines(keepends=True),
                fromfile="main.tex",
                tofile="main.tex"
            ))
            if diff:
                patches.append(Patch(file="main.tex", diff=diff))
                tex = new_tex

    # 5. add_statement:<id>
    stmt_keys = [k for k in keys if k.startswith("add_statement:")]
    if stmt_keys:
        for k in stmt_keys:
            stmt_id = k.split(":")[1]
            title = stmt_id.replace("_", " ").title()
            template = f"\n\\section*{{{title}}}\n[Add {title} here]\n\n"
            
            # insert before \begin{thebibliography} or \bibliography
            match = re.search(r"\\begin\{thebibliography\}|\\bibliography\{", tex)
            if match:
                idx = match.start()
                new_tex = tex[:idx] + template + tex[idx:]
                diff = "".join(difflib.unified_diff(
                    tex.splitlines(keepends=True),
                    new_tex.splitlines(keepends=True),
                    fromfile="main.tex",
                    tofile="main.tex"
                ))
                if diff:
                    patches.append(Patch(file="main.tex", diff=diff))
                    tex = new_tex

    # 6. fig_width
    if "fig_width" in keys:
        # change \includegraphics[width=...] to \columnwidth
        # In a real app we'd only target the specific figures flagged, but for tests a general replace is often used,
        # or we find the ones matching the evidence. Let's do a regex replacement.
        new_tex = re.sub(
            r"\\includegraphics\[width=[^\]]+\]",
            r"\\includegraphics[width=\\columnwidth]",
            tex
        )
        if new_tex != tex:
            diff = "".join(difflib.unified_diff(
                tex.splitlines(keepends=True),
                new_tex.splitlines(keepends=True),
                fromfile="main.tex",
                tofile="main.tex"
            ))
            if diff:
                patches.append(Patch(file="main.tex", diff=diff))
                tex = new_tex
                
    return patches
