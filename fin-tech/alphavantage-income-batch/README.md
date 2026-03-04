# Alpha Vantage Income Batch

**Part of [Python Encounters](https://rtapulse.com/python-encounters/) — rtapulse.com**
Script: [`combine_inc_stmt.py`](https://github.com/sachmehta2/pythonencounters/blob/main/fin-tech/alphavantage-income-batch/combine_inc_stmt.py) · [Published page](https://rtapulse.com/python-encounters/financial/alphavantage-income-batch/)

---

## The problem

Pulling income statement data for a portfolio of securities — ten, thirty, a hundred tickers — one at a time through a web interface is the kind of task that consumes half a day when the underlying data is available via API in thirty seconds per ticker. The friction is not the data; it is the tooling. Most analysts either do this manually or pay for a Bloomberg terminal. Alpha Vantage provides a free-tier API that covers this need for most analytical purposes — but it still requires a wrapper to do batch extraction cleanly.

---

## Use case

You are building a peer comparison model for an investment committee review covering fifteen Indian ADRs listed on US exchanges. You need five years of annual income statement data — revenue, EBITDA, net income, EPS — for all fifteen in a single model-ready CSV. You create a tickers.txt with all fifteen symbols, run this script with your Alpha Vantage API key, and receive a consolidated CSV with all companies and all years in a consistent column structure. Total elapsed time: under two minutes.

---

## What the script does

combine_inc_stmt.py reads a text file of ticker symbols, calls the Alpha Vantage INCOME_STATEMENT endpoint for each, extracts the annual report data, and appends all results to a single CSV with a timestamp in the filename. The free Alpha Vantage tier allows approximately 5 requests per minute — the script includes a delay between calls. Store your API key in an environment variable or .env file; do not commit it to the repository.

---

## Install and run

```bash
# Install dependencies
$ pip install requests python-dotenv

# Set your API key
$ export ALPHA_VANTAGE_KEY=your_api_key_here

# Create tickers file
$ echo -e "AAPL
MSFT
GOOGL" > tickers.txt

# Run
$ python3 combine_inc_stmt.py
```

---

## Dependencies

- `requests` — HTTP calls to the Alpha Vantage INCOME_STATEMENT endpoint
- `python-dotenv (optional)` — Loads API key from .env file — avoids hardcoding credentials
- `Alpha Vantage API key` — Free tier available at alphavantage.co — rate limited to 25 calls/day on free tier
- `Internet access` — Queries api.alphavantage.co — requires outbound HTTPS

---

## Sample output

**Success:**
```
Reading tickers from tickers.txt  (3 tickers)
  API key  : ****6789  (from environment)

  [1/3]  AAPL   → 5 annual reports fetched
  [2/3]  MSFT   → 5 annual reports fetched  (rate-limiting delay...)
  [3/3]  GOOGL  → 5 annual reports fetched

  Ticker  FiscalYear  Revenue       NetIncome   EPS
  AAPL    2025        391,035,000   93,736,000  6.11
  AAPL    2024        383,285,000   97,150,000  6.43
  ...

  Exported → combined_income_statements_2026-03-02T194500.csv  (15 rows)
```

**Error / warning:**
```
[2/3]  MSFT   → API error: Thank you for using Alpha Vantage. Our standard API
  rate limit is 25 requests per day.

  Free tier exhausted. Options:
  1. Wait until tomorrow (resets daily at midnight UTC)
  2. Upgrade to a paid Alpha Vantage plan
  3. Add --checkpoint flag to resume from MSFT on the next run

  Partial output written → combined_income_statements_partial_2026-03-02.csv
```

---

## Regulation map

| Framework | Control / Clause | Obligation |
|-----------|-----------------|------------|
| **SEBI LODR** | Regulation 33 | Annual and quarterly financial results for listed companies must be disclosed. This script aggregates that disclosed data for analysis. |
| **FEMA 1999 (India)** | FDI / Portfolio Investment | NRI investors in US-listed Indian ADRs require income statement data for valuation and tax reporting purposes. |
| **Income Tax Act 1961 (India)** | Foreign Asset Disclosure | Schedule FA in ITR requires disclosure of foreign assets and income. Income statement data supports accurate valuation. |
| **NIST CSF 2.0** | GV.RM-04 | Financial risk decisions must be supported by documented, traceable data. Timestamped batch exports establish data provenance. |
| **ISO 27001:2022** | A.8.1 — Asset Inventory | Data assets used in financial models must have documented sources and retrieval timestamps for audit purposes. |
| **RBI Master Directions** | Overseas Investment | Remittances for overseas investment require documented financial analysis of the target company. |

---

## Safety

- Run only in environments you are authorised to inspect.
- Do not commit credentials or API keys. Use environment variables or `.env` files.
- Treat all outputs as evidence — store with retrieval timestamps.

---

MIT licence · [rtapulse.com](https://rtapulse.com) · grcguy@rtapulse.com
