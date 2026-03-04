# Screener Profit/Loss Export

**Part of [Python Encounters](https://rtapulse.com/python-encounters/) — rtapulse.com**
Script: [`screener.py`](https://github.com/sachmehta2/pythonencounters/blob/main/fin-tech/screener-profitloss-export/screener.py) · [Published page](https://rtapulse.com/python-encounters/financial/screener-profitloss-export/)

---

## The problem

Screener.in is one of the best freely available sources of Indian listed company financials. Its P&L tables are clean, consistent, and multi-year. But they live in a web page. Every analyst doing fundamental analysis or vendor due diligence on an Indian listed company manually copies these tables into a spreadsheet, loses formatting, fixes columns, and repeats the process next quarter. There is no download button. The data is there — the workflow is just broken.

---

## Use case

You are conducting due diligence on a potential Indian technology vendor as part of a third-party risk assessment. The vendor is NSE-listed. You need five years of P&L data to assess revenue trend, margin stability, and debt position before the business team signs a multi-year contract. You run this script with the vendor's NSE ticker, get a clean CSV in thirty seconds, and load it directly into your due diligence model — no manual reformatting.

---

## What the script does

screener.py sends an HTTP request to Screener.in with a user-agent header, parses the Profit & Loss table from the company page using BeautifulSoup, and exports the multi-year data as a CSV named <ticker>_profit_loss.csv. Screener.in occasionally changes its page structure — if the table is not found, the script fails loudly rather than writing a partial output. Add a delay between runs if processing multiple tickers.

---

## Install and run

```bash
# Install dependencies
$ pip install requests beautifulsoup4

# Run and follow prompts
$ python3 screener.py

# Enter NSE ticker when prompted (e.g. TCS, INFY, HDFCBANK)
```

---

## Dependencies

- `requests` — HTTP GET to Screener.in with user-agent header
- `beautifulsoup4` — HTML parsing to extract the P&L table
- `Internet access` — Queries screener.in — requires outbound HTTPS

---

## Sample output

**Success:**
```
Ticker  : TCS
  Source  : https://www.screener.in/company/TCS/

  Metric              Mar-21    Mar-22    Mar-23    Mar-24    Mar-25
  Revenue             164,177   191,754   225,458   240,893   255,324
  Operating Profit     41,208    48,902    54,318    57,890    61,204
  Net Profit           32,430    38,617    42,303    45,908    47,112

  Exported → TCS_profit_loss.csv
```

**Error / warning:**
```
Ticker  : INVALIDCO
  Source  : https://www.screener.in/company/INVALIDCO/

  ERROR: Company not found or P&L table not present on page.
  Verify the ticker is an NSE symbol listed on Screener.in.
  If the page exists but the table is absent, Screener may have
  changed its HTML structure — check and update the parser.
```

---

## Regulation map

| Framework | Control / Clause | Obligation |
|-----------|-----------------|------------|
| **SEBI LODR** | Regulation 33 — Financial Results | Listed companies must publish quarterly and annual P&L results. This script captures that published data for analysis. |
| **Companies Act 2013 (India)** | Section 129 — Financial Statements | Auditors and analysts reviewing Indian company financials may use this data as a starting point for further investigation from primary sources. |
| **FEMA 1999 (India)** | FDI / Portfolio Investment | NRIs and foreign investors assessing Indian listed companies for investment decisions require multi-year P&L data for informed analysis. |
| **NIST CSF 2.0** | GV.RM-04 | Third-party financial risk assessments require quantitative financial data. Traceable CSV export supports documented risk decisions. |
| **ISO 27001:2022** | A.18.1 — Compliance | Vendor due diligence programmes require documented financial analysis as part of third-party risk management obligations. |
| **RBI Master Directions** | Outsourcing / Third-party Risk | Banks must assess financial health of outsourced service providers. P&L trend analysis is a standard component of this assessment. |

---

## Safety

- Run only in environments you are authorised to inspect.
- Do not commit credentials or API keys. Use environment variables or `.env` files.
- Treat all outputs as evidence — store with retrieval timestamps.

---

MIT licence · [rtapulse.com](https://rtapulse.com) · grcguy@rtapulse.com
