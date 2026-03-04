# grc-tech

**Part of [Python Encounters](https://rtapulse.com/python-encounters/) — rtapulse.com**

Security, GRC, and audit utilities. Scripts in this folder are inspection-only and evidence-oriented — designed to produce structured, dated output suitable for audit workpapers.

---

## Scripts

| Script | What it does | Published page |
|--------|-------------|----------------|
| [ssl-cert-check/SSLcert.py](ssl-cert-check/) | Retrieve and inspect SSL/TLS certificate metadata for a hostname | [rtapulse.com](https://rtapulse.com/python-encounters/grc-tech/ssl-cert-check/) |
| [net-monitor/netmon.py](net-monitor/) | Capture active network connections with process context, export to CSV | [rtapulse.com](https://rtapulse.com/python-encounters/grc-tech/net-monitor/) |
| [file-hash-md5/generate_md5_hash.py](file-hash-md5/) | Compute MD5 hash of a file and write integrity receipt outputs | [rtapulse.com](https://rtapulse.com/python-encounters/grc-tech/file-hash-md5/) |
| [email-header-analyzer/email_header_analyzer.py](email-header-analyzer/) | Analyse email headers for SPF/DKIM/DMARC signals and From alignment | [rtapulse.com](https://rtapulse.com/python-encounters/grc-tech/email-header-analyzer/) |

## Control testing programme

Automated control evidence collection mapped to CIS benchmarks and regulatory frameworks.

| Programme | Platform | Checks | Published page |
|-----------|----------|--------|----------------|
| [control-testing/aws-iam-programme/](control-testing/aws-iam-programme/) | AWS IAM | 5 checks — root MFA, root access keys, password policy, inactive users, MFA on console users | [rtapulse.com](https://rtapulse.com/labs/control-testing/) |

More platforms coming: GCP, Linux, Windows, Network.

---

## Setup

```bash
pip install -r grc-tech/requirements.txt
```

Each script folder contains a `README.md` with full install instructions, sample output, and a regulation map.

---

## Regulation frameworks covered

NIST CSF 2.0 · ISO 27001:2022 · PCI DSS v4.0 · SOX ITGC · FFIEC CAT · DORA · CIS Controls v8 · HIPAA

---

## Safety

- Run only in environments you are authorised to inspect.
- Scripts are read-only — no resources are modified.
- Do not commit credentials. Use environment variables or named profiles.

---

MIT licence · [rtapulse.com](https://rtapulse.com) · grcguy@rtapulse.com
