from typing import Protocol

from pydantic import BaseModel

from deskreject.models import Finding, ParsedDoc
from deskreject.presets import Preset


class Context(BaseModel):
    vision: object | None = None      # VisionPool or None when vision is disabled
    use_cache: bool = True
    tex: str | None = None
    # Settings and logger can be attached dynamically if needed

class Check(Protocol):
    name: str
    priority: str  # P0 | P1 | P2
    def run(self, doc: ParsedDoc, preset: Preset, ctx: Context) -> list[Finding]: ...

_REGISTRY: list[Check] = []

def register_check(func) -> Check:
    _REGISTRY.append(func)
    return func

def get_all_checks() -> list[Check]:
    return _REGISTRY
