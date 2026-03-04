# fin-tech

**Part of [Python Encounters](https://rtapulse.com/python-encounters/) — rtapulse.com**

Financial data extraction and analysis utilities. Scripts in this folder retrieve, clean, and export financial data for investment analysis, portfolio reconciliation, NRI compliance workflows, and third-party due diligence.

---

## Scripts

| Script | What it does | Published page |
|--------|-------------|----------------|
| [yfinance-export/yf_invest.py](yfinance-export/) | Download historical OHLCV price data from Yahoo Finance and export to CSV | [rtapulse.com](https://rtapulse.com/python-encounters/financial/yfinance-export/) |
| [screener-profitloss-export/screener.py](screener-profitloss-export/) | Scrape the P&L statement from Screener.in for an NSE company and export as CSV | [rtapulse.com](https://rtapulse.com/python-encounters/financial/screener-profitloss-export/) |
| [alphavantage-income-batch/combine_inc_stmt.py](alphavantage-income-batch/) | Batch-download annual income statements from Alpha Vantage API | [rtapulse.com](https://rtapulse.com/python-encounters/financial/alphavantage-income-batch/) |
| [nse-ticker-list/nsepy_list.py](nse-ticker-list/) | Export a dated snapshot of NSE ticker symbols and company names | [rtapulse.com](https://rtapulse.com/python-encounters/financial/nse-ticker-list/) |

---

## Setup

```bash
pip install -r fin-tech/requirements.txt
```

Each script folder contains a `README.md` with full install instructions, sample output, and a regulation/context map.

---

## Regulation frameworks covered

SEBI LODR · FEMA 1999 · Income Tax Act 1961 · Companies Act 2013 · RBI Master Directions · NIST CSF 2.0 · ISO 27001:2022

---

## Safety

- Data from Yahoo Finance, Screener.in, and Alpha Vantage is best-effort — verify against primary sources for any regulated use.
- Do not commit API keys. Use environment variables or `.env` files.
- Log retrieval timestamps on any output used as audit evidence.

---

MIT licence · [rtapulse.com](https://rtapulse.com) · grcguy@rtapulse.com
