`screener.py` scrapes the Profit & Loss table from Screener.in for an NSE company and exports it as CSV to avoid manual copy/paste.

**Inputs:** NSE ticker. **Outputs:** `<ticker>_profit_loss.csv`. **Run:** `python screener.py` and follow prompts. **Known limitations:** scraping can break when HTML changes or rate limits occur; failures are expected. **Safety:** add user-agent + delay and fail loudly if the table isn’t found (avoid partial outputs).
