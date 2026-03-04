# user-tech

**Part of [Python Encounters](https://rtapulse.com/python-encounters/) — rtapulse.com**

Productivity and investigation utilities for local workflows. Scripts in this folder handle file conversion, web capture, and content extraction tasks that come up regularly in audit, compliance, and research work.

---

## Scripts

| Script | What it does | Published page |
|--------|-------------|----------------|
| [pst-to-eml/pst_to_eml.py](pst-to-eml/) | Convert Outlook PST archives to EML folder trees with attachments intact | [rtapulse.com](https://rtapulse.com/python-encounters/user-tech/pst-to-eml/) |
| [url-crawl-to-docx/url_crawl.py](url-crawl-to-docx/) | Crawl a website and export page text to a structured Word document | [rtapulse.com](https://rtapulse.com/python-encounters/user-tech/url-crawl-to-docx/) |

---

## Setup

```bash
pip install -r user-tech/requirements.txt
```

`pst-to-eml` also requires `readpst` installed via your system package manager:

```bash
# Ubuntu/Debian
sudo apt-get install pst-utils

# macOS
brew install libpst
```

Each script folder contains a `README.md` with full install instructions, sample output, and a regulation/context map.

---

## Regulation frameworks covered

GDPR / UK GDPR · FRCP eDiscovery · ISO 27001:2022 · DORA · SOX · SEBI · PCI DSS v4.0 · NIST CSF 2.0

---

## Safety

- `pst-to-eml`: always run on a **copy** of the PST — never the original. Output can be 1.5–2× the source file size.
- `url-crawl-to-docx`: respect the target site's terms of service. Use `--max-pages` and `--delay` to avoid overloading servers.
- Do not process real sensitive data (email archives, personal data) in shared or uncontrolled environments.

---

MIT licence · [rtapulse.com](https://rtapulse.com) · grcguy@rtapulse.com
