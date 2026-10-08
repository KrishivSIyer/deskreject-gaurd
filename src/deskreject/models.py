from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

BBox = tuple[float, float, float, float]  # x0, y0, x1, y1 in PDF points, origin top-left

class Severity(str, Enum):
    fatal = "fatal"
    warning = "warning"
    info = "info"

class Finding(BaseModel):
    code: str                       # from the catalogue below
    check: str                      # figure_caption | anonymity | sequencing | statements | legibility | accessibility | system
    severity: Severity
    title: str                      # one line, shown on the card
    detail: str                     # one to three plain sentences
    page: int | None = None         # 1-based, None means document level
    bbox: BBox | None = None
    evidence: str | None = None     # exact text or numbers that triggered it
    fix_hint: str | None = None
    source: str = "rule"            # rule | vision | llm
    confidence: float = 1.0
    figure_id: str | None = None    # "Figure 3"
    patch_key: str | None = None    # which patch template can fix it
    number: int | None = None       # assigned in finalize, used for overlay badges

class Span(BaseModel):
    page: int
    text: str
    size: float
    bold: bool
    bbox: BBox

class TextBlock(BaseModel):
    page: int
    bbox: BBox
    text: str
    size: float
    bold: bool
    column: int  # 0 left, 1 right, 0 if single column

class ImageRef(BaseModel):
    page: int
    bbox: BBox
    px_w: int
    px_h: int
    xref: int

class LinkRef(BaseModel):
    page: int
    bbox: BBox
    uri: str

class Heading(BaseModel):
    page: int
    bbox: BBox
    text: str
    norm: str   # norm = lowercase, number stripped

class Caption(BaseModel):
    kind: str            # figure | table
    number: int
    page: int
    bbox: BBox
    text: str

class Figure(BaseModel):
    id: str              # "Figure 3"
    number: int
    page: int
    region: BBox
    caption: Caption
    images: list[ImageRef] = []
    spans: list[Span] = []          # text spans inside the region (vector labels, tick labels)

class Mention(BaseModel):
    kind: str            # figure | table
    number: int
    page: int
    bbox: BBox
    in_caption: bool
    after_references: bool

class FrontMatter(BaseModel):
    title: str
    author_blocks: list[TextBlock]
    abstract_start: tuple[int, float] | None   # page, y

class ParsedDoc(BaseModel):
    path: str
    page_sizes: list[tuple[float, float]]
    metadata: dict[str, str]
    body_font_size: float
    two_column: bool
    blocks: list[TextBlock]
    spans: list[Span]
    images: list[ImageRef]
    links: list[LinkRef]
    headings: list[Heading]
    captions: list[Caption]
    figures: list[Figure]
    mentions: list[Mention]
    front_matter: FrontMatter
    references_start: tuple[int, float] | None  # page, y of the References heading

class Patch(BaseModel):
    key: str
    title: str
    applies_to: list[str]   # finding codes
    before: str
    after: str
    diff: str            # unified diff text

class Report(BaseModel):
    preset: str
    file_name: str
    page_count: int
    findings: list[Finding]
    risk: str                                   # LOW | MEDIUM | HIGH
    counts: dict[str, int]                      # fatal, warning, info
    timings: dict[str, float]                   # seconds per stage and per check
    vision_stats: dict                          # calls, cache_hits, failures, per_endpoint
    external_requests_blocked: int
    figure_previews: dict[str, dict[str, str]] = {}   # figure id -> file paths
    patches: list[Patch] = []

class LegibilityPreset(BaseModel):
    line_art: int
    photo: int
    fatal_below: int

class StatementRule(BaseModel):
    required: bool
    position: str

class StatementsPreset(BaseModel):
    data_availability: StatementRule
    code_availability: StatementRule
    conflict_of_interest: StatementRule
    ethics: StatementRule
    ai_use: StatementRule

class SequencingPreset(BaseModel):
    require_in_order: bool

class LatexPreset(BaseModel):
    class_options_add: list[str]
    author_placeholder: str
    anonymous_repo_url: str

class Preset(BaseModel):
    id: str
    label: str
    anonymous: bool
    min_figure_font_pt: float
    min_raster_dpi: LegibilityPreset
    column_width_in: float
    sequencing: SequencingPreset
    statements: StatementsPreset
    latex: LatexPreset | None = None
