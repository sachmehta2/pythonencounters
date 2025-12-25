`url_crawl.py` crawls a website (same-domain links) and exports extracted page text into a Word document with a section per URL. Guardrails are included to prevent runaway crawls.

**Inputs:** start URL + output `.docx`. **Outputs:** Word document. **Run:** `python url_crawl.py --start-url https://example.com --output output.docx`. **Known limitations:** large sites can still generate large documents; extraction quality varies. **Safety:** respect site terms/permissions; tune `--max-pages`, `--max-depth`, and `--delay`.
