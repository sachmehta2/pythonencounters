`nsepy_list.py` exports a snapshot of NSE tickers with company names using `nsepy`, producing a dated CSV.

**Inputs:** none. **Outputs:** `nse_tickers_with_names_YYYYMMDD.csv`. **Run:** `python nsepy_list.py`. **Known limitations:** weekend checks don’t cover exchange holidays; upstream availability varies. **Safety:** add `--force` and log retrieval timestamp so snapshots remain auditable.
