# pythonencounters
Last curated on: 2025-12-25

A small, curated set of Python utilities grouped by domain:

- **fin-tech/**: finance data extraction and CSV exports
- **grc-tech/**: security/GRC inspection and evidence-style helpers
- **user-tech/**: personal productivity tools (local-only workflows)

Only scripts that are repeatable, documented, and non-experimental are included here. Everything else stays local until refreshed.

## Quickstart

Create a virtual environment, then install dependencies for the domain you want:

- `pip install -r fin-tech/requirements.txt`
- `pip install -r grc-tech/requirements.txt`
- `pip install -r user-tech/requirements.txt`

Each tool folder contains a `README.md` with inputs, outputs, and a minimal run example.

## Safety & hygiene

- Run tools only in environments you control and are authorized to inspect.
- Do not commit secrets (API keys, tokens, credentials). Use `.env` / environment variables.
- Outputs from third‑party sources are best‑effort and may change as providers change.
