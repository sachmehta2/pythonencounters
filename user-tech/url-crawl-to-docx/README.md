# URL Crawl to DOCX

**Part of [Python Encounters](https://rtapulse.com/python-encounters/) — rtapulse.com**
Script: [`url_crawl.py`](https://github.com/sachmehta2/pythonencounters/blob/main/user-tech/url-crawl-to-docx/url_crawl.py) · [Published page](https://rtapulse.com/python-encounters/user-tech/url-crawl-to-docx/)

---

## The problem

Auditors and compliance teams regularly need to capture the published content of a website — a vendor's privacy policy, an organisation's published security standards, a regulator's guidance page — as a point-in-time record. Manual copy/paste across dozens of pages is slow and the output is unstructured. Screenshots are not searchable. A dated Word document with one section per page is a usable, storable, citable evidence artifact.

---

## Use case

You are scoping a third-party vendor risk assessment. The vendor's security and compliance documentation lives across fourteen pages of their public website. You need a snapshot dated to the start of the assessment as the baseline. You run this script against the vendor's documentation section, set max-pages to 20, and get a Word document with each page as a numbered section, all text extracted, and a table of contents. That document is date-stamped and attached to the assessment workpaper as the point-in-time baseline.

---

## What the script does

url_crawl.py starts from a given URL, follows same-domain links up to a configurable depth and page limit, extracts visible text from each page using BeautifulSoup, and writes a structured Word document using python-docx. Each page becomes a numbered section with the URL as the heading. Use --max-pages, --max-depth, and --delay to control crawl scope and be considerate of server load. Respect the target site's terms of service.

---

## Install and run

```bash
# Install dependencies
$ pip install requests beautifulsoup4 python-docx

# Basic crawl
$ python3 url_crawl.py --start-url https://example.com --output snapshot.docx

# Limit scope
$ python3 url_crawl.py --start-url https://example.com/docs --max-pages 20 --max-depth 3 --output vendor_docs.docx
```

---

## Dependencies

- `requests` — HTTP GET for each page in the crawl
- `beautifulsoup4` — HTML parsing and visible text extraction
- `python-docx` — Word document assembly — one section per crawled URL
- `Network access` — Must be able to reach the target domain

---

## Sample output

**Success:**
```
Start URL  : https://example.com/security/
  Max pages  : 20  |  Max depth : 3  |  Delay : 1s

  Crawling...
    [1/20]  /security/             → 1,204 words
    [2/20]  /security/policy/      → 3,812 words
    [3/20]  /security/certs/       → 847 words
    ...
    [14/20] /security/contact/     → 312 words

  Writing document → vendor_docs_2026-03-02.docx
  Done — 14 pages, 24,601 words, 1 document.
```

**Error / warning:**
```
WARNING: Page /security/legal/ returned 403 Forbidden — skipped.
  WARNING: Max pages (20) reached — crawl stopped at depth 2.
  Pages captured: 20 of estimated 35+ available.

  To capture more: increase --max-pages or run against specific sub-paths.
  Output still written → vendor_docs_partial_2026-03-02.docx
```

---

## Regulation map

| Framework | Control / Clause | Obligation |
|-----------|-----------------|------------|
| **GDPR / UK GDPR** | Article 13/14 — Privacy Notices | Controllers must maintain accessible privacy notices. Crawl snapshots provide dated evidence of published notice content. |
| **ISO 27001:2022** | A.18.1.1 | Legal, statutory, and contractual requirements must be documented. Website snapshots capture externally published security commitments. |
| **PCI DSS v4.0** | 12.9 | Service provider compliance obligations must be documented. Crawling a vendor's compliance page captures their published assertions. |
| **NIST CSF 2.0** | GV.SC-04 | Suppliers and third parties must be assessed. Published security documentation is a key input to third-party risk assessments. |
| **DORA (EU)** | Article 28 — Third-party ICT risk | Due diligence on ICT service providers requires review of their published security and resilience commitments. |
| **SEBI CSCRF** | Third-party Risk | SEBI-regulated entities must assess vendors' security posture — published documentation is a baseline evidence source. |

---

## Safety

- Run only in environments you are authorised to inspect.
- Do not commit credentials or API keys. Use environment variables or `.env` files.
- Treat all outputs as evidence — store with retrieval timestamps.

---

MIT licence · [rtapulse.com](https://rtapulse.com) · grcguy@rtapulse.com
