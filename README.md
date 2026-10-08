# DeskReject Guard

> Local, fully offline pre-flight auditor for academic manuscripts. Upload a compiled PDF, pick a venue preset, and get findings for problems that commonly lead to desk rejection — before peer review even begins.

## Team

**Team Name:** *TBD*

| Member | Contribution |
|--------|-------------|
| *TBD*  | *TBD*       |

## Problem Statement

### The Problem

Preventable visual, anonymity and formatting errors in academic manuscripts are a common cause of desk rejection. Text-only linting tools cannot inspect the visual layer — logos hidden inside figures, unreadable chart text, or author information baked into PDF metadata go undetected. Meanwhile, unpublished work is confidential and cannot be sent to cloud services.

### Why We Chose This Problem

Researchers spend weeks writing papers only to have them rejected for mechanical issues that a careful visual audit would catch. Existing tools check LaTeX source but not the compiled output that reviewers actually see. A fully local solution respects the confidentiality of unpublished research.

## Solution

DeskReject Guard audits the compiled PDF itself — reading text, metadata, link annotations, and the visual layer of every figure — using a pipeline of deterministic checks augmented by local Gemma 4 vision inference through Ollama. Findings are marked on the page with overlays, and LaTeX diffs fix the common issues automatically.

### Key Features

- Figure-caption parity checking (sub-panel labels vs caption text)
- Double-blind anonymity scrub (text, metadata, links, and images)
- Figure/table sequencing and mandatory statement detection
- Risk gauge dashboard with page overlays
- 100% offline: all inference on local hardware via Ollama

## Innovation and Differentiation

*TBD — to be completed during the hackathon.*

## Technical Implementation

### Architecture

*TBD — architecture diagram to be added.*

### Technology Stack

| Category        | Technologies                                              |
|----------------|----------------------------------------------------------|
| Backend         | Python 3.12, PyMuPDF, Pydantic v2, httpx                |
| AI / ML         | Gemma 4 (via Ollama, local inference)                    |
| UI              | Streamlit                                                 |
| Infrastructure  | Ollama (multi-node LAN), fully offline                   |

### Where Gemma 4 Is Used and What It Contributes

*TBD — to be completed when vision checks are implemented.*

## Implementation During the Hackathon

*TBD — to be documented as features are built.*

## Open Source and AI Usage

### AI / Models

- **Gemma 4** (via Ollama): Local vision inference for detecting logos, crests, and identifying text inside figures

### Open Source Components

- **PyMuPDF**: PDF parsing and rendering
- **Pydantic v2**: Data validation and contracts
- **Streamlit**: Dashboard UI
- **httpx**: HTTP client (Ollama communication only)
- **Pillow**: Image processing
- **NumPy**: Numerical operations
- **PyYAML**: Preset configuration
- **Matplotlib**: Synthetic sample generation only

## Setup and Usage

### Prerequisites

- Python 3.12+
- Ollama with Gemma 4 model pulled
- pip

### Installation

**PowerShell (Windows):**

```powershell
git clone https://github.com/<org>/deskreject-guard.git
cd deskreject-guard
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Bash (macOS / Linux):**

```bash
git clone https://github.com/<org>/deskreject-guard.git
cd deskreject-guard
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables

Copy `.env.example` to `.env` and adjust endpoints:

```bash
cp .env.example .env
```

### Running the Project

**CLI audit:**

```bash
python -m deskreject audit samples/bad_paper.pdf --preset neurips-style-double-blind
```

**Streamlit UI:**

```bash
streamlit run ui/app.py
```

**Run tests:**

```bash
pytest -q
```

**Lint:**

```bash
ruff check .
```

## Challenges and Learnings

*TBD — to be documented during the hackathon.*

## Credits and License

### Credits

Built for Hacktoberfest Hack Day — Coimbatore 2026, organized by INIT CLUB × iDEA CLUB in collaboration with Major League Hacking (MLH).

### License

[MIT](LICENSE)