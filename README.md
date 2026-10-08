# DeskReject Guard

DeskReject Guard is a local, fully offline pre-flight auditor for academic manuscripts.

## Setup and Usage

### Prerequisites
- Python 3.12+
- Ollama running locally

### Installation (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Installation (Bash)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running the App
```bash
streamlit run ui/app.py
```