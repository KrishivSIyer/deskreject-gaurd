# AGENTS.md

## Hacktoberfest Hack Day — Coimbatore 2026

This file is the single source of truth for coding agents working in this repository, including Claude Code, OpenAI Codex, Gemini CLI, Cursor, Windsurf, GitHub Copilot, Aider, RooCode, Antigravity, and other agentic development tools.

Read this file before making changes to the repository.

> **How this file is organised.** Sections 1 to 12 are the organizers' original requirements, kept as given. Small project-specific additions inside them are marked **[Project]**. Sections 13 to 26 are the DeskReject Guard project rules, the condensed build plan, and the conventions agents must follow to write good code here.

## 0. Start here (agents)

1. Read this whole file.
2. Read `docs/PRD.md` (what we build) and `docs/IMPLEMENTATION_PLAN.md` sections 3 and 4 (architecture, contracts, finding codes).
3. You will be given one task ID (for example `T1.4`). Find its full text in `docs/IMPLEMENTATION_PLAN.md` section 6. Do exactly that task.
4. Touch only the files listed under the task's **Touches**.
5. Run `.venv\Scripts\pytest -q` (or inside activated `.venv`) and `ruff check .`. Both must pass. All execution MUST occur exclusively inside `.venv`.
6. Commit with the message `T<id>: <short summary>`, then `git pull --rebase` and push.
7. Report what changed and what you verified (section 24).

If this file and the plan disagree, the plan's contracts (section 4) win for code, and the organizers' sections 1 to 12 win for submission rules.

## 1. Project Context

This repository contains a project built for **Hacktoberfest Hack Day — Coimbatore 2026**, organized by INIT CLUB × iDEA CLUB in collaboration with Major League Hacking (MLH).

The project should be developed as a functional hackathon submission and should clearly communicate:

- The problem being solved
- Why the problem was selected
- The proposed solution
- Innovation and differentiation
- Technical implementation
- Work completed during the hackathon
- Open-source and AI usage
- Setup and usage
- Challenges and learnings

The repository must remain suitable for final submission.

**[Project] What this project is.** **DeskReject Guard** is a local, fully offline pre-flight auditor for academic manuscripts. An author uploads a compiled PDF (optionally the `.tex`), picks a venue preset, and gets findings for problems that commonly lead to rejection before review: author details left in a blinded paper (including logos inside figures and PDF metadata), figure and caption mismatches, figures cited out of order, missing mandatory statements, unreadable figure text, and color-inaccessible charts. Findings are marked on the page, and LaTeX diffs fix the common ones. Open-weight Gemma 4 models run through Ollama on the team's own laptops. Nothing leaves the local network.

**[Project] Event constraints that shape the code.** 100% local inference (no cloud APIs), team of 4, public repo with a clear open-source license, a working build, and at least one meaningful commit per teammate per hour.

## 2. Development Principles

Agents working in this repository must:

- Understand the existing project before modifying it.
- Prefer simple, maintainable solutions over unnecessary complexity.
- Preserve existing functionality unless a change explicitly requires it.
- Follow the project's existing architecture and conventions.
- Keep implementations focused on the hackathon problem.
- Avoid introducing unnecessary dependencies.
- Use environment variables for secrets and credentials.
- Never hardcode API keys, tokens, passwords, or private credentials.
- Keep commits focused and meaningful.
- Do not fabricate functionality, results, benchmarks, integrations, or claims.

## 3. Repository Structure

The repository may follow a structure similar to:

```text
.
├── README.md
├── AGENTS.md
├── .gitignore
├── .env.example
├── src/
├── public/
├── docs/
└── ...
```

The actual project structure takes precedence over this example.

Do not restructure the repository unnecessarily.

**[Project] Actual structure.**

```text
deskreject-guard/
├── README.md
├── AGENTS.md
├── LICENSE                         # MIT
├── .env.example
├── requirements.txt
├── pyproject.toml                  # ruff and pytest config only
├── docs/
│   ├── PRD.md
│   ├── IMPLEMENTATION_PLAN.md
│   └── deskreject_guard_product_specification.md
├── presets/
│   ├── neurips-style-double-blind.yaml
│   └── ieee-journal.yaml
├── src/deskreject/
│   ├── __main__.py                 # CLI: python -m deskreject audit file.pdf
│   ├── config.py                   # .env into Settings
│   ├── models.py                   # shared contracts (section 17)
│   ├── presets.py                  # load and validate presets
│   ├── netguard.py                 # the only allowed HTTP client
│   ├── pipeline.py                 # parse, run checks, finalize
│   ├── report.py                   # sort, number, count, risk
│   ├── ingest/                     # parse.py, layout.py, figures.py, mentions.py, render.py
│   ├── checks/                     # base.py, figure_caption.py, anonymity_text.py, anonymity_vision.py,
│   │                               # sequencing.py, statements.py, legibility.py, accessibility.py
│   ├── vision/                     # client.py, pool.py, cache.py, prompts.py, schemas.py
│   └── patches/                    # latex.py
├── ui/                             # app.py, overlays.py, components.py (Streamlit)
├── samples/                        # make_samples.py, expected.json, bad_paper.tex (+ generated PDFs)
├── eval/                           # run_eval.py, results.md
├── scripts/                        # check_models.py
├── tests/
└── .cache/                         # git-ignored
```

## 4. README Requirements

`README.md` is the primary project submission document.

Agents must keep it accurate and aligned with the actual implementation.

The README should contain:

### Project Title and Pitch

Project name and a concise description of what it does.

### Team

Team name, members, and contributions.

### Problem Statement

The problem being addressed, its target users or context, and why the team selected the problem.

### Solution

The proposed solution, how it addresses the problem, and its key features.

### Innovation and Differentiation

What makes the approach novel or different from existing or conventional solutions.

### Technical Implementation

Architecture, technology stack, major components, AI or ML models, APIs, infrastructure, and important technical decisions.

### Implementation During the Hackathon

What the team actually built during the Hack Day and the major contributions completed during the event.

### Open Source and AI Usage

Open-source libraries, frameworks, models, datasets, APIs, and other external components used in the project, including relevant attribution.

### Setup and Usage

Prerequisites, installation, environment variables, commands, and instructions required to run the project.

### Challenges and Learnings

Important technical or product challenges encountered during development and what the team learned from them.

### Credits and License

External resources, contributors, dependencies, and project licensing information.

Do not add judging criteria, judging scores, internal judging procedures, volunteer information, room allocations, or other organizer-only information to the project README.

**[Project] README mapping.** The headings above are required and take precedence over any other README outline. Put the project content into them like this:

| Required heading | DeskReject Guard content |
|---|---|
| Problem Statement | Preventable visual, anonymity and formatting errors in manuscripts; text-only tools cannot see figures; confidentiality of unpublished work. Do not quote a desk-rejection percentage unless a source is cited. |
| Solution | The audit pipeline, the findings and risk gauge, page overlays, LaTeX diffs |
| Innovation and Differentiation | Reads the visual layer (logos in figures, panel labels, figure text size, metadata and link annotations); "the model reads, code decides"; fully local multi-node inference |
| Technical Implementation | Architecture diagram, check list, vision pool, presets, **a subsection "Where Gemma 4 is used and what it contributes"** |
| Open Source and AI Usage | Gemma 4 (via Ollama), PyMuPDF, Streamlit, Pydantic, Pillow, NumPy, PyYAML, httpx, Matplotlib (samples only), with licenses |
| Setup and Usage | Section 22 commands, `.env` variables, multi-node setup, how to verify the offline claim |
| Challenges and Learnings | Real problems met (figure-region heuristics, vision false positives, worker memory limits and so on) |

## 5. AI and Open-Source Requirements

When AI or open-source components are used:

- Document the model, framework, library, API, or dataset.
- Explain its role in the system.
- Include appropriate attribution and licensing information.
- Do not claim an external component was developed by the team.
- Do not hide significant external dependencies.
- Keep AI integrations meaningful to the project.

If an AI model is used, document where it is used and what function it performs.

**[Project] Where models are used.** Gemma 4 vision is used for (1) finding logos, crests, lab names and readable identifying text inside figures and page images, and (2) reading sub-panel labels in raster figures when no embedded text exists. Gemma 4 text and `qwen2.5-coder` are P2 only. Everything else is code. Keep this list accurate in the README.

## 6. Hackathon Development Requirements

The project should represent work substantially developed during the Hack Day.

Agents must not:

- Present an unrelated pre-existing project as newly built.
- Invent implementation history.
- Remove evidence of existing dependencies or external components.
- Misrepresent external work as team work.
- Add fabricated metrics or results.

Existing libraries, frameworks, APIs, datasets, models, and open-source components may be used where appropriate.

**[Project]** The first commit is made at the start of the event. Do not paste in code written before the event. Planning documents (`docs/`) and `AGENTS.md` are fine. Evaluation numbers in the README must come from `eval/run_eval.py` output. If something was not measured, write "not measured".

## 7. Secrets and Environment Variables

Never commit secrets.

Use environment variables for credentials and configuration.

Provide required variables through:

```text
.env.example
```

The actual `.env` file must remain untracked.

Examples:

```env
API_KEY=
DATABASE_URL=
MODEL_API_KEY=
```

Never place real credentials in source code, documentation, commits, or configuration files intended for version control.

**[Project] Actual variables.** This project needs no API keys. Its configuration is local endpoints and limits. Never hardcode IPs or model names in code; read them from `Settings`.

```env
# host first; format is model@url; one entry per worker laptop
OLLAMA_VISION_ENDPOINTS=gemma4:12b-it-qat@http://127.0.0.1:11434,gemma4:e4b-it-qat@http://192.168.43.101:11434
TEXT_MODEL=gemma4:12b-it-qat@http://127.0.0.1:11434
CODER_MODEL=qwen2.5-coder:14b@http://127.0.0.1:11434
VISION_ENABLED=true
VISION_MAX_PX=1024
VISION_MAX_CROPS=12
VISION_TIMEOUT_S=90
CACHE_DIR=.cache
DEFAULT_PRESET=neurips-style-double-blind
```

Model tags are assumptions until `scripts/check_models.py` confirms them. If a tag differs, change `.env.example` only.

## 8. Code Quality

Agents should:

- Follow the language and framework conventions already used by the project.
- Keep functions and modules focused.
- Avoid unnecessary abstraction.
- Handle errors appropriately.
- Validate external input where relevant.
- Keep configuration separate from application logic.
- Remove unused code and dependencies when encountered.
- Avoid temporary debugging code in the final submission.

## 9. Testing and Verification

Before declaring a feature complete:

1. Run the relevant tests.
2. Verify the application starts successfully.
3. Verify the affected functionality manually where practical.
4. Check that required environment variables are documented.
5. Ensure the README remains consistent with the implementation.

Do not claim that functionality works without verifying it.

**[Project] How to verify here.** `pytest -q`, then `ruff check .`, then run the CLI on both sample PDFs (section 22). For UI work, run `streamlit run ui/app.py`, click "Load sample", and confirm the tab you changed renders. A check is verified only when it finds its seeded flaws on `bad_paper.pdf` and reports nothing blocking on `clean_paper.pdf`.

## 10. Changes to the Repository

Before modifying an unfamiliar area:

- Inspect the relevant files.
- Understand how the component is currently used.
- Check for existing utilities or abstractions.
- Make the smallest appropriate change.

Do not rewrite working components merely for stylistic preference.

## 11. Submission Readiness Checklist

Before the final submission, verify:

- [ ] Project builds or runs successfully
- [ ] Core functionality works
- [ ] README is complete and accurate
- [ ] Problem and reason for selecting it are documented
- [ ] Solution and key features are documented
- [ ] Innovation and differentiation are explained
- [ ] Architecture is documented
- [ ] Technical implementation is documented
- [ ] Hackathon-built work is documented
- [ ] Team contributions are documented
- [ ] AI and open-source components are documented
- [ ] Setup instructions work
- [ ] Environment variables are documented
- [ ] Challenges and learnings are documented
- [ ] Credits are included
- [ ] License is included
- [ ] No secrets are committed
- [ ] No fabricated claims are present
- [ ] Repository contains no unnecessary files or dependencies

**[Project] Additional items:**

- [ ] `pytest -q` and `ruff check .` pass on a fresh clone
- [ ] `python eval/run_eval.py` runs and its table is in the README (misses included)
- [ ] The README has a "Where Gemma 4 is used and what it contributes" section
- [ ] The UI footer shows `external requests blocked: 0` after a full audit
- [ ] No real papers, real logos or personal data are committed (samples are synthetic)
- [ ] Every teammate has commits in every hour of the event
- [ ] The Gemma 4 challenge is selected when submitting on OrganizerHQ

## 12. Agent Behavior

When asked to modify the project:

1. Inspect the relevant code and repository structure.
2. Understand the existing implementation.
3. Make the requested change.
4. Test or verify the change.
5. Update the README when the change materially affects project functionality or documented setup.
6. Report what changed and what was verified.

When asked to add a feature, do not modify unrelated parts of the project.

When asked to prepare the project for submission, prioritize correctness, reproducibility, documentation, and repository cleanliness.

---

# Part B. DeskReject Guard: project rules for agents

## 13. The plan in one page

**Scope and priority.** P0 must demo. P1 only after the M2 exit check. P2 only if everything else works. Nothing new after the feature freeze (3:15 PM); revert anything half-working.

| Priority | Features | Requirement groups in `docs/PRD.md` |
|---|---|---|
| P0 | Figure and caption parity; anonymity on text, metadata and links; anonymity on images (Gemma 4 vision); figure and table sequencing; mandatory statements; findings, risk and dashboard; offline proof and multi-node vision | FIG, ANON, SEQ, STMT, RPT, UI, OFF, NODE |
| P1 | Print legibility (DPI and tiny figure text); LaTeX patches; color accessibility previews | LEG, PATCH, ACC |
| P2 | Abstract-vs-table numbers; table units; FastAPI endpoint; model second opinion; model-written rewrites; text height inside raster figures | DATA, API |

**Milestones and exit checks.**

| Milestone | Delivers | Exit check |
|---|---|---|
| M0 Foundation | Repo, contracts, presets, model check, sample PDFs, CLI shell, netguard | Everyone can install and run `pytest -q`; `check_models.py` shows host and a worker with vision OK; sample PDFs generate |
| M1 Ingest and core checks | Parser, figure regions, anonymity text, sequencing, statements, report finalize, vision pool, UI skeleton | Every P0 code from those checks is found on `bad_paper.pdf` and none on `clean_paper.pdf`; UI lists findings |
| M2 Figures, vision, overlays | Figure parity, image anonymity, overlays, gauge, run log, worker fan-out | Every P0 seeded flaw found; nothing fatal on the clean paper; run log shows calls on more than one endpoint |
| M3 P1 extras and eval | Legibility, patches, colorblind previews, eval script | P1 flaws found; diffs generated for `bad_paper.tex`; eval table prints |
| M4 Freeze and submit | README, demo, backup recording, submission | Public repo, license, README, demo runs twice, submitted |

**Lanes.**
- **Lane A:** Sibi Chakravarthi (pipeline, parser, eval, submission)
- **Lane B:** Karthik MG (text checks and patches)
- **Lane C:** Krishiv S Iyer (vision, workers, geometry and color checks)
- **Lane D:** Aditya Vineeth (samples, UI, docs, demo)

**Task index.** Full task bodies are in `docs/IMPLEMENTATION_PLAN.md` section 6. Tick your task in the same commit that finishes it. If a rebase conflicts on this list, keep every tick from both sides.

- M0
  - [x] T0.1 Scaffold the repo (A, P0)
  - [x] T0.2 Models and endpoints check (C, P0)
  - [x] T0.3 Contracts and presets (A, P0) **push first, everyone depends on it**
  - [x] T0.4 Synthetic papers (D, P0)
  - [x] T0.5 Pipeline shell, CLI and netguard (A, P0)
- M1
  - [ ] T1.1 PDF ingest (A, P0)
  - [ ] T1.2 Captions, figure regions, crops (A, P0)
  - [ ] T1.3 Report finalize (A, P0)
  - [ ] T1.4 Anonymity checks on text, links and metadata (B, P0)
  - [ ] T1.5 Mentions and sequencing (B, P0)
  - [ ] T1.6 Statements sweeper (B, P0)
  - [ ] T1.7 Vision client, pool and cache (C, P0)
  - [x] T1.8 UI skeleton (D, P0)
- M2
  - [ ] T2.1 Figure to caption parity (B, P0)
  - [ ] T2.2 Anonymity on images with Gemma 4 (C, P0)
  - [x] T2.3 Overlays (D, P0)
  - [x] T2.4 Dashboard polish and run log (D, P0)
  - [ ] T2.5 Worker fan-out (C, P0)
  - [ ] T2.6 Real-PDF smoke test (A, P0)
- M3
  - [ ] T3.1 Legibility (C, P1)
  - [x] T3.2 LaTeX patches (B, P1)
  - [ ] T3.3 Colorblind previews and check (C, P1)
  - [ ] T3.4 Evaluation script (A, P1)
  - [ ] T3.5 Buffer: fix false positives first, then misses (all)
- M4
  - [ ] T4.1 README (D, P0)
  - [ ] T4.2 Demo and backup (D, P0)
  - [ ] T4.3 Submission (A, P0)
- P2 backlog: T5.1 abstract vs table, T5.2 table units, T5.3 FastAPI `/audit`, T5.4 Gemma text second opinion, T5.5 qwen patch polish, T5.6 text height inside raster figures

## 14. Architecture in brief

```text
 PDF (+ optional .tex) + preset
              │
              ▼
   ingest (PyMuPDF): text spans with fonts and boxes, images with placed size,
                     links, metadata, headings, front matter, captions, figure regions
              │
     ┌────────┴──────────────────────┐
     ▼                               ▼
 code-based checks                figure crops (150 dpi)
 figure labels, anonymity text,        │
 sequencing, statements, legibility    ▼
     │                          VisionPool ──► Ollama host + worker laptops (Gemma 4)
     │                                │
     └──────────────┬─────────────────┘
                    ▼
        merge, sort, risk score ──► Report (JSON) ──► Streamlit UI / CLI
```

Entry point: `pipeline.audit(pdf_path, preset_id, tex_text=None, use_cache=True) -> Report`. The UI renders from the `Report` alone and never calls a check directly.

## 15. Core principles for the code

1. **The model reads, code decides.** Use geometry, regex and arithmetic first. Gemma is used only where nothing else can answer. Never ask a model to compute a number, a date, a count or a threshold.
2. **Checks are pure functions** of a `ParsedDoc`, a `Preset` and a `Context`. No global state, no hidden I/O. This is what lets four people work in parallel.
3. **Never crash an audit.** Catch errors at the check boundary and return an info finding (`SYS_CHECK_ERROR`). A bad page is skipped and logged, never fatal. A failed vision call becomes `SYS_VISION_UNAVAILABLE`.
4. **Evidence or silence.** Every finding carries the exact text or numbers that triggered it. If you cannot show evidence, do not raise a finding.
5. **Calibrate for no false alarms.** A clean paper must produce no fatal and no warning findings. When unsure between a warning and a fatal, choose the warning.
6. **Deterministic.** Same input, same output. Model calls use temperature 0, a fixed seed and the cache. Sort outputs.
7. **Fail honestly.** If something is not supported, say so in the report or README. Do not hide it.

## 16. Hard rules

- **Network.** All HTTP goes through `netguard.make_client()`, which allows only the configured Ollama hosts. No cloud APIs. No telemetry. No `requests`, `urllib` or raw sockets in library code.
- **Dependencies.** No new dependency without adding it to `requirements.txt` and saying so in the commit message. Do not add ChromaDB, FAISS, MSS, PyAutoGUI or OpenCV. They are not needed.
- **Coordinates.** PDF points, origin top-left, `bbox = (x0, y0, x1, y1)`. Page numbers are 1-based in findings.
- **Finding codes.** Use only codes from the catalogue (section 17). Do not invent codes or change severities.
- **Contracts.** `src/deskreject/models.py` is shared by all lanes. Changes must be additive. If you must change an existing field, say so in the commit message and the team chat first.
- **Logging.** Use `logging`, never `print`, in library code. The CLI may print its summary.
- **Types and style.** Type hints on every public function. `ruff check .` clean (line length 100).
- **Files.** Touch only the files listed in the task. If you must touch another, say why in the commit message.
- **Data.** No real papers, real logos or personal data in the repo. Samples are synthetic. Real PDFs used for smoke tests stay local and untracked.
- **Config.** No hardcoded IPs, model names or thresholds. Endpoints and models come from `.env`; thresholds and rules come from presets.

## 17. Contracts and finding codes

Full definitions: `docs/IMPLEMENTATION_PLAN.md` section 4. The essentials:

```python
BBox = tuple[float, float, float, float]   # x0, y0, x1, y1, PDF points, origin top-left

class Finding(BaseModel):
    code: str; check: str; severity: Severity   # fatal | warning | info
    title: str; detail: str
    page: int | None; bbox: BBox | None
    evidence: str | None; fix_hint: str | None
    source: str = "rule"                         # rule | vision | llm
    confidence: float = 1.0
    figure_id: str | None; patch_key: str | None; number: int | None

class Check(Protocol):
    name: str
    priority: str                                # P0 | P1 | P2
    def run(self, doc: ParsedDoc, preset: Preset, ctx: Context) -> list[Finding]: ...
```

Checks register with `@register_check` from `checks/base.py`. `ctx.vision` is a `VisionPool` or `None`.

**Finding catalogue (codes are fixed):**

| Code | Check | Severity |
|---|---|---|
| `FIG_PANEL_UNREFERENCED` | figure_caption | fatal (warning if the caption mentions no panels) |
| `FIG_PANEL_COUNT_MISMATCH` | figure_caption | fatal |
| `FIG_PANEL_ORDER` | figure_caption | warning |
| `ANON_METADATA_AUTHOR`, `ANON_AUTHOR_BLOCK`, `ANON_EMAIL`, `ANON_AFFILIATION`, `ANON_REPO_URL`, `ANON_LOGO_IN_FIGURE` | anonymity | fatal |
| `ANON_SELF_CITE`, `ANON_ACK` | anonymity | warning |
| `SEQ_ORPHAN_REF`, `SEQ_UNRESOLVED_REF` | sequencing | fatal |
| `SEQ_OUT_OF_ORDER`, `SEQ_GHOST`, `SEQ_NUMBER_GAP` | sequencing | warning |
| `STMT_MISSING_<ID>` | statements | fatal if required in the preset, else warning |
| `STMT_MISPLACED_<ID>` | statements | warning |
| `LEG_RASTER_LOW_DPI` | legibility | warning (fatal below the preset's `fatal_below`) |
| `LEG_FONT_TOO_SMALL` | legibility | warning |
| `ACC_CB_INDISTINGUISHABLE` | accessibility | warning |
| `SYS_VISION_UNAVAILABLE`, `SYS_CHECK_ERROR` | system | info |

`<ID>` is one of `DATA_AVAILABILITY`, `CODE_AVAILABILITY`, `CONFLICT_OF_INTEREST`, `ETHICS`, `AI_USE`.

**Risk:** HIGH if any fatal, MEDIUM if any warning, else LOW. Gauge text: `Desk-Reject Risk: HIGH, 5 fatal flags, 4 warnings`.

Anonymity checks (text and vision) return `[]` when `preset.anonymous` is false.

## 18. Working with PDFs (PyMuPDF)

- `import pymupdf` (not `fitz`).
- Text: `page.get_text("dict")` gives blocks, lines and spans with `size`, `flags` and `bbox`. Bold is `flags & 16`. Do not use `get_text("blocks", sort=True)` for reading order; it breaks on two columns.
- Images: `page.get_image_info(xrefs=True)` gives placed `bbox`, `width`, `height`. Raw image bytes: `doc.extract_image(xref)`.
- Vector graphics: `page.get_drawings()`. Links: `page.get_links()`. Metadata: `doc.metadata`.
- Render a region: `page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(*bbox))`, then `.tobytes("png")`.
- Normalise extracted text before matching: Unicode NFKC, rejoin words hyphenated at line ends, collapse whitespace.
- Two-column detection: at least 60% of body-size blocks narrower than 55% of the page width. Read column by column, top to bottom.
- Figure region: anchor to the caption, take its column range, walk upward to the nearest body-text block or page top, union the images, drawings and short text spans in that band, pad 4 pt. If the band is empty, look below the caption.
- Wrap each page in `try/except`. Log and skip pages that fail.
- Text inside vector figures is already at print size in a compiled PDF. Do not guess scaling.
- Sample generation: set `matplotlib.rcParams["pdf.fonttype"] = 42` so figure text stays extractable.

## 19. Vision (Ollama) conventions

- Endpoint: `POST {url}/api/chat` with `stream: false`, `format: <JSON schema>`, `options: {temperature: 0, seed: 7, num_ctx: 4096}`, `keep_alive: "30m"`, and `messages: [{role: "user", content: <prompt>, images: [<base64 png>]}]`.
- Downscale images so the long side is at most `VISION_MAX_PX` (1024) before encoding.
- At most `VISION_MAX_CROPS` (12) images per document, largest first. Submit them in one `ask_many` call so all endpoints stay busy.
- One in-flight request per endpoint (the worker GPUs have 6 GB). A shared queue feeds one thread per healthy endpoint. Retry a failed job up to 2 times, preferably on another endpoint. Mark an endpoint unhealthy after 2 consecutive failures.
- Cache key: sha256 of image bytes, prompt and canonical schema JSON. Do not include the endpoint in the key. The UI has a "bypass cache" switch for demos.
- Parse with Pydantic. On invalid JSON, retry once, then return a failed `VisionResult`.
- Trust rule: a vision item counts only at `confidence >= 0.6`. Vision findings are labelled `source="vision"` and show their confidence. Never use vision for something code can read.
- Prompts and schemas live in `vision/prompts.py` and `vision/schemas.py`. Text of both is in `docs/IMPLEMENTATION_PLAN.md` Appendix B.

## 20. Presets

- Presets are YAML in `presets/`, validated by the `Preset` model. Thresholds and rules live there, not in code.
- Values are approximate. Never describe a preset as a publisher's official rules.
- Adding a venue means adding a YAML file only.

## 21. Testing conventions

- Every check has unit tests built from **hand-made `ParsedDoc` objects**, with at least one positive and one negative case per rule. Do not make unit tests depend on the parser.
- Every check also has one test on the sample PDFs: it finds its seeded flaws on `samples/bad_paper.pdf` and reports nothing blocking on `samples/clean_paper.pdf`. The seeded flaw list is in `docs/IMPLEMENTATION_PLAN.md` section 4 and in `samples/expected.json`.
- Vision tests use a fake pool that returns canned `VisionResult`s. Pool tests use `httpx.MockTransport`. Tests never need a running Ollama.
- Network tests must prove that a non-allowlisted host is blocked and counted.
- Keep tests fast. The whole suite should run in well under a minute.
- Never weaken a test to make a check pass. If a seeded flaw is not found, fix the check or report it as a known miss.

## 22. Commands

PowerShell (Windows):

```powershell
# ALL development, scripts, linters, and tests MUST run exclusively inside .venv
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt  # or install required dependencies into .venv
copy .env.example .env
```

bash:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then, in either shell:

```text
python samples/make_samples.py                 # generate bad_paper.pdf, clean_paper.pdf, expected.json
python scripts/check_models.py                 # verify endpoints, models and vision support
python -m deskreject audit samples/bad_paper.pdf --preset neurips-style-double-blind --json out.json
python -m deskreject audit samples/bad_paper.pdf --preset neurips-style-double-blind --no-vision --no-cache
streamlit run ui/app.py                        # the dashboard
pytest -q                                      # tests
ruff check .                                   # lint
python eval/run_eval.py                        # evaluation table, writes eval/results.md
```

CLI flags: `--preset <id>`, `--tex <file>`, `--json <file>`, `--no-vision`, `--no-cache`.

## 23. Git and commits

- Trunk-based. Short branches or direct pushes to `main`. `git pull --rebase` before every push. Never force-push `main`.
- One task, one commit. Message: `T<id>: <short summary>`. Use `WIP T<id>: ...` if a task runs past 45 minutes, so there is always a commit each hour.
- Do not commit `.env`, `.cache/`, `.venv/`, `__pycache__/`, `out.json`, or any real paper.
- If a P1 or P2 change is not working at the feature freeze, revert it.
- One agent per branch or worktree. Do not run two agents in the same working copy.

## 24. Working on a task (agent procedure)

1. Read the task body: **Covers**, **Touches**, **Do**, **Done when**, **Not in this task**.
2. Inspect the files you will touch and the contracts you depend on. Reuse existing helpers.
3. Write the tests first or alongside, using hand-made `ParsedDoc` objects.
4. Implement the smallest change that satisfies **Done when**.
5. Run `pytest -q` and `ruff check .`. Run the CLI on both sample PDFs if your task is a check or a parser change.
6. Tick the task in section 13, commit, rebase, push.
7. Report in this format:
   - What changed (files)
   - What was verified (commands and results)
   - Known gaps or misses (be specific and honest)

**Definition of done:** the task's **Done when** is met, both commands pass, no files outside **Touches** changed, no debug prints, no new dependency without a note, and any behavior change that affects setup or usage is reflected in the README.

## 25. Do not

- Do not call a cloud model or any external API.
- Do not use a model to do what a regex, geometry or arithmetic can do.
- Do not raise a finding without evidence.
- Do not add a finding code or change a severity.
- Do not change `models.py` fields without telling the team.
- Do not add global mutable state, singletons that hold documents, or hidden caches outside `.cache/`.
- Do not sleep or poll to hide a race. Fix it.
- Do not swallow exceptions silently. Log them and degrade gracefully.
- Do not reformat or refactor files you were not asked to touch.
- Do not hardcode paths, IPs, model names or thresholds.
- Do not write evaluation numbers by hand. Paste them from `eval/results.md`.
- Do not claim a feature works until you have run it.

## 26. Quality targets

| Target | Bar |
|---|---|
| Parse a 10-page PDF | under 3 s |
| All code-based checks | under 2 s |
| Vision step, 12 images, 3 or 4 nodes | under 60 s; under 5 s from cache |
| Seeded P0 flaws on `bad_paper.pdf` | all found |
| Blocking findings on `clean_paper.pdf` | none (no fatal, no warning) |
| Bad page or failed model call | audit still completes with a report |
