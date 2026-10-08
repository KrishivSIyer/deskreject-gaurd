import typing

from deskreject.checks.base import Context, register_check
from deskreject.models import Finding, ParsedDoc, Severity
from deskreject.presets import Preset


class StatementsCheck:
    name = "statements"
    priority = "P0"

    SYNONYMS: typing.ClassVar[dict[str, list[str]]] = {
        "data_availability": ["data availability", "availability of data", "data and code availability", "data sharing"],
        "code_availability": ["code availability", "software availability", "code and data"],
        "conflict_of_interest": ["conflict of interest", "conflicts of interest", "competing interests", "declaration of interest", "disclosure of interest"],
        "ethics": ["ethics", "ethical", "institutional review board", "irb", "informed consent", "animal care"],
        "ai_use": ["generative ai", "large language model", "llm", "ai-assisted", "use of ai", "ai usage", "ai disclosure"]
    }

    def run(self, doc: ParsedDoc, preset: Preset, ctx: Context) -> list[Finding]:
        findings: list[Finding] = []
        
        # Identify back matter boundaries
        conclusion_idx = -1
        references_idx = len(doc.blocks)
        
        for i, h in enumerate(doc.headings):
            if "conclusion" in h.norm:
                # find the block index roughly corresponding to this heading
                for j, b in enumerate(doc.blocks):
                    if b.page == h.page and b.bbox == h.bbox:
                        conclusion_idx = j
                        break
            if "reference" in h.norm:
                for j, b in enumerate(doc.blocks):
                    if b.page == h.page and b.bbox == h.bbox:
                        references_idx = j
                        break
        
        if conclusion_idx == -1:
            # If no Conclusion, last 35% of the body
            conclusion_idx = int(len(doc.blocks) * 0.65)
        
        # Create a single text string for back matter to search within
        back_matter_blocks = [b for i, b in enumerate(doc.blocks) if conclusion_idx <= i < references_idx]
        back_matter_text = " ".join(b.text.lower() for b in back_matter_blocks)
        
        statements_config = preset.statements
        for stmt_id, synonyms in self.SYNONYMS.items():
            config = getattr(statements_config, stmt_id, None)
            if not config:
                continue

            found = False
            found_after_references = False
            
            # 1. Search headings
            for h in doc.headings:
                if any(syn in h.norm for syn in synonyms):
                    found = True
                    # Check position
                    for j, b in enumerate(doc.blocks):
                        if b.page == h.page and b.bbox == h.bbox:
                            if j >= references_idx:
                                found_after_references = True
                            break
                    break

            # 2. Search back matter sentences if not found in headings
            if not found:
                for syn in synonyms:
                    if syn in back_matter_text:
                        found = True
                        break
            
            # 3. Search after references if still not found and we care about misplaced ones
            if not found:
                after_ref_blocks = [b for i, b in enumerate(doc.blocks) if i >= references_idx]
                after_ref_text = " ".join(b.text.lower() for b in after_ref_blocks)
                for syn in synonyms:
                    if syn in after_ref_text:
                        found = True
                        found_after_references = True
                        break

            if not found:
                severity = Severity.fatal if config.required else Severity.warning
                findings.append(Finding(
                    code=f"STMT_MISSING_{stmt_id.upper()}",
                    check=self.name,
                    severity=severity,
                    title=f"Missing {stmt_id.replace('_', ' ')} statement",
                    detail=f"No statement regarding {stmt_id.replace('_', ' ')} was found.",
                    fix_hint=f"Add a '{stmt_id.replace('_', ' ').title()}' section before the references.",
                    patch_key=f"add_statement:{stmt_id}"
                ))
            elif found_after_references and config.position == "before_references":
                findings.append(Finding(
                    code=f"STMT_MISPLACED_{stmt_id.upper()}",
                    check=self.name,
                    severity=Severity.warning,
                    title=f"Misplaced {stmt_id.replace('_', ' ')} statement",
                    detail=f"The {stmt_id.replace('_', ' ')} statement appears after the references.",
                    fix_hint="Move the statement before the references section."
                ))

        return findings

statements_check_instance = StatementsCheck()

@register_check
def run_statements(doc: ParsedDoc, preset: Preset, ctx: Context) -> list[Finding]:
    return statements_check_instance.run(doc, preset, ctx)
