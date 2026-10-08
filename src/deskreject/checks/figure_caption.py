import re

from deskreject.checks.base import Context, register_check
from deskreject.models import Finding, ParsedDoc, Severity
from deskreject.presets import Preset


def caption_panel_refs(text: str) -> set[str]:
    """Extract panel references from caption text."""
    refs = set()
    text = text.lower()
    
    # normalize dashes
    text = re.sub(r"[–—]", "-", text)
    
    # 1. Matches ranges like (a)-(c) or (a-c)
    range_regex = re.compile(r"\(([a-h])\)\s*-\s*\(([a-h])\)|\(([a-h])\s*-\s*([a-h])\)")
    for match in range_regex.finditer(text):
        if match.group(1) and match.group(2):
            start, end = match.group(1), match.group(2)
        else:
            start, end = match.group(3), match.group(4)
            
        if start and end and start <= end:
            for char_code in range(ord(start), ord(end) + 1):
                refs.add(chr(char_code))
                
    # 2. Match single items like (a), (b)
    single_regex = re.compile(r"\(([a-h])\)")
    for match in single_regex.finditer(text):
        refs.add(match.group(1))
        
    return refs

class FigureCaptionCheck:
    name = "figure_caption"
    priority = "P0"

    def run(self, doc: ParsedDoc, preset: Preset, ctx: Context) -> list[Finding]:
        findings: list[Finding] = []
        
        # Define panel label matching
        # 1. Standalone label: ^\(?([a-h])\)?[.:]?$
        # 2. Leading label: ^\(([a-h])\)(?:\s+|$)
        label_regex = re.compile(r"^\(?([a-h])\)?[.:]?$|^\(([a-h])\)(?:\s+|$)")

        for fig in doc.figures:
            # 1. Extract referenced labels from caption
            referenced = caption_panel_refs(fig.caption.text)
            
            # 2. Extract visible labels from spans
            # Keep track of coordinates to check order (x, y)
            visible = {}
            for span in fig.spans:
                match = label_regex.match(span.text.lower().strip())
                if match:
                    label = match.group(1) or match.group(2)
                    if label:
                        x0, y0, _, _ = span.bbox
                        visible[label] = (x0, y0)
                        
            source = "rule"
            
            # If no visible spans but has raster images, use vision if available
            if not visible and fig.images and ctx.vision:
                # Mock calling ctx.vision.ask if it exists
                try:
                    # We expect a method like `read_panels` but since it's a test fake we just call it
                    vision_res = ctx.vision.read_panels(doc.path, fig.page, fig.region)  # type: ignore
                    for item in vision_res:
                        if item["confidence"] >= 0.6:
                            visible[item["label"]] = (item["bbox"][0], item["bbox"][1])
                    if visible:
                        source = "vision"
                except AttributeError:
                    pass

            visible_labels = set(visible.keys())
            
            # 3. Check Unreferenced
            unreferenced = visible_labels - referenced
            if unreferenced:
                severity = Severity.warning if not referenced else Severity.fatal
                for label in sorted(unreferenced):
                    findings.append(Finding(
                        code="FIG_PANEL_UNREFERENCED",
                        check=self.name,
                        severity=severity,
                        title="Unreferenced figure panel",
                        detail=f"Panel '{label}' is visible in Figure {fig.number} but not mentioned in its caption.",
                        page=fig.page,
                        bbox=fig.region,
                        evidence=f"({label})",
                        source=source,
                        figure_id=f"Figure {fig.number}"
                    ))
                    
            # 4. Check Missing / Count Mismatch
            missing = referenced - visible_labels
            if missing:
                for label in sorted(missing):
                    findings.append(Finding(
                        code="FIG_PANEL_COUNT_MISMATCH",
                        check=self.name,
                        severity=Severity.fatal,
                        title="Missing figure panel",
                        detail=f"Caption for Figure {fig.number} mentions panel '{label}', but it was not found in the figure.",
                        page=fig.page,
                        bbox=fig.region,
                        evidence=f"({label})",
                        figure_id=f"Figure {fig.number}"
                    ))
                    
            # 5. Check Order
            if visible:
                # Top-to-bottom, left-to-right means sort by Y, then X
                # We need a small tolerance for Y so that items on the same row are sorted by X.
                # A heuristic: group by Y rounded to ~15 points.
                sorted_labels = sorted(visible.keys(), key=lambda l: (round(visible[l][1] / 15.0), visible[l][0]))
                alphabetical_labels = sorted(visible.keys())
                
                if sorted_labels != alphabetical_labels:
                    findings.append(Finding(
                        code="FIG_PANEL_ORDER",
                        check=self.name,
                        severity=Severity.warning,
                        title="Figure panels out of order",
                        detail=f"Panels in Figure {fig.number} do not follow a top-to-bottom, left-to-right order.",
                        page=fig.page,
                        bbox=fig.region,
                        evidence=f"Found: {', '.join(sorted_labels)}",
                        figure_id=f"Figure {fig.number}"
                    ))

        return findings

figure_caption_check_instance = FigureCaptionCheck()

@register_check
def run_figure_caption(doc: ParsedDoc, preset: Preset, ctx: Context) -> list[Finding]:
    return figure_caption_check_instance.run(doc, preset, ctx)
