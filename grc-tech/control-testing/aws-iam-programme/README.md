# AWS IAM Identity Hardening — Audit Programme

**Part of the Control Testing Automation Theatre**
Published at: [rtapulse.com/labs/control-testing](https://rtapulse.com/labs/control-testing/)

---

Five scripts that form a single, coherent IAM audit programme. Run them in sequence on any AWS account. Each produces a PASS / FAIL / WARN verdict with a structured JSON evidence package suitable for workpaper attachment.

The programme covers the five most frequently cited IAM findings in SOX ITGC, PCI DSS, and FFIEC CAT assessments. One boto3 session. Read-only permissions throughout.

---

## Checks

| Script | Check ID | What it tests | CIS Control | Risk if failing |
|--------|----------|---------------|-------------|-----------------|
| `aws_01_root_mfa.py` | AWS-01 | Root account MFA status | 1.4 | CRITICAL |
| `aws_02_root_access_keys.py` | AWS-02 | Root account access keys | 1.12 | CRITICAL |
| `aws_03_iam_password_policy.py` | AWS-03 | IAM password policy (7 sub-checks) | 1.8–1.11 | HIGH |
| `aws_04_inactive_iam_users.py` | AWS-04 | Inactive IAM users (>90 days) | 1.15 | HIGH |
| `aws_05_mfa_console_users.py` | AWS-05 | MFA on all console-enabled users | 1.10 | HIGH |

---

## Regulation mapping

| Framework | Controls covered |
|-----------|-----------------|
| NIST CSF 2.0 | PR.AC-1, PR.AC-4, PR.AC-7 |
| SOX ITGC | AC-01 through AC-05 |
| PCI DSS v4.0 | 8.2.1, 8.3, 8.5, 8.8 |
| ISO 27001:2022 | A.9.2.3, A.9.2.6, A.9.4.2, A.9.4.3 |
| FFIEC CAT | Baseline — Identity & Access Management |
| DORA (EU) | Article 9 — ICT security |
| HIPAA Security Rule | §164.312 (AWS-03 only) |

---

## Prerequisites

```bash
pip install boto3
```

Minimal read-only IAM policy for the executing identity:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:GetAccountSummary",
        "iam:GetAccountPasswordPolicy",
        "iam:ListUsers",
        "iam:GetLoginProfile",
        "iam:ListAccessKeys",
        "iam:GetAccessKeyLastUsed",
        "iam:ListMFADevices",
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

No write permissions required or used.

---

## Quick run — all five

```bash
# Default credentials (env vars / instance role)
python3 aws_01_root_mfa.py
python3 aws_02_root_access_keys.py
python3 aws_03_iam_password_policy.py
python3 aws_04_inactive_iam_users.py
python3 aws_05_mfa_console_users.py

# Named profile, save JSON evidence for each
for script in aws_0*.py; do
  python3 "$script" --profile my-audit-role --save
done

# JSON-only for pipeline / CI
python3 aws_01_root_mfa.py --json-only | jq .result
```

Exit codes: `0` = PASS · `1` = FAIL · `2` = WARN

---

## Output format

Every script produces a terminal report and a JSON evidence package:

```json
{
  "check_id": "AWS-01",
  "check_name": "Root Account MFA Status",
  "cis_reference": "CIS AWS Foundations Benchmark v2.0 — Control 1.4",
  "regulation_map": "NIST CSF PR.AC-7 | SOX ITGC AC-01 | PCI DSS 8.5 | ...",
  "account_id": "123456789012",
  "timestamp": "2026-03-02T19:45:00Z",
  "result": "PASS",
  "risk_rating": "N/A",
  "finding": "Root account MFA is enabled.",
  "remediation": "None required.",
  "raw": { "AccountMFAEnabled": 1 }
}
```

---

## Safety

- All scripts are read-only. No resources are created, modified, or deleted.
- Run only in accounts you are authorised to inspect.
- Do not commit AWS credentials. Use named profiles, environment variables, or instance roles.
- JSON evidence files may contain account IDs — handle accordingly.

---

## Companion audit programme

The audit programme pages (written for the GRC manager, not just the script executor) are published at:

- [rtapulse.com/labs/control-testing/](https://rtapulse.com/labs/control-testing/)

---

MIT licence · [rtapulse.com](https://rtapulse.com) · grcguy@rtapulse.com
