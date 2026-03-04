# pythonencounters

A curated set of Python utilities grouped by domain. Every script here is repeatable, documented, and non-experimental. Each folder contains a `README.md` with the problem it solves, a use case, install/run instructions, sample output, and a regulation map showing where the script sits in audit and compliance frameworks.

Published companion pages: [rtapulse.com/python-encounters](https://rtapulse.com/python-encounters/)

Last updated: 2026-03-03

---

## Structure

```
pythonencounters/
├── grc-tech/          GRC, security, and audit utilities
├── user-tech/         Productivity and investigation tools
└── fin-tech/          Financial data and analysis scripts
```

---

## Scripts

### grc-tech — Security & Audit

| Script | What it does | Published page |
|--------|-------------|----------------|
| [ssl-cert-check/SSLcert.py](grc-tech/ssl-cert-check/) | Retrieve and inspect SSL/TLS certificate metadata for a hostname | [rtapulse.com](https://rtapulse.com/python-encounters/grc-tech/ssl-cert-check/) |
| [net-monitor/netmon.py](grc-tech/net-monitor/) | Capture active network connections with process context, export to CSV | [rtapulse.com](https://rtapulse.com/python-encounters/grc-tech/net-monitor/) |
| [file-hash-md5/generate_md5_hash.py](grc-tech/file-hash-md5/) | Compute MD5 hash of a file and write integrity receipt outputs | [rtapulse.com](https://rtapulse.com/python-encounters/grc-tech/file-hash-md5/) |
| [email-header-analyzer/email_header_analyzer.py](grc-tech/email-header-analyzer/) | Analyse email headers for SPF/DKIM/DMARC signals and From alignment | [rtapulse.com](https://rtapulse.com/python-encounters/grc-tech/email-header-analyzer/) |
| [control-testing/aws-iam-programme/](grc-tech/control-testing/aws-iam-programme/) | Five CIS-mapped AWS IAM checks with PASS/FAIL evidence output | [rtapulse.com](https://rtapulse.com/labs/control-testing/) |

### user-tech — Productivity & Investigation

| Script | What it does | Published page |
|--------|-------------|----------------|
| [pst-to-eml/pst_to_eml.py](user-tech/pst-to-eml/) | Convert Outlook PST archives to EML folder trees with attachments | [rtapulse.com](https://rtapulse.com/python-encounters/user-tech/pst-to-eml/) |
| [url-crawl-to-docx/url_crawl.py](user-tech/url-crawl-to-docx/) | Crawl a website and export page text to a structured Word document | [rtapulse.com](https://rtapulse.com/python-encounters/user-tech/url-crawl-to-docx/) |

### fin-tech — Financial Data

| Script | What it does | Published page |
|--------|-------------|----------------|
| [yfinance-export/yf_invest.py](fin-tech/yfinance-export/) | Download historical OHLCV data from Yahoo Finance and export to CSV | [rtapulse.com](https://rtapulse.com/python-encounters/financial/yfinance-export/) |
| [screener-profitloss-export/screener.py](fin-tech/screener-profitloss-export/) | Scrape P&L statement from Screener.in and export as CSV | [rtapulse.com](https://rtapulse.com/python-encounters/financial/screener-profitloss-export/) |
| [alphavantage-income-batch/combine_inc_stmt.py](fin-tech/alphavantage-income-batch/) | Batch-download annual income statements from Alpha Vantage | [rtapulse.com](https://rtapulse.com/python-encounters/financial/alphavantage-income-batch/) |
| [nse-ticker-list/nsepy_list.py](fin-tech/nse-ticker-list/) | Export a dated snapshot of NSE ticker symbols and company names | [rtapulse.com](https://rtapulse.com/python-encounters/financial/nse-ticker-list/) |

---

## Quickstart

Install dependencies for the domain you want to use:

```bash
pip install -r grc-tech/requirements.txt
pip install -r fin-tech/requirements.txt
pip install -r user-tech/requirements.txt
```

Each script folder contains a `README.md` with the full install and run instructions.

---

## Safety & hygiene

- Run tools only in environments you are authorised to inspect.
- Do not commit credentials, API keys, or tokens — use `.env` / environment variables.
- Treat outputs as evidence artifacts — store with retrieval timestamps.
- See [SECURITY.md](SECURITY.md) for responsible disclosure.

---

MIT licence · [rtapulse.com](https://rtapulse.com) · grcguy@rtapulse.com
