import importlib
import logging
from collections.abc import Callable
from typing import Protocol

from pydantic import BaseModel

from deskreject.models import Finding, ParsedDoc, Preset


class Context(BaseModel):
    vision: object | None = None
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


def run_all(doc: ParsedDoc, preset: Preset, ctx: Context) -> list[Finding]:
    modules = [
        "deskreject.checks.figure_caption",
        "deskreject.checks.anonymity_text",
        "deskreject.checks.anonymity_vision",
        "deskreject.checks.sequencing",
        "deskreject.checks.statements",
        "deskreject.checks.legibility",
        "deskreject.checks.accessibility"
    ]
    for mod in modules:
        try:
            importlib.import_module(mod)
        except ImportError:
            pass

    all_findings = []
    for check_class_or_func in get_all_checks():
        try:
            if hasattr(check_class_or_func, "run"):
                res = check_class_or_func.run(doc, preset, ctx)
            else:
                res = check_class_or_func(doc, preset, ctx)
            all_findings.extend(res)
        except Exception as e:  # noqa: BLE001
            logging.getLogger(__name__).error(f"Error running check {check_class_or_func}: {e}")
            all_findings.append(Finding(
                code="SYS_CHECK_ERROR",
                check="system",
                severity="info",
                title="Check failed",
                detail=str(e)
            ))
    return all_findings
