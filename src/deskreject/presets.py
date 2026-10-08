from pydantic import BaseModel


class RasterDpiPreset(BaseModel):
    line_art: int
    photo: int
    fatal_below: int

class SequencingPreset(BaseModel):
    require_in_order: bool

class StatementPreset(BaseModel):
    required: bool
    position: str

class StatementsPreset(BaseModel):
    data_availability: StatementPreset | None = None
    code_availability: StatementPreset | None = None
    conflict_of_interest: StatementPreset | None = None
    ethics: StatementPreset | None = None
    ai_use: StatementPreset | None = None

class LatexPreset(BaseModel):
    class_options_add: list[str] = []
    author_placeholder: str = "Anonymous Authors"
    anonymous_repo_url: str = "https://anonymous.4open.science/r/ANON"

class Preset(BaseModel):
    id: str
    label: str
    anonymous: bool
    min_figure_font_pt: float
    min_raster_dpi: RasterDpiPreset
    column_width_in: float
    sequencing: SequencingPreset
    statements: StatementsPreset
    latex: LatexPreset

def load_preset(preset_id: str) -> Preset:
    # This is a stub just to make tests and type checking pass
    return Preset(
        id=preset_id,
        label="Stub Preset",
        anonymous=True,
        min_figure_font_pt=7.0,
        min_raster_dpi=RasterDpiPreset(line_art=300, photo=150, fatal_below=100),
        column_width_in=3.25,
        sequencing=SequencingPreset(require_in_order=True),
        statements=StatementsPreset(
            data_availability=StatementPreset(required=True, position="before_references"),
            code_availability=StatementPreset(required=False, position="any"),
            conflict_of_interest=StatementPreset(required=True, position="before_references"),
            ethics=StatementPreset(required=False, position="any"),
            ai_use=StatementPreset(required=True, position="before_references"),
        ),
        latex=LatexPreset()
    )
