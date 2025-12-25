`yf_invest.py` downloads historical daily OHLCV price data using Yahoo Finance (`yfinance`) for a ticker and lookback period (years), then exports a clean CSV.

**Inputs:** ticker + years. **Outputs:** daily CSV (script-defined filename). **Run:** `python yf_invest.py` and follow prompts. **Known limitations:** Yahoo data can be incomplete/adjusted and may throttle. **Safety:** informational use only; log date range fetched for traceability.
