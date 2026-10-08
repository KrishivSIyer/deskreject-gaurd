import re

from deskreject.checks.base import Context, register_check
from deskreject.models import Finding, ParsedDoc, Severity
from deskreject.presets import Preset


class AnonymityTextCheck:
    name = "anonymity"
    priority = "P0"

    def run(self, doc: ParsedDoc, preset: Preset, ctx: Context) -> list[Finding]:
        if not preset.anonymous:
            return []

        findings: list[Finding] = []

        # 1. Metadata
        known_producers = {"latex", "pdftex", "microsoft word", "chrome", "matplotlib"}
        for key in ["author", "creator", "title"]:
            val = doc.metadata.get(key, "").strip()
            if val:
                val_lower = val.lower()
                if not any(prod in val_lower for prod in known_producers) and "anonymous" not in val_lower:
                    severity = Severity.fatal if key == "author" else Severity.warning
                    findings.append(Finding(
                        code="ANON_METADATA_AUTHOR",
                        check=self.name,
                        severity=severity,
                        title=f"Metadata {key} set",
                        detail=f"The PDF {key} metadata field contains identifying information.",
                        evidence=val,
                        fix_hint="Clear the metadata when exporting the PDF."
                    ))

        # 2. Author block
        for block in doc.front_matter.author_blocks:
            if "anonymous" not in block.text.lower():
                findings.append(Finding(
                    code="ANON_AUTHOR_BLOCK",
                    check=self.name,
                    severity=Severity.fatal,
                    title="Non-anonymous author block",
                    detail="Front matter author block contains non-anonymous text.",
                    page=block.page,
                    bbox=block.bbox,
                    evidence=block.text,
                    patch_key="anon_author"
                ))

        # 3. Email
        email_regex = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
        email_matches = set()
        for block in doc.blocks:
            for match in email_regex.finditer(block.text):
                email = match.group(0)
                if email not in email_matches:
                    email_matches.add(email)
                    findings.append(Finding(
                        code="ANON_EMAIL",
                        check=self.name,
                        severity=Severity.fatal,
                        title="Email address found",
                        detail="An email address is present in the text.",
                        page=block.page,
                        bbox=block.bbox,
                        evidence=email
                    ))

        # 4. Affiliation in front matter
        affil_regex = re.compile(r"\b(University|Institute|Laboratory|Lab|Department of|School of|College)\b", re.IGNORECASE)
        for block in doc.front_matter.author_blocks:
            match = affil_regex.search(block.text)
            if match:
                findings.append(Finding(
                    code="ANON_AFFILIATION",
                    check=self.name,
                    severity=Severity.fatal,
                    title="Institution name in front matter",
                    detail="Institutional affiliation found in front matter.",
                    page=block.page,
                    bbox=block.bbox,
                    evidence=block.text
                ))

        # 5. Repo URL
        repo_regex = re.compile(r"(github\.com/[\w.-]+|gitlab\.com/[\w.-]+|huggingface\.co/[\w.-]+)", re.IGNORECASE)
        repo_urls = set()
        
        def check_url(url: str, page: int, bbox: tuple):
            url_lower = url.lower()
            if "anonymous" in url_lower or "anon" in url_lower or "anonymous.4open.science" in url_lower:
                return
            match = repo_regex.search(url_lower)
            if match and url not in repo_urls:
                repo_urls.add(url)
                findings.append(Finding(
                        code="ANON_REPO_URL",
                        check=self.name,
                        severity=Severity.fatal,
                        title="Non-anonymous code repository",
                        detail="Found a link to a repository that is not anonymized.",
                        page=page,
                        bbox=bbox,
                        evidence=url,
                        patch_key="anon_url"
                    ))

        for link in doc.links:
            check_url(link.uri, link.page, link.bbox)
        
        for block in doc.blocks:
            for word in block.text.split():
                if "github.com" in word.lower() or "gitlab.com" in word.lower() or "huggingface.co" in word.lower():
                    check_url(word, block.page, block.bbox)

        # 6. Self-citation
        self_cite_patterns = [
            r"our (previous|prior|earlier|recent) (work|paper|study|publication)",
            r"we (previously|earlier) (showed|proposed|introduced|presented)",
            r"as we (showed|proposed|described) in \[\d+\]",
            r"our (own )?(work|paper) \[\d+"
        ]
        self_cite_regex = re.compile("|".join(self_cite_patterns), re.IGNORECASE)
        for block in doc.blocks:
            # Note: A real implementation might segment into sentences.
            for match in self_cite_regex.finditer(block.text):
                findings.append(Finding(
                    code="ANON_SELF_CITE",
                    check=self.name,
                    severity=Severity.warning,
                    title="Self-citation phrasing",
                    detail="Found phrasing indicating a self-citation.",
                    page=block.page,
                    bbox=block.bbox,
                    evidence=match.group(0)
                ))

        # 7. Acknowledgements
        for heading in doc.headings:
            if heading.norm in ["acknowledgements", "acknowledgments", "funding"]:
                findings.append(Finding(
                    code="ANON_ACK",
                    check=self.name,
                    severity=Severity.warning,
                    title="Acknowledgements section",
                    detail="An acknowledgements or funding section is present.",
                    page=heading.page,
                    bbox=heading.bbox,
                    evidence=heading.text,
                    patch_key="anon_ack"
                ))

        return findings

anonymity_text_check_instance = AnonymityTextCheck()

@register_check
def run_anonymity_text(doc: ParsedDoc, preset: Preset, ctx: Context) -> list[Finding]:
    return anonymity_text_check_instance.run(doc, preset, ctx)
