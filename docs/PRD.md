# DeskReject Guard: Product Requirements

| | |
|---|---|
| Status | Draft v0.1 |
| Last updated | 2026-10-08 |
| Owner | Lane A (Team Lead) |
| Product spec | [`deskreject_guard_product_specification.md`](deskreject_guard_product_specification.md) (original vision, wider than Phase 1) |
| Build plan | [`docs/IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) |

Requirement IDs (`ANON-4`, `SEQ-2`, …) are stable once a milestone using them has started. Reference them in issues, PRs and commits. The build plan's feature IDs (F1 to F13) map to the requirement groups in [§6](#6-scope-and-phases).

---

## 1. Summary

DeskReject Guard is a local pre-flight check for academic manuscripts. An author drops in the compiled PDF, picks the target venue preset, and gets a list of problems that commonly get a submission rejected before a human reads it: author details left in a blinded paper, a figure whose caption skips a panel, figures cited out of order, missing mandatory statements, unreadable chart text.

Today authors check this by hand against a long author-guidelines PDF, and text-only proofreading tools cannot see inside figures. A university crest in a system diagram, a hidden PDF author field or a fourth panel nobody described all pass a spell check. DeskReject Guard reads the document's visual layer as well as its text, shows exactly where each problem is on the page, and, when the author uploads the `.tex` source, produces diffs that fix the common ones.

Unpublished manuscripts are confidential. Everything runs on the author's own machines with open-weight models (Gemma 4 through Ollama). No manuscript, figure or finding leaves the local network.

## 2. Goals and non-goals

### Goals

| ID | Goal |
|---|---|
| G1 | **Catch what text tools miss.** Find problems inside figures and in the document's hidden layers (metadata, link annotations), not only in the running text. |
| G2 | **Findings you can act on.** Every finding names the problem, shows the evidence, marks the exact spot on the page and says how to fix it. |
| G3 | **Trustworthy output.** Anything that can be decided with geometry, patterns or arithmetic is decided by code. The model is used only for what nothing else can answer, and its findings carry a confidence and a label. A clean paper produces no blocking findings. |
| G4 | **Private by construction.** Fully local. The app can show that it made no external requests. |
| G5 | **Fast enough to use before every submission.** An audit of a typical paper finishes in about a minute. See §8. |

### Non-goals (Hack Day build)

- Judging the science, the writing or the grammar. Existing proofreading tools cover that.
- Guaranteeing acceptance, or replacing the venue's official checklist. Presets are approximate and editable.
- Reading scanned or image-only PDFs, handwriting, or non-English papers.
- Editing the author's PDF or `.tex` automatically. Patches are suggestions the author applies.
- Overleaf and VS Code plugins, editorial system integrations (Editorial Manager, ScholarOne), and importing a venue's guideline page or URL.
- Accounts, sign-in, cloud storage or telemetry.

## 3. Users and modes

There is no sign-in. The tool is used by whoever runs it.

| User | What they do | Phase |
|---|---|---|
| Author | Uploads a compiled PDF (and optionally the `.tex`), picks a venue preset, reads the findings, applies fixes | Hack Day |
| Lab maintainer | Edits or adds venue presets as YAML files, with no code change | Hack Day (files only) |
| Editorial assistant | Sends submissions through an API and gets a risk verdict before assigning editors | Later |

### Data handling

| Item | Rule |
|---|---|
| The uploaded PDF and `.tex` | Held only for the session. Not copied anywhere else by the app. |
| Page and figure images | Sent only to the configured local Ollama endpoints on the same network. |
| Vision cache | Stores model answers keyed by a hash of the image and prompt, in a local folder. It does not store the PDF. The user can clear it from the UI. |
| Network | Only the configured Ollama hosts can be contacted. Anything else is blocked and counted. |

## 4. Interface and navigation

DeskReject Guard is **one Streamlit page** plus a **command-line tool**, both calling the same audit pipeline.

### Page layout

| Area | What's there |
|---|---|
| Sidebar | Preset select, PDF upload, optional `.tex` upload, "bypass vision cache" toggle, endpoint status list, "Run audit", "Load sample" |
| Header | Risk badge and gauge text, for example `Desk-Reject Risk: HIGH, 5 fatal flags, 4 warnings` |
| Tab: Findings | Cards grouped by severity, filter by check, "show on page" button on each |
| Tab: Page overlays | Rendered page with colored boxes and numbered badges, page selector, findings for that page beside it |
| Tab: Figures | Every detected figure with its status; colorblind previews when available |
| Tab: Patches | Diffs against the uploaded `.tex`, copy buttons, download of the patched file |
| Tab: Run log | Timings per stage and per check, vision calls per endpoint, cache hits, endpoint health, external requests blocked |
| Footer | `100% local, no external requests` when the blocked count is 0 |

### Command line

`python -m deskreject audit <pdf> --preset <id> [--tex file] [--json out.json] [--no-vision] [--no-cache]`. Prints a summary and writes the full report as JSON.

## 5. Functional requirements

### 5.1 Input and presets

| ID | Requirement |
|---|---|
| IN-1 | The author uploads a compiled PDF. Typical conference and journal papers (about 4 to 20 pages) are the target. |
| IN-2 | The author can optionally upload the `.tex` source to enable patches (PATCH group). |
| IN-3 | The author picks a venue preset from a list. The chosen preset controls which checks run and every threshold. |
| IN-4 | A preset is a YAML file. It sets: whether review is anonymous; minimum figure font size; raster DPI thresholds; whether figure order is enforced; which statements are required, recommended or ignored, and where they must appear; LaTeX patch settings. Changing a preset needs no code change. |
| IN-5 | Two presets ship: a double-blind conference style and an IEEE-style journal. Both are labelled "approximate, editable" in the UI. |
| IN-6 | Encrypted, corrupt, or scanned (no extractable text) PDFs get a clear error message instead of a crash or an empty report. |
| IN-7 | A "Load sample" button audits a bundled synthetic paper so the tool can be tried without an upload. |

### 5.2 Document understanding

| ID | Requirement |
|---|---|
| PARSE-1 | The tool extracts text with position, font size and boldness, and reads two-column pages in the correct order. |
| PARSE-2 | It finds headings, the front matter above the abstract (title and author block), and the start of the references. |
| PARSE-3 | It finds figure and table captions and the page area each figure occupies, and can render any area as an image. |
| PARSE-4 | It records every placed image with its pixel size and its printed size on the page. |
| PARSE-5 | It reads PDF metadata and every link annotation. |
| PARSE-6 | A page or element that cannot be read is skipped and logged. It never aborts the audit. |

### 5.3 Figure and caption parity

| ID | Requirement |
|---|---|
| FIG-1 | For vector figures, the visible sub-panel labels (a, b, c, …) are read from the text embedded in the figure. |
| FIG-2 | For raster figures with no readable labels, a vision model lists the labels it can see. Its answer is used only when its confidence is at least 0.6, and the resulting finding is marked as coming from vision. |
| FIG-3 | The caption's panel references are understood in the common forms: singles `(a)`, ranges `(a)-(c)` and `(a-c)`, and lists `(a), (b) and (d)`. |
| FIG-4 | A visible panel that the caption never mentions is a **fatal** finding, marked at that label's position. If the caption mentions no panels at all, it is a warning. |
| FIG-5 | A panel that the caption mentions but that is not visible is a **fatal** finding, only when label detection was reliable. |
| FIG-6 | Labels that are not in alphabetical reading order (top to bottom, left to right) are a warning. |

### 5.4 Double-blind anonymity

These checks run only when the preset is anonymous. Otherwise they return nothing.

| ID | Requirement |
|---|---|
| ANON-1 | A named author in the PDF metadata (author, creator or title field) is **fatal**. Software names and placeholders are ignored. |
| ANON-2 | Anything in the front matter other than an anonymous placeholder is a **fatal** author-block finding. |
| ANON-3 | Any email address anywhere in the document is **fatal**. |
| ANON-4 | Institution words (University, Institute, Laboratory, Department of, …) in the front matter are **fatal**. |
| ANON-5 | Links to GitHub, GitLab or Hugging Face user pages, in the text or in link annotations, are **fatal** unless the address is clearly anonymous. |
| ANON-6 | Self-citation phrasing that reveals authorship ("in our previous work [3], we …") is a warning. |
| ANON-7 | An acknowledgements or funding section is a warning. |
| ANON-8 | A vision model inspects every figure image, and any other placed image of reasonable size, for university or company logos, crests, seals, lab names, readable author or institution names, emails and watermarks. |
| ANON-9 | A vision finding is **fatal** only when its confidence is at least 0.6 and it is a logo, crest, badge or watermark, or its text matches institution words, an email or a URL. The finding shows what the model saw, the text it read and its confidence. |
| ANON-10 | At most 12 images are sent per document, largest first. Images are downscaled before sending. |
| ANON-11 | If vision calls fail, the audit still completes. One informational finding says how many images could not be checked. |

### 5.5 Figure and table sequencing

| ID | Requirement |
|---|---|
| SEQ-1 | Figures and tables are tracked separately. References in captions and after the reference list are ignored. |
| SEQ-2 | Ranges such as "Figures 2-4" count as mentions of 2, 3 and 4. Supplementary labels such as S1 are ignored. |
| SEQ-3 | If the first mention of figure N+1 comes before the first mention of N, it is a warning (only when the preset enforces order). |
| SEQ-4 | A figure or table with a caption and no mention in the body (a "ghost") is a warning. |
| SEQ-5 | A mention of a figure or table that has no caption (an "orphan") is **fatal**. |
| SEQ-6 | A literal `??` where a reference should be is **fatal**. |
| SEQ-7 | Caption numbers with a gap (1, 2, 4) are a warning. |

### 5.6 Mandatory statements

| ID | Requirement |
|---|---|
| STMT-1 | The tool checks for five statements: data availability, code availability, conflict of interest, ethics approval, and AI or large-language-model use. |
| STMT-2 | The preset says, for each statement, whether it is required, recommended or ignored, and where it must appear (before the references, or anywhere). |
| STMT-3 | A statement counts as present if a heading matches, or a sentence in the back matter matches, a list of common wordings. |
| STMT-4 | A missing required statement is **fatal**. A missing recommended statement is a warning. |
| STMT-5 | A statement that is present but in the wrong position for the preset is a warning. |
| STMT-6 | Each missing-statement finding includes ready-to-paste template wording. |

### 5.7 Print legibility

| ID | Requirement |
|---|---|
| LEG-1 | The tool audits the compiled PDF at its true printed size. Text inside vector figures is therefore already at its final size. |
| LEG-2 | Text inside a vector figure smaller than the preset minimum is one warning per figure, with the smallest size found and how many pieces of text are affected. |
| LEG-3 | For every placed raster image, the effective resolution is computed (image pixels over printed inches). |
| LEG-4 | Images with few colors (line art) are held to the higher threshold, photographs to the lower. Below the threshold is a warning. Below the preset's "fatal" threshold is **fatal**. |
| LEG-5 | The finding states the numbers, for example "280 px over 3.3 in = 85 dpi". |

### 5.8 Color accessibility

| ID | Requirement |
|---|---|
| ACC-1 | For each figure, the tool shows the original next to simulated views for protanopia, deuteranopia and tritanopia. |
| ACC-2 | It finds pairs of colors that are clearly different normally but nearly the same in a simulated view, and reports each as a warning with the colors and the measured difference. |
| ACC-3 | The fix hint recommends colorblind-safe palettes with ready-to-use colors or plotting-library settings. |

### 5.9 Findings, risk and reports

| ID | Requirement |
|---|---|
| RPT-1 | Every finding has: a stable code, the check it came from, a severity, a one-line title, a short explanation, the page, a box on the page when known, the exact evidence, a fix hint, a source (rule or vision) and a confidence. |
| RPT-2 | Severity is fixed per finding code. Codes are listed in the build plan. |
| RPT-3 | Risk is **HIGH** with at least one fatal finding, **MEDIUM** with no fatal but at least one warning, **LOW** otherwise. The header shows the risk and the counts. |
| RPT-4 | Findings are ordered fatal first, then warning, then info, then by page position. Each gets a number used on the page overlay. |
| RPT-5 | A check that fails unexpectedly becomes an informational finding. It never stops the other checks. |
| RPT-6 | The same input gives the same report. Model calls use fixed settings and cached answers. |
| RPT-7 | The full report can be exported as JSON. |

### 5.10 Fix suggestions for LaTeX

These need the `.tex` file. Without it, the tool shows fix hints only.

| ID | Requirement |
|---|---|
| PATCH-1 | Patches are shown as unified diffs. Nothing is changed automatically. |
| PATCH-2 | Add the preset's anonymity options to the `\documentclass` line when missing. |
| PATCH-3 | Replace the author block with the preset's anonymous placeholder, handling nested braces correctly. |
| PATCH-4 | Replace non-anonymous repository links with the preset's anonymous link. |
| PATCH-5 | Comment out the acknowledgements section. |
| PATCH-6 | Insert a stub section with template wording for each missing statement, before the bibliography. |
| PATCH-7 | For figures with too-small text, widen the figure to the column width. |
| PATCH-8 | The author can copy each diff or download the fully patched `.tex`. |

### 5.11 Dashboard

| ID | Requirement |
|---|---|
| UI-1 | A progress display shows each audit step while it runs. |
| UI-2 | The risk badge is red, amber or green and shows the gauge text. |
| UI-3 | The Findings tab groups cards by severity and can filter by check. Each card shows title, explanation, evidence, fix hint and a "show on page" button. |
| UI-4 | The Page overlays tab draws a box and a numbered badge for each finding on the rendered page, colored by severity. |
| UI-5 | The Figures tab shows each detected figure with a count of its findings and, when available, the colorblind previews. |
| UI-6 | The Run log tab shows timings, vision calls per endpoint, cache hits, endpoint health and external requests blocked. |
| UI-7 | Changing the preset and re-running changes the result, which shows that rules are data and not code. |

### 5.12 Offline and privacy

| ID | Requirement |
|---|---|
| OFF-1 | All model inference runs through Ollama on the local network. No cloud API is called at any point. |
| OFF-2 | All network access goes through one guarded client that allows only the configured Ollama hosts. Anything else is refused. |
| OFF-3 | The number of refused external requests is counted and shown in the UI. It should read 0. |
| OFF-4 | There are no accounts, analytics or telemetry. |
| OFF-5 | After setup (installing packages, pulling models), the tool works with no internet uplink. |
| OFF-6 | The user can clear the vision cache from the UI. |

### 5.13 Multi-node vision

| ID | Requirement |
|---|---|
| NODE-1 | The list of vision endpoints (host and worker laptops, each with its model) is configuration. |
| NODE-2 | Images are sent to all healthy endpoints in parallel, one at a time per endpoint, so small GPUs are not overloaded. |
| NODE-3 | A failed request is retried on another endpoint. An endpoint that keeps failing is marked unhealthy for the run. |
| NODE-4 | Endpoint health and per-endpoint usage are visible in the UI. |
| NODE-5 | The tool works with the host alone. Workers only make it faster. |

### 5.14 Consistency checks (later)

| ID | Requirement |
|---|---|
| DATA-1 | Numbers quoted in the abstract and conclusion are compared with the values shown in tables and figures, and mismatches are warned about. |
| DATA-2 | Numeric table columns whose header and caption give no unit are flagged as informational. |

### 5.15 API (later)

| ID | Requirement |
|---|---|
| API-1 | A small HTTP endpoint accepts a PDF and a preset id and returns the JSON report, so a submission system can call the same audit. |

### 5.16 Evaluation

| ID | Requirement |
|---|---|
| EVAL-1 | Two synthetic sample papers ship with the repo: one with a fixed list of seeded flaws, and a clean one. They contain no real people, logos or papers. |
| EVAL-2 | An evaluation script runs the audit on both and reports: recall on the seeded flaws, unexpected findings, blocking findings on the clean paper (target 0), timings, and vision calls. |
| EVAL-3 | The numbers go in the README, including misses. |

## 6. Scope and phases

| Phase | Features |
|---|---|
| Hack Day, must demo (P0) | Input and presets; document understanding; figure and caption parity; double-blind scrub (text, metadata, links, images); sequencing; statements; findings and risk; dashboard with overlays and run log; offline proof; multi-node vision; evaluation |
| Hack Day, should demo (P1) | Print legibility; LaTeX patches; color accessibility |
| After Hack Day (P2) | Consistency checks; API; text-model second opinion on ambiguous cases; model-written rewrites of self-citations; text-height estimate inside raster figures |
| Later | Overleaf and VS Code plugins; editorial system integration; importing a venue's guidelines; more venue presets; more languages |
| Deferred | Scanned PDFs |

### Mapping to the build plan

| Build plan feature | Requirement groups |
|---|---|
| F1 Figure to caption parity | FIG |
| F2 Anonymity on text, links, metadata | ANON-1 to ANON-7 |
| F3 Anonymity on images | ANON-8 to ANON-11 |
| F4 Sequencing | SEQ |
| F5 Statements | STMT |
| F6 Dashboard | RPT, UI |
| F7 Offline proof | OFF, NODE |
| F8 Legibility | LEG |
| F9 LaTeX patches | PATCH |
| F10 Color accessibility | ACC |
| F11 Consistency checks | DATA |
| F12 API | API |
| F13 Model second opinion and rewrites | none yet (P2, advisory only) |
| Foundation, testing | IN, PARSE, EVAL |

## 7. Design

Design principles for the UI:

- **Evidence first.** Every claim shows what was seen and where. No finding without a spot on the page or a quoted piece of text, unless it is about something missing.
- **Calm severity.** Red means the paper may be rejected, amber means fix if you can, blue is information. Colors are never the only signal; each card also has a text label.
- **Honest about the model.** Findings from the vision model are labelled and show their confidence.
- **Readable on a projector.** Large badge, large type for the gauge, nothing that needs squinting.

No mockup yet. UI guidelines will be added here if the UI is reworked after the event.

## 8. Quality bar

A check that cries wolf on a clean paper does not ship.

| Target | Bar |
|---|---|
| Parse a 10-page PDF | Under 3 s |
| All code-based checks | Under 2 s |
| Vision step, 12 images, 3 or 4 nodes | Under 60 s; under 5 s from cache |
| Seeded P0 flaws found | All of them on the sample paper |
| Blocking findings on the clean sample | None (no fatal, no warning) |
| A bad page or failed model call | Audit still completes with a report |

- **Enforced:** `pytest -q` and `ruff check .` pass before each commit. The evaluation script runs before the feature freeze, and its numbers go in the README.

## 9. Technical constraints

Runs on laptops with no cloud dependency. The host has a 12 GB GPU. Worker laptops have 6 GB GPUs, so each handles one image request at a time.

| Layer | Choice |
|---|---|
| Language and UI | Python 3.12, Streamlit |
| PDF reading and rendering | PyMuPDF |
| Data models and validation | Pydantic v2, YAML for presets |
| Image work | Pillow, NumPy |
| Models | Gemma 4 through Ollama: the larger model on the host (text and vision), the smaller model on workers (vision). Model names are configuration. |
| Network | httpx behind a host allowlist |
| Tests | pytest, ruff |

Not used: cloud model APIs, vector databases, screen-capture or desktop-automation libraries.

Full details in [`docs/IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) §3 and §4.

## 10. Decisions

All decisions from the planning session are logged in [`IMPLEMENTATION_PLAN.md` §2](IMPLEMENTATION_PLAN.md#2-scope-and-decisions-log). The earlier open questions are closed:

| # | Question | Decision |
|---|---|---|
| D0 | Where does the model matter? | Only for logos in images and panel labels in raster figures. Everything else is code. |
| D1 | How are the venue rules stored? | As YAML presets, approximate and editable. Two ship. |
| D2 | What does the tool read? | The compiled PDF. The `.tex` is optional and only enables patches. |
| D3 | How are worker laptops used? | Plain Ollama on each, with a pool that spreads images across them and retries elsewhere. |
| D4 | Do anonymity checks run for every venue? | Only for anonymous presets. |
| D5 | Are patches applied automatically? | No. They are diffs the author applies. |
| D6 | Is text in a vector figure checked against column width? | No scaling is guessed. The compiled PDF is already at print size, so the actual size is read. |
| D7 | How is a model's answer trusted? | Confidence floor of 0.6, labelled as vision, never the only basis for a fatal finding about text that code can read. |
| D8 | Is there a vector database for statements? | No. Headings and keywords are enough. |

### Still open

- [ ] **D9 Verify the model tags.** Confirm the Gemma 4 tags exist in Ollama and that each accepts images. First task of the build.
- [ ] **D10 Source for the desk-rejection rate.** The original spec says 15 to 30% of submissions are desk-rejected for preventable issues. No source is given. Do not state it as fact until one is found.
- [ ] **D11 Real venue rules.** The presets are approximations. Decide which real venues to model first and check their current author guidelines before claiming support.
- [ ] **D12 Handling confidential manuscripts.** Decide what the README tells users about where files and the vision cache live, and whether the cache should be off by default outside demos.

## 11. Success metrics

Hack Day targets:

- [ ] All P0 seeded flaws found on the sample paper
- [ ] No fatal or warning findings on the clean sample
- [ ] Full audit under about a minute on host plus workers, under 5 s cached
- [ ] Vision calls visibly spread across more than one machine in the run log
- [ ] The demo runs end to end in under 4 minutes, twice in a row

After the event (targets still to be set):

- [ ] Share of findings that authors judge correct, on real papers
- [ ] Share of real papers where a fatal finding was missed
- [ ] Time to prepare a submission, with and without the tool
- [ ] Number of venue presets contributed
