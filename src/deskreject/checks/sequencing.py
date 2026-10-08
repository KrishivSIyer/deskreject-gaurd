
from deskreject.checks.base import Context, register_check
from deskreject.ingest.mentions import find_mentions
from deskreject.models import Finding, ParsedDoc, Severity
from deskreject.presets import Preset


class SequencingCheck:
    name = "sequencing"
    priority = "P0"

    def run(self, doc: ParsedDoc, preset: Preset, ctx: Context) -> list[Finding]:
        findings: list[Finding] = []
        
        # If doc.mentions is empty, parse it here
        mentions = doc.mentions
        if not mentions and doc.blocks:
            mentions = find_mentions(doc.blocks, doc.captions, doc.references_start)

        # Handle `??` unresolved refs everywhere (number=0)
        for mention in mentions:
            if mention.number == 0:
                findings.append(Finding(
                    code="SEQ_UNRESOLVED_REF",
                    check=self.name,
                    severity=Severity.fatal,
                    title="Unresolved reference",
                    detail="A literal '??' was found where a reference should be.",
                    page=mention.page,
                    bbox=mention.bbox,
                    evidence="??"
                ))

        for kind in ["figure", "table"]:
            # Gather all body mentions (not in caption, not after references, ignoring number 0)
            body_mentions = [m for m in mentions if m.kind == kind and not m.in_caption and not m.after_references and m.number > 0]
            
            # 1. First-mention order
            if preset.sequencing.require_in_order:
                seen_numbers = set()
                highest_seen = 0
                for mention in body_mentions:
                    num = mention.number
                    if num not in seen_numbers:
                        if num > highest_seen + 1:
                            # Mentioned out of order! 
                            findings.append(Finding(
                                code="SEQ_OUT_OF_ORDER",
                                check=self.name,
                                severity=Severity.warning,
                                title=f"{kind.title()} mentioned out of order",
                                detail=f"First mention of {kind} {num} comes before first mention of {highest_seen + 1}.",
                                page=mention.page,
                                bbox=mention.bbox,
                                evidence=f"{kind} {num}"
                            ))
                        seen_numbers.add(num)
                        highest_seen = max(highest_seen, num)

            # 2. Orphans (mention with no caption)
            caption_numbers = {c.number for c in doc.captions if c.kind == kind}
            for mention in body_mentions:
                if mention.number not in caption_numbers:
                    findings.append(Finding(
                        code="SEQ_ORPHAN_REF",
                        check=self.name,
                        severity=Severity.fatal,
                        title=f"Orphan {kind} reference",
                        detail=f"Mention of {kind} {mention.number} that does not exist.",
                        page=mention.page,
                        bbox=mention.bbox,
                        evidence=f"{kind} {mention.number}",
                        figure_id=f"{kind.title()} {mention.number}" if kind == "figure" else None
                    ))

            # 3. Ghosts (caption with no body mention)
            mentioned_numbers = {m.number for m in body_mentions}
            for cap in [c for c in doc.captions if c.kind == kind]:
                if cap.number not in mentioned_numbers:
                    findings.append(Finding(
                        code="SEQ_GHOST",
                        check=self.name,
                        severity=Severity.warning,
                        title=f"Unreferenced {kind}",
                        detail=f"{kind.title()} {cap.number} has a caption but is never mentioned in the body.",
                        page=cap.page,
                        bbox=cap.bbox,
                        evidence=f"{kind.title()} {cap.number}",
                        figure_id=f"{kind.title()} {cap.number}" if kind == "figure" else None
                    ))

            # 4. Number gap
            if caption_numbers:
                max_num = max(caption_numbers)
                for i in range(1, max_num):
                    if i not in caption_numbers:
                        findings.append(Finding(
                            code="SEQ_NUMBER_GAP",
                            check=self.name,
                            severity=Severity.warning,
                            title=f"Gap in {kind} numbering",
                            detail=f"Missing {kind} {i}.",
                            evidence=f"missing {i}"
                        ))

        return findings

sequencing_check_instance = SequencingCheck()

@register_check
def run_sequencing(doc: ParsedDoc, preset: Preset, ctx: Context) -> list[Finding]:
    return sequencing_check_instance.run(doc, preset, ctx)
