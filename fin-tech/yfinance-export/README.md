# yfinance Export

**Part of [Python Encounters](https://rtapulse.com/python-encounters/) — rtapulse.com**
Script: [`yf_invest.py`](https://github.com/sachmehta2/pythonencounters/blob/main/fin-tech/yfinance-export/yf_invest.py) · [Published page](https://rtapulse.com/python-encounters/financial/yfinance-export/)

---

## The problem

Market data is frequently needed in financial audits, NRI investment reviews, and portfolio reconciliation workflows — and it is almost never in a clean, reproducible format when you need it. Yahoo Finance's web interface is fine for looking at a chart. It is not useful when you need a dated, source-attributed CSV that can be attached to a workpaper, loaded into a spreadsheet model, or compared against a broker statement. Downloading data manually is not repeatable and produces no audit trail of when the data was retrieved.

---

## Use case

You are performing a portfolio reconciliation for an NRI client's Indian equity holdings ahead of a FEMA compliance review. You need historical NAV and price data for ten securities across a three-year period to verify reported gains against market prices on specific dates. You run this script for each ticker with the relevant lookback period. Each CSV is timestamped at retrieval, includes the ticker and date range in the filename, and can be dropped directly into the reconciliation workbook.

---

## What the script does

yf_invest.py prompts for a ticker symbol and lookback period in years, calls the Yahoo Finance API via the yfinance library, and exports daily OHLCV data to a clean CSV. The filename includes the ticker and date range for traceability. Yahoo Finance data is best-effort — it may include adjusted prices and is subject to upstream availability. Log the retrieval timestamp and source attribution in any workpaper that uses this data.

---

## Install and run

```bash
# Install dependency
$ pip install yfinance

# Run and follow prompts
$ python3 yf_invest.py

# Enter ticker (e.g. RELIANCE.NS) and years (e.g. 3)
```

---

## Dependencies

- `yfinance` — Yahoo Finance API wrapper — downloads OHLCV data
- `pandas` — DataFrame handling and CSV export
- `Internet access` — Queries Yahoo Finance API — requires outbound HTTPS

---

## Sample output

**Success:**
```
Ticker     : RELIANCE.NS
  Period     : 3 years  (2023-03-02 → 2026-03-02)
  Rows       : 742 trading days

  Date        Open      High      Low       Close     Volume
  2023-03-02  2381.00   2410.50   2375.20   2398.75   5,821,300
  2023-03-03  2400.00   2428.90   2396.00   2421.40   4,293,100
  ...

  Exported → RELIANCE_NS_2023-03-02_2026-03-02.csv  (742 rows)
```

**Error / warning:**
```
Ticker     : INVALIDTICKER
  ERROR: No data returned for INVALIDTICKER. Check ticker symbol.
  Use .NS suffix for NSE-listed stocks (e.g. TCS.NS, INFY.NS).
  Use .BO suffix for BSE-listed stocks.

  Yahoo Finance may throttle requests — if data is empty for a
  valid ticker, wait 60 seconds and retry.
```

---

## Regulation map

| Framework | Control / Clause | Obligation |
|-----------|-----------------|------------|
| **FEMA 1999 (India)** | Schedule 3 — Portfolio Investment | NRIs holding Indian equities must be able to reconcile investment values against market prices for repatriation and reporting purposes. |
| **Income Tax Act 1961 (India)** | Section 112A — LTCG | Long-term capital gains on listed equities require date-specific acquisition and disposal price data, sourced and attributable. |
| **SEBI (India)** | LODR — Disclosure | Listed company securities price data underpins material non-public information assessments and insider trading monitoring. |
| **NIST CSF 2.0** | GV.RM-04 | Financial risk quantification requires accurate, traceable market data. Timestamped CSV downloads establish data provenance. |
| **ISO 27001:2022** | A.8.1 — Asset Management | Data assets used in financial analysis must have documented provenance, including source and retrieval date. |
| **RBI / FEMA Audit** | External Liabilities and Assets | Audit of NRI investment portfolios requires independently sourced historical price data to verify reported valuations. |

---

## Safety

- Run only in environments you are authorised to inspect.
- Do not commit credentials or API keys. Use environment variables or `.env` files.
- Treat all outputs as evidence — store with retrieval timestamps.

---

MIT licence · [rtapulse.com](https://rtapulse.com) · grcguy@rtapulse.com
