# SSL Cert Check

**Part of [Python Encounters](https://rtapulse.com/python-encounters/) — rtapulse.com**
Script: [`SSLcert.py`](https://github.com/sachmehta2/pythonencounters/blob/main/grc-tech/ssl-cert-check/SSLcert.py) · [Published page](https://rtapulse.com/python-encounters/grc-tech/ssl-cert-check/)

---

## The problem

Expired and misconfigured TLS certificates are one of the most common findings in external-facing system reviews — and one of the most embarrassing. A certificate that expired last week tells an auditor that no monitoring process caught it, that nobody reviewed the renewal schedule, and that the control supposedly managing it is either misconfigured or not running. Certificate authority mismatch, wildcard scope creep, and SAN gaps create their own set of findings. None of this is visible from a browser padlock.

---

## Use case

You are running a pre-engagement reconnaissance sweep before an FFIEC CAT assessment at a regional bank. The system owner hands you a spreadsheet of 40 external-facing hostnames and says all certs are managed and monitored. You batch-run this script. Three come back with certificates expiring in under 30 days. Two show SANs that do not match the hostname in the spreadsheet. One has a self-signed cert on a production endpoint. Each is a finding before fieldwork has started.

---

## What the script does

SSLcert.py connects to a hostname over port 443 (or a specified port), retrieves the TLS certificate presented by the server, and prints a structured report: subject CN, issuer, SAN entries, validity window, and days to expiry. It uses Python's standard ssl library — no additional dependencies. Use --insecure only when you need to retrieve metadata from an invalid or self-signed certificate. Results are observation-level — the script reports what the server presented, not what cipher suites it supports.

---

## Install and run

```bash
# No external dependencies — stdlib only
$ python3 SSLcert.py example.com

# Custom port
$ python3 SSLcert.py example.com --port 8443

# Retrieve metadata from self-signed / invalid cert
$ python3 SSLcert.py internal.host --insecure
```

---

## Dependencies

- `ssl (stdlib)` — Connects to the host and retrieves the presented TLS certificate
- `socket (stdlib)` — Resolves hostname to IP for the connection
- `Network access` — Script must be able to reach the target host on the specified port

---

## Sample output

**Success:**
```
Subject CN   : example.com
  Issuer       : Let's Encrypt Authority X3
  SAN entries  : example.com, www.example.com
  Valid from   : 2025-11-01
  Valid to     : 2026-01-30
  Days to exp  : 91 — valid
  Serial       : 03:A1:4B:...
```

**Error / warning:**
```
Subject CN   : example.com
  Issuer       : Let's Encrypt Authority X3
  SAN entries  : example.com
  Valid from   : 2025-09-01
  Valid to     : 2026-01-08
  Days to exp  : 18 — expiring soon
  Serial       : 04:C2:9F:...

  ⚠  Certificate expires in 18 days. Renew immediately.
```

---

## Regulation map

| Framework | Control / Clause | Obligation |
|-----------|-----------------|------------|
| **NIST CSF 2.0** | PR.DS-2 | Data in transit must be protected. Expired or misconfigured TLS certificates represent a failure of this control. |
| **ISO 27001:2022** | A.10.1.1 | Cryptographic controls must be correctly applied and maintained. Certificate expiry without renewal monitoring is a control gap. |
| **PCI DSS v4.0** | 6.3.3 / 4.2.1 | All software and system components must be protected from known vulnerabilities; encryption of cardholder data in transit is mandatory. |
| **FFIEC CAT** | Baseline — Infrastructure | Certificate management is a baseline infrastructure security control for financial institutions. |
| **DORA (EU)** | Article 9 | ICT systems must use current and properly configured encryption. Expired certificates breach this requirement. |
| **SOC 2 (Trust Principles)** | Availability / Confidentiality | Lapsed TLS certificates can cause service outages and expose data in transit — both reportable under SOC 2 criteria. |

---

## Safety

- Run only in environments you are authorised to inspect.
- Do not commit credentials or API keys. Use environment variables or `.env` files.
- Treat all outputs as evidence — store with retrieval timestamps.

---

MIT licence · [rtapulse.com](https://rtapulse.com) · grcguy@rtapulse.com
