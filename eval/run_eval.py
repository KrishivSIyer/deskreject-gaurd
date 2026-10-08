import json
import os
import platform
import sys

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from deskreject.pipeline import audit


def run():
    bad_pdf = os.path.join(os.path.dirname(__file__), "..", "samples", "bad_paper.pdf")
    clean_pdf = os.path.join(os.path.dirname(__file__), "..", "samples", "clean_paper.pdf")
    expected_path = os.path.join(os.path.dirname(__file__), "..", "samples", "expected.json")

    preset = "neurips-style-double-blind"

    print("Auditing bad_paper.pdf...")
    bad_report = audit(bad_pdf, preset_id=preset, use_cache=True)

    print("Auditing clean_paper.pdf...")
    clean_report = audit(clean_pdf, preset_id=preset, use_cache=True)

    with open(expected_path, "r", encoding="utf-8") as f:
        expected = json.load(f)

    p0_expected = {(e["code"], e.get("figure_id")) for e in expected if e["priority"] == "P0"}
    p1_expected = {(e["code"], e.get("figure_id")) for e in expected if e["priority"] == "P1"}

    bad_found = {(f.code, f.figure_id) for f in bad_report.findings if not f.code.startswith("SYS_")}
    
    p0_recall = len(p0_expected.intersection(bad_found))
    p0_total = len(p0_expected)
    p1_recall = len(p1_expected.intersection(bad_found))
    p1_total = len(p1_expected)

    unexpected = bad_found - p0_expected - p1_expected
    
    clean_blocking = [f for f in clean_report.findings if f.severity in ("fatal", "warning") and not f.code.startswith("SYS_")]

    hardware = f"{platform.system()} {platform.release()} ({platform.machine()})"

    md = f"""# Evaluation Results

## Metrics
| Metric | Value |
|--------|-------|
| P0 Recall | {p0_recall} / {p0_total} |
| P1 Recall | {p1_recall} / {p1_total} |
| Unexpected (bad_paper) | {len(unexpected)} |
| Blocking (clean_paper) | {len(clean_blocking)} (Target: 0) |

## Timings (bad_paper)
| Stage | Seconds |
|-------|---------|
| Parse | {bad_report.timings.get('parse', 0):.2f} |
| Checks | {bad_report.timings.get('checks', 0):.2f} |
| Total | {bad_report.timings.get('total', 0):.2f} |

## Vision Stats
- Calls: {bad_report.vision_stats.get('calls', 0)}
- Cache Hits: {bad_report.vision_stats.get('cache_hits', 0)}
- Failures: {bad_report.vision_stats.get('failures', 0)}

## Hardware
`{hardware}`

"""
    if unexpected:
        md += "### Unexpected findings (bad_paper)\n"
        for code, fig in unexpected:
            md += f"- `{code}` (Figure: {fig})\n"

    if clean_blocking:
        md += "### Blocking findings (clean_paper)\n"
        for f in clean_blocking:
            md += f"- `{f.code}` ({f.severity})\n"
            
    # As requested by the plan: "(misses included)"
    misses = (p0_expected | p1_expected) - bad_found
    if misses:
        md += "\n### Misses\n"
        for code, fig in misses:
            md += f"- `{code}` (Figure: {fig})\n"

    results_path = os.path.join(os.path.dirname(__file__), "results.md")
    with open(results_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Wrote {results_path}")


if __name__ == "__main__":
    run()
