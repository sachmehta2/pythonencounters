# Fin-Tech

Finance data extraction and CSV exports.

## Setup
`pip install -r fin-tech/requirements.txt`

## Tools
- **yfinance-export/**: export daily OHLCV history to CSV
- **alphavantage-income-batch/**: batch income statement pulls to a single CSV (rate-limited)
- **screener-profitloss-export/**: export P&L table from Screener.in (HTML may change)
- **nse-ticker-list/**: snapshot NSE tickers + company names to CSV

Outputs are best-effort and provider formats can change.
