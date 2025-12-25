`combine_inc_stmt.py` batch-downloads annual income statements from Alpha Vantage for tickers listed in a text file and consolidates results into a single CSV.

**Inputs:** tickers file + API key. **Outputs:** `combined_income_statements_<timestamp>.csv`. **Run:** `python combine_inc_stmt.py` and follow prompts. **Known limitations:** strict rate limits; add backoff/retry and checkpointing for large lists. **Safety:** keep API keys out of the repo (env var or `.env`).
