# Email Header Analyzer

**Part of [Python Encounters](https://rtapulse.com/python-encounters/) — rtapulse.com**
Script: [`email_header_analyzer.py`](https://github.com/sachmehta2/pythonencounters/blob/main/grc-tech/email-header-analyzer/email_header_analyzer.py) · [Published page](https://rtapulse.com/python-encounters/grc-tech/email-header-analyzer/)

---

## The problem

Phishing remains the primary initial access vector in the majority of recorded breaches. When a suspicious email is flagged — by a user, a filter, or an alert — someone needs to triage it quickly. The raw headers contain everything needed to assess whether the sender domain is authenticated, whether the message traversed a secure channel, and whether the visible From address matches the actual return path. Without a tool, this means reading through dozens of Received lines and authentication result strings manually, which is slow and error-prone under pressure.

---

## Use case

Your security operations team flags an email claiming to be from a tier-one banking partner requesting an urgent wire transfer confirmation. The email passed the spam filter. You export the raw headers to a text file and run this script. Output: SPF soft-fail on the sending domain, DKIM absent, From domain does not match Return-Path, and no DMARC record published. Four signals pointing in the same direction. The investigation is thirty seconds old and you already have a documented triage output to attach to the incident ticket.

---

## What the script does

email_header_analyzer.py reads a plain-text file containing raw email headers (exported from any mail client), parses the Authentication-Results, Received-SPF, DKIM-Signature, From, and Return-Path headers, and performs a DNS lookup against the sending domain's DMARC record. Output is a structured console report. No mail server access required. Results are heuristic where Authentication-Results is absent or inconsistent — the script flags ambiguity rather than asserting certainty.

---

## Install and run

```bash
# Install dependency
$ pip install dnspython

# Analyse a saved header file
$ python3 email_header_analyzer.py -i header.txt

# Save report to file
$ python3 email_header_analyzer.py -i header.txt --output triage_report.txt
```

---

## Dependencies

- `dnspython` — DNS lookup for DMARC record on the sender domain
- `email, re (stdlib)` — Header parsing — no external parser needed
- `DNS access` — Script queries _dmarc.<domain> — requires outbound DNS resolution

---

## Sample output

**Success:**
```
From           : noreply@trusted-bank.com
  Return-Path    : noreply@trusted-bank.com  ✓ match
  SPF            : pass  (sending IP authorised for trusted-bank.com)
  DKIM           : pass  (signed by trusted-bank.com)
  DMARC          : policy=reject  published at _dmarc.trusted-bank.com
  TLS hint       : TLS 1.3 observed in Received headers
  Alignment      : SPF + DKIM aligned — domain consistent
```

**Error / warning:**
```
From           : payments@trusted-bank.com
  Return-Path    : bounce@mailer99.net         ✗ mismatch
  SPF            : softfail  (sending IP not listed in SPF record)
  DKIM           : absent   (no DKIM-Signature header found)
  DMARC          : none     (no _dmarc record for trusted-bank.com)
  TLS hint       : none observed
  Alignment      : ⚠  From/Return-Path mismatch — likely spoofed sender
```

---

## Regulation map

| Framework | Control / Clause | Obligation |
|-----------|-----------------|------------|
| **DORA (EU)** | Article 17 | Incident detection and response procedures must include capability to triage phishing and email-borne threats. |
| **NIST CSF 2.0** | RS.AN-1 | Notifications from detection systems must be investigated. Header analysis is the first step in email threat investigation. |
| **ISO 27001:2022** | A.16.1.2 | Information security incidents must be reported and triaged. Email header analysis supports incident classification. |
| **PCI DSS v4.0** | 12.10.5 | Organisations must have incident response capabilities covering phishing and social engineering. Header analysis is a core triage technique. |
| **FFIEC CAT** | Evolving — Threat Intelligence | Financial institutions must have processes to detect and respond to phishing targeting employees and customers. |
| **CIS Controls v8** | Control 9 — Email / Web Browser Protection | Email authentication (SPF/DKIM/DMARC) must be configured and its output must be reviewable during incidents. |

---

## Safety

- Run only in environments you are authorised to inspect.
- Do not commit credentials or API keys. Use environment variables or `.env` files.
- Treat all outputs as evidence — store with retrieval timestamps.

---

MIT licence · [rtapulse.com](https://rtapulse.com) · grcguy@rtapulse.com
