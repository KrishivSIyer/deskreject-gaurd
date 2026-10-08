from deskreject.models import Finding
from deskreject.report import finalize


def test_finalize_deduplicates_and_sorts():
    f1 = Finding(
        code="C1", check="system", severity="info", title="Info 1", detail="", page=2, bbox=(0, 100, 10, 110)
    )
    f2 = Finding(
        code="C1", check="system", severity="info", title="Info 1", detail="", page=2, bbox=(0, 100, 10, 110)
    )  # duplicate
    f3 = Finding(
        code="F1", check="system", severity="fatal", title="Fatal 1", detail="", page=1, bbox=(0, 50, 10, 60)
    )
    f4 = Finding(
        code="W1", check="system", severity="warning", title="Warn 1", detail="", page=1, bbox=(0, 200, 10, 210)
    )

    rep = finalize([f1, f2, f3, f4], "preset1", "file.pdf", 5, {}, {}, 0)

    assert len(rep.findings) == 3
    # Order should be fatal, warning, info
    assert rep.findings[0].severity == "fatal"
    assert rep.findings[1].severity == "warning"
    assert rep.findings[2].severity == "info"

    # Numbers should be 1, 2, 3
    assert rep.findings[0].number == 1
    assert rep.findings[1].number == 2
    assert rep.findings[2].number == 3

    assert rep.risk == "HIGH"
    assert rep.counts["fatal"] == 1
    assert rep.counts["warning"] == 1
    assert rep.counts["info"] == 1


def test_risk_levels():
    rep_low = finalize([], "preset", "f", 1, {}, {}, 0)
    assert rep_low.risk == "LOW"

    rep_med = finalize(
        [Finding(code="W", check="sys", severity="warning", title="", detail="")], "preset", "f", 1, {}, {}, 0
    )
    assert rep_med.risk == "MEDIUM"

