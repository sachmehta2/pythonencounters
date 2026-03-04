# NSE Ticker List

**Part of [Python Encounters](https://rtapulse.com/python-encounters/) — rtapulse.com**
Script: [`nsepy_list.py`](https://github.com/sachmehta2/pythonencounters/blob/main/fin-tech/nse-ticker-list/nsepy_list.py) · [Published page](https://rtapulse.com/python-encounters/financial/nse-ticker-list/)

---

## The problem

Working with Indian listed equities requires a clean, current list of NSE symbols. NSE's own website provides this, but downloading and formatting it manually every time you start a new model or refresh a screening dataset is friction. Symbol changes, delistings, and new listings mean that a list from three months ago can cause silent errors in downstream scripts — a ticker that no longer exists returns no data without an obvious error message.

---

## Use case

You are building a systematic screening model across all NSE-listed companies to identify candidates for a SEBI-compliant portfolio strategy. Before running any financial data queries, you need the current universe. You run this script, get a dated CSV with all active symbols and company names, load it as your ticker reference file, and know that every downstream API call is working against a current universe — with the retrieval date embedded in the filename for the audit trail.

---

## What the script does

nsepy_list.py calls the nsepy library to retrieve the list of active NSE equity instruments and exports the symbol and company name columns to a CSV named nse_tickers_with_names_YYYYMMDD.csv. The date in the filename makes each snapshot independently identifiable. Run this at the start of any workflow that will query NSE data to establish a current baseline. Note that nsepy upstream availability varies — if the run fails, retry during NSE trading hours.

---

## Install and run

```bash
# Install dependency
$ pip install nsepy

# Run — no prompts
$ python3 nsepy_list.py

# Output: nse_tickers_with_names_YYYYMMDD.csv
```

---

## Dependencies

- `nsepy` — NSE data library — retrieves the active equity instrument list
- `pandas` — DataFrame handling and CSV export
- `Internet access` — Queries NSE data source via nsepy — requires outbound HTTPS

---

## Sample output

**Success:**
```
Retrieving NSE equity list via nsepy...

  Symbol      Company Name
  RELIANCE    Reliance Industries Limited
  TCS         Tata Consultancy Services Limited
  HDFCBANK    HDFC Bank Limited
  INFY        Infosys Limited
  ...

  Total symbols : 1,847

  Exported → nse_tickers_with_names_20260302.csv
```

**Error / warning:**
```
Retrieving NSE equity list via nsepy...

  ERROR: nsepy connection failed or empty response received.
  NSE data availability can vary — common causes:
  1. Exchange is closed (weekend / public holiday)
  2. NSE upstream endpoint has changed
  3. Rate limiting — wait and retry

  Try running during NSE trading hours (09:15–15:30 IST, Mon–Fri).
  Use --force flag to write partial output if available.
```

---

## Regulation map

| Framework | Control / Clause | Obligation |
|-----------|-----------------|------------|
| **SEBI (India)** | LODR — Disclosure Obligations | SEBI-regulated entities must maintain accurate records of listed securities they hold or screen. A dated ticker snapshot provides the reference universe. |
| **FEMA 1999 (India)** | Schedule 3 — Portfolio Investment Scheme | NRI equity investments under PIS must be in listed securities. A current NSE ticker list confirms the investment universe for compliance review. |
| **Income Tax Act 1961 (India)** | Section 112A — LTCG on Equities | Capital gains calculations on listed equity require confirmation that securities were listed on a recognised exchange at the time of transaction. |
| **NIST CSF 2.0** | GV.RM-04 — Risk Data | Reference data used in financial risk models must have documented provenance. Date-stamped snapshots establish when the universe was defined. |
| **ISO 27001:2022** | A.8.1 — Asset Inventory | Data assets underpinning financial analysis workflows must be documented and sourced — dated snapshots satisfy this for reference data. |
| **RBI / SEBI Audit Trail** | Investment Record-keeping | Institutional investors must be able to demonstrate the universe of securities considered at any given point in time for regulatory review. |

---

## Safety

- Run only in environments you are authorised to inspect.
- Do not commit credentials or API keys. Use environment variables or `.env` files.
- Treat all outputs as evidence — store with retrieval timestamps.

---

MIT licence · [rtapulse.com](https://rtapulse.com) · grcguy@rtapulse.com
