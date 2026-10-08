from collections.abc import Callable
from typing import Protocol

from pydantic import BaseModel

from deskreject.models import Finding, ParsedDoc, Preset


class Context(BaseModel):
    vision: object | None
    use_cache: bool = True
    tex: str | None = None
    # plus logger and settings handles

class Check(Protocol):
    name: str
    priority: str
    def run(self, doc: ParsedDoc, preset: Preset, ctx: Context) -> list[Finding]: ...

_registry: list[Callable] = []

def register_check(func: Callable) -> Callable:
    _registry.append(func)
    return func

def get_all_checks() -> list[Callable]:
    return _registry
