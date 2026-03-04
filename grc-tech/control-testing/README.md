# control-testing

**Part of [Python Encounters](https://rtapulse.com/python-encounters/) — rtapulse.com**

Python scripts for automated control evidence collection. Every script maps to CIS benchmarks and regulatory frameworks, produces structured PASS/FAIL output, and is designed to generate audit-ready evidence in a single run.

Published companion: [Control Testing Automation Theatre](https://rtapulse.com/labs/control-testing/)

---

## Programmes

| Folder | Platform | Checks | Status |
|--------|----------|--------|--------|
| [aws-iam-programme/](aws-iam-programme/) | AWS IAM | 5 checks — root MFA, root access keys, password policy, inactive users, MFA on console users | ✅ Published |
| gcp-iam-programme/ | GCP IAM | Coming next | 🔜 Planned |
| linux-baseline/ | Linux | Coming next | 🔜 Planned |
| windows-baseline/ | Windows | Coming next | 🔜 Planned |
| network-controls/ | Network infrastructure | Coming next | 🔜 Planned |

---

## Design principles

Every script in this library follows the same structure:

1. **Connect** — establish a read-only API or CLI session
2. **Check** — run the specific control test
3. **Build evidence** — structure the result as a dated, labelled artifact
4. **Report** — print PASS / FAIL / WARN with exit code (0 / 1 / 2)

Scripts are read-only. None write, modify, or delete resources.

---

## Regulation coverage

All checks in this library map to one or more of: NIST CSF 2.0, CIS Controls v8, SOX ITGC, PCI DSS v4.0, ISO 27001:2022, FFIEC CAT, DORA, HIPAA. Full regulation tables are in each programme README and on the published pages.

---

## Quick run — AWS IAM programme

```bash
pip install boto3

# Run all 5 checks against default AWS profile
python aws-iam-programme/aws_01_root_mfa.py
python aws-iam-programme/aws_02_root_access_keys.py
python aws-iam-programme/aws_03_iam_password_policy.py
python aws-iam-programme/aws_04_inactive_iam_users.py
python aws-iam-programme/aws_05_mfa_console_users.py

# Named profile
python aws-iam-programme/aws_01_root_mfa.py --profile audit-readonly
```

See [aws-iam-programme/README.md](aws-iam-programme/README.md) for full documentation, required IAM permissions, and sample output.

---

## Safety

- Read-only. No AWS resources are modified.
- Do not commit credentials. Use named profiles, environment variables, or IAM roles.
- All output is local — nothing is transmitted outside your environment.

---

MIT licence · [rtapulse.com](https://rtapulse.com) · grcguy@rtapulse.com
