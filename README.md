# PDF Chat with Gemini

A Streamlit app that lets you upload a PDF and ask questions about its content using Google's Gemini models and the File Search API.

## Features
- Drag-and-drop PDF upload with file status indicators and reset controls.
- Secure Gemini API key entry stored only in the local session.
- Model picker (Gemini 2.5 Flash, Gemini 2.5 Flash Lite, Gemini 2.5 Pro).
- Conversational interface powered by `st.chat_message` with streaming-like status.
- Source explorer that surfaces references returned by Gemini File Search.

## Project Structure
```
.
├── app/
│   ├── conversation.py      # Prompt/response helpers
│   ├── file_search.py       # Gemini File Search service layer
│   ├── localization.py      # Copy and translation lookup
│   ├── pdf_utils.py         # Secure file staging utilities
│   ├── state.py             # Streamlit session helpers
│   └── ui.py                # Sidebar and chat rendering primitives
├── main.py                  # Streamlit entrypoint
├── pyproject.toml           # Project metadata and dependencies
└── requirements.txt         # Pip-compatible dependency lock
```

## Prerequisites
- Python 3.10+
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

## Setup (UV)
1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you do not already have it.
2. Sync the environment and dependencies:
	```bash
	uv python install 3.10  # optional if 3.10+ already available
	uv sync
	```

Export your API key (optional if you plan to paste it in the sidebar):
```bash
export GEMINI_API_KEY="YOUR_KEY_HERE" 
```

## Run the app (UV)
```bash
uv run streamlit run main.py
```

Then open the provided local URL, enter your API key (or rely on the env var), upload a PDF, and start chatting.

## Pip fallback (optional)
If you prefer plain pip/venv workflows, you can still rely on the compatibility `requirements.txt` file (regenerate it via `uv pip compile pyproject.toml --output requirements.txt`).
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Notes
- Uploaded files are staged in a temporary directory and removed when you clear the session.
- File Search stores are created per upload and destroyed when you reset or exit the app.
- The app currently ships with English UI copy; hook into `TRANSLATIONS` to localize.

## CI/CD: Oracle Cloud via GitHub Actions
This repository ships with `.github/workflows/deploy.yml`, which builds the app and deploys it to an Oracle Cloud VM through SSH whenever you push to `main`/`master` (or on manual dispatch).

### 1. Prepare the Oracle instance
- Install Git, Python 3.10+, and `systemd` on the VM.
- Clone this repository into your preferred path (for example `/home/ubuntu/gemini-api-file-search-tool`).
- Create a virtual environment in-place (the workflow will re-use or create `.venv`).
- Register a `systemd` service (default name `streamlit`) that launches `streamlit run main.py` using the virtual environment.

### 2. GitHub secrets (required)
| Secret | Purpose |
| --- | --- |
| `ORACLE_HOST` | Public IP / host of the Oracle VM |
| `ORACLE_USERNAME` | SSH user with deploy permissions |
| `ORACLE_SSH_KEY` | Private key (PEM) for that user |
| `ORACLE_SSH_PORT` *(optional)* | Non-default SSH port, defaults to 22 |

### 3. GitHub repository variables (optional)
| Variable | Purpose | Default |
| --- | --- | --- |
| `ORACLE_APP_DIR` | Absolute path to the app on the VM | `$HOME/gemini-api-file-search-tool` |
| `ORACLE_SERVICE_NAME` | `systemd` unit to restart after deploy | `streamlit` |

### 4. What the workflow does
1. Checks out the repository and installs dependencies with Python 3.12.
2. Runs a lightweight `py_compile` sanity check on all tracked Python files.
3. SSHes into the Oracle VM, clones the repo if needed, resets the target branch, installs dependencies inside `.venv`, and restarts the configured `systemd` service.

Trigger the workflow manually from the Actions tab or simply push to the tracked branch to deploy.
