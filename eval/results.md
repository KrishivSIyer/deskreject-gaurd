# Evaluation Results

## Metrics
| Metric | Value |
|--------|-------|
| P0 Recall | 15 / 16 |
| P1 Recall | 0 / 3 |
| Unexpected (bad_paper) | 8 |
| Blocking (clean_paper) | 9 (Target: 0) |

## Timings (bad_paper)
| Stage | Seconds |
|-------|---------|
| Parse | 0.03 |
| Checks | 0.08 |
| Total | 0.24 |

## Vision Stats
- Calls: 6
- Cache Hits: 0
- Failures: 6

## Hardware
`Windows 11 (AMD64)`

### Unexpected findings (bad_paper)
- `LEG_FONT_TOO_SMALL` (Figure: Figure 1)
- `SEQ_GHOST` (Figure: Figure 3)
- `LEG_RASTER_LOW_DPI` (Figure: None)
- `SEQ_GHOST` (Figure: None)
- `FIG_PANEL_UNREFERENCED` (Figure: Figure 5)
- `FIG_PANEL_UNREFERENCED` (Figure: Figure 4)
- `SEQ_GHOST` (Figure: Figure 5)
- `STMT_MISSING_CODE_AVAILABILITY` (Figure: None)
### Blocking findings (clean_paper)
- `STMT_MISSING_AI_USE` (Severity.fatal)
- `LEG_RASTER_LOW_DPI` (Severity.fatal)
- `ANON_METADATA_AUTHOR` (Severity.warning)
- `ANON_METADATA_AUTHOR` (Severity.warning)
- `STMT_MISSING_CODE_AVAILABILITY` (Severity.warning)
- `STMT_MISSING_ETHICS` (Severity.warning)
- `LEG_FONT_TOO_SMALL` (Severity.warning)
- `FIG_PANEL_UNREFERENCED` (Severity.warning)
- `FIG_PANEL_UNREFERENCED` (Severity.warning)

### Misses
- `LEG_RASTER_LOW_DPI` (Figure: Figure 2)
- `ACC_CB_INDISTINGUISHABLE` (Figure: Figure 5)
- `ANON_LOGO_IN_FIGURE` (Figure: Figure 3)
- `LEG_FONT_TOO_SMALL` (Figure: Figure 4)
