from deskreject.checks.base import get_all_checks, register_check
from deskreject.models import Finding, Report
from deskreject.presets import load_preset


def test_preset_loading():
    preset = load_preset("neurips-style-double-blind")
    assert preset.id == "neurips-style-double-blind"
    assert preset.anonymous is True
    assert preset.statements.data_availability.required is True
    
def test_report_json_roundtrip():
    finding = Finding(
        code="ANON_EMAIL",
        check="anonymity",
        severity="fatal",
        title="Email found",
        detail="Found an email",
        page=1,
        evidence="test@example.com"
    )
    report = Report(
        preset="neurips-style-double-blind",
        file_name="test.pdf",
        page_count=4,
        findings=[finding],
        risk="HIGH",
        counts={"fatal": 1, "warning": 0, "info": 0},
        timings={"anonymity": 0.1},
        vision_stats={"calls": 0},
        external_requests_blocked=0
    )
    
    report_json = report.model_dump_json()
    loaded_report = Report.model_validate_json(report_json)
    
    assert loaded_report.preset == "neurips-style-double-blind"
    assert loaded_report.findings[0].code == "ANON_EMAIL"

def test_check_registry():
    @register_check
    def check_a(): pass
    
    @register_check
    def check_b(): pass
    
    checks = get_all_checks()
    assert check_a in checks
    assert check_b in checks
    assert checks.index(check_a) < checks.index(check_b)
