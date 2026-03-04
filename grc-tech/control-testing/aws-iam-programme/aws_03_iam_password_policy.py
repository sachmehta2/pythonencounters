#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AWS-03 — IAM Account Password Policy
  Control Testing Automation Theatre — rtapulse.com/labs/control-testing/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  CIS Reference : CIS AWS Foundations Benchmark v2.0 — Controls 1.8–1.11
  Regulation map: NIST CSF PR.AC-1 | SOX ITGC AC-03 | PCI DSS 8.3
                  ISO 27001 A.9.4.3 | FFIEC CAT Baseline | HIPAA §164.312

  What it checks: Whether the IAM account password policy meets all
                  CIS-required thresholds across 7 individual sub-checks:

                  1. MinimumPasswordLength         >= 14       (CIS 1.8)
                  2. RequireUppercaseCharacters     = True      (CIS 1.8)
                  3. RequireLowercaseCharacters     = True      (CIS 1.8)
                  4. RequireNumbers                 = True      (CIS 1.8)
                  5. RequireSymbols                 = True      (CIS 1.8)
                  6. MaxPasswordAge                 <= 365 days (CIS 1.9)
                  7. PasswordReusePrevention        >= 24       (CIS 1.11)

                  Overall result:
                  ALL sub-checks pass → PASS
                  1+ sub-checks fail  → FAIL (HIGH)
                  No policy exists    → FAIL (CRITICAL)

  Note          : Password policy applies to IAM users only. If your
                  environment uses SSO / Identity Centre exclusively,
                  document this as a compensating control and note in
                  the workpaper that local IAM user logins are disabled.

  Prerequisites : pip install boto3
                  AWS credentials with iam:GetAccountPasswordPolicy
                  Recommended: read-only IAM role

  Output        : JSON report + human-readable terminal
  Runtime       : < 5 seconds

  Author        : rtapulse.com
  Published     : 2026-03-02
  Licence       : MIT — use freely, attribute appreciated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import boto3
import json
import sys
from datetime import datetime, timezone
from botocore.exceptions import ClientError, NoCredentialsError

# ── Configuration ────────────────────────────────────────────────────
CHECK_ID   = "AWS-03"
CHECK_NAME = "IAM Account Password Policy"
CIS_REF    = "CIS AWS Foundations Benchmark v2.0 — Controls 1.8–1.11"
REGULATION = "NIST CSF PR.AC-1 | SOX ITGC AC-03 | PCI DSS 8.3 | ISO 27001 A.9.4.3 | FFIEC CAT | HIPAA §164.312"

# CIS thresholds — single source of truth
POLICY_REQUIREMENTS = {
    "MinimumPasswordLength":      {"operator": ">=", "threshold": 14,   "cis": "1.8",  "label": "Min password length >= 14"},
    "RequireUppercaseCharacters": {"operator": "==", "threshold": True,  "cis": "1.8",  "label": "Require uppercase characters"},
    "RequireLowercaseCharacters": {"operator": "==", "threshold": True,  "cis": "1.8",  "label": "Require lowercase characters"},
    "RequireNumbers":             {"operator": "==", "threshold": True,  "cis": "1.8",  "label": "Require numbers"},
    "RequireSymbols":             {"operator": "==", "threshold": True,  "cis": "1.8",  "label": "Require symbols"},
    "MaxPasswordAge":             {"operator": "<=", "threshold": 365,   "cis": "1.9",  "label": "Max password age <= 365 days"},
    "PasswordReusePrevention":    {"operator": ">=", "threshold": 24,    "cis": "1.11", "label": "Password reuse prevention >= 24"},
}

# ── Colour codes ──────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
DIM    = "\033[2m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


# ── CONNECT ───────────────────────────────────────────────────────────
def connect(profile_name: str = None, region: str = "us-east-1"):
    """
    Establish AWS session. Returns (iam_client, sts_client).
    Credential resolution order:
      1. Named profile (--profile flag)
      2. Environment variables
      3. Instance profile / ECS task role
      4. ~/.aws/credentials default profile
    """
    try:
        session = boto3.Session(profile_name=profile_name, region_name=region)
        return session.client("iam"), session.client("sts")
    except Exception:
        return None, None


# ── CHECK ─────────────────────────────────────────────────────────────
def check(iam_client, sts_client) -> dict:
    """
    Retrieve the IAM password policy and evaluate each sub-check
    against CIS thresholds. Returns a unified result dict including
    per-sub-check detail for the workpaper.

    Sub-check evaluation:
      - operator ">="  → actual >= threshold
      - operator "<="  → actual <= threshold
      - operator "=="  → actual == threshold (used for booleans)

    If no password policy exists the overall result is FAIL (CRITICAL)
    because AWS defaults allow passwords with no complexity requirements.
    """
    timestamp  = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    account_id = "UNKNOWN"

    try:
        account_id = sts_client.get_caller_identity().get("Account", "UNKNOWN")
    except Exception:
        pass

    # ── No-policy case ───────────────────────────────────────────────
    try:
        response = iam_client.get_account_password_policy()
        policy   = response.get("PasswordPolicy", {})

    except ClientError as e:
        code = e.response["Error"]["Code"]

        if code == "NoSuchEntity":
            # No password policy configured — AWS defaults apply (weak)
            return {
                "result":      "FAIL",
                "risk_rating": "CRITICAL",
                "finding":     "No IAM account password policy is configured. AWS defaults allow "
                               "passwords of any length with no complexity, expiry, or reuse controls. "
                               "All 7 CIS sub-checks fail by absence.",
                "remediation": "Configure an IAM account password policy via Console → IAM → "
                               "Account settings → Edit password policy. Apply all 7 CIS thresholds "
                               "as a minimum: min length 14, uppercase, lowercase, numbers, symbols, "
                               "max age 365 days, reuse prevention 24.",
                "sub_checks":  {k: {"result": "FAIL", "actual": "NOT SET",
                                    "threshold": f"{v['operator']} {v['threshold']}",
                                    "label": v["label"]}
                                for k, v in POLICY_REQUIREMENTS.items()},
                "account_id":  account_id,
                "timestamp":   timestamp,
                "raw":         {"policy_exists": False},
            }

        if code == "AccessDenied":
            return {
                "result":      "WARN",
                "risk_rating": "UNKNOWN",
                "finding":     f"AWS API error (AccessDenied): insufficient permission to read "
                               f"password policy. Check could not complete.",
                "remediation": "Ensure the executing IAM identity has iam:GetAccountPasswordPolicy.",
                "sub_checks":  {},
                "account_id":  account_id,
                "timestamp":   timestamp,
                "raw":         {"error_code": code},
            }

        # Other client error
        msg = e.response["Error"]["Message"]
        return {
            "result":      "WARN",
            "risk_rating": "UNKNOWN",
            "finding":     f"AWS API error ({code}): {msg}.",
            "remediation": "Verify permissions and re-run.",
            "sub_checks":  {},
            "account_id":  account_id,
            "timestamp":   timestamp,
            "raw":         {"error_code": code, "error_message": msg},
        }

    except NoCredentialsError:
        return {
            "result":      "WARN",
            "risk_rating": "UNKNOWN",
            "finding":     "No AWS credentials found.",
            "remediation": "Run: aws configure  or set AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY",
            "sub_checks":  {},
            "account_id":  "UNKNOWN",
            "timestamp":   timestamp,
            "raw":         {},
        }

    # ── Evaluate each sub-check ──────────────────────────────────────
    sub_checks  = {}
    failures    = []

    for field, req in POLICY_REQUIREMENTS.items():
        actual    = policy.get(field, None)
        threshold = req["threshold"]
        operator  = req["operator"]
        label     = req["label"]

        if actual is None:
            # Field absent from policy — treat as not meeting requirement
            sub_result = "FAIL"
            failures.append(f"{label} (not set)")
        elif operator == ">=":
            sub_result = "PASS" if actual >= threshold else "FAIL"
            if sub_result == "FAIL":
                failures.append(f"{label} (actual: {actual})")
        elif operator == "<=":
            sub_result = "PASS" if actual <= threshold else "FAIL"
            if sub_result == "FAIL":
                failures.append(f"{label} (actual: {actual})")
        elif operator == "==":
            sub_result = "PASS" if actual == threshold else "FAIL"
            if sub_result == "FAIL":
                failures.append(f"{label} (actual: {actual})")
        else:
            sub_result = "WARN"

        sub_checks[field] = {
            "result":    sub_result,
            "actual":    actual,
            "threshold": f"{operator} {threshold}",
            "cis":       req["cis"],
            "label":     label,
        }

    # ── Overall result ───────────────────────────────────────────────
    if not failures:
        finding     = ("IAM password policy meets all 7 CIS sub-checks. "
                       "Minimum length, complexity, expiry, and reuse prevention "
                       "are all correctly configured.")
        remediation = "None required."
        result      = "PASS"
        risk_rating = "N/A"
    else:
        n = len(failures)
        s = "s" if n > 1 else ""
        finding = (
            f"{n} of 7 CIS password policy sub-check{s} failing: "
            + "; ".join(failures) + ". "
            "IAM users can authenticate with passwords that do not meet "
            "regulatory complexity requirements."
        )
        remediation = (
            "Update the IAM account password policy via Console → IAM → "
            "Account settings → Edit password policy. Correct each failing "
            "sub-check to the CIS threshold listed above."
        )
        result      = "FAIL"
        risk_rating = "HIGH"

    return {
        "result":      result,
        "risk_rating": risk_rating,
        "finding":     finding,
        "remediation": remediation,
        "sub_checks":  sub_checks,
        "account_id":  account_id,
        "timestamp":   timestamp,
        "raw":         policy,
    }


# ── EVIDENCE ──────────────────────────────────────────────────────────
def build_evidence(result: dict) -> dict:
    """Assemble full audit evidence package — workpaper artefact."""
    return {
        "check_id":       CHECK_ID,
        "check_name":     CHECK_NAME,
        "cis_reference":  CIS_REF,
        "regulation_map": REGULATION,
        "account_id":     result["account_id"],
        "timestamp":      result["timestamp"],
        "result":         result["result"],
        "risk_rating":    result["risk_rating"],
        "finding":        result["finding"],
        "remediation":    result["remediation"],
        "sub_checks":     result["sub_checks"],
        "raw":            result["raw"],
    }


# ── REPORT ────────────────────────────────────────────────────────────
def print_terminal_report(evidence: dict):
    """Human-readable terminal output with per-sub-check detail table."""
    res    = evidence["result"]
    colour = GREEN if res == "PASS" else (RED if res == "FAIL" else YELLOW)
    icon   = "✓"   if res == "PASS" else ("✗" if res == "FAIL" else "⚠")

    def wrap(text, width=64):
        words = text.split()
        line  = "  "
        for w in words:
            if len(line) + len(w) + 1 > width:
                print(line)
                line = "  " + w + " "
            else:
                line += w + " "
        if line.strip():
            print(line)

    print(f"\n{DIM}{'─' * 68}{RESET}")
    print(f"{BOLD}{CYAN}  Control Testing Automation Theatre — rtapulse.com{RESET}")
    print(f"{DIM}{'─' * 68}{RESET}")
    print(f"  {BOLD}Check      {RESET}  {evidence['check_id']} — {evidence['check_name']}")
    print(f"  {BOLD}CIS Ref    {RESET}  {evidence['cis_reference']}")
    print(f"  {BOLD}Regs       {RESET}  {DIM}{evidence['regulation_map']}{RESET}")
    print(f"  {BOLD}Account    {RESET}  {evidence['account_id']}")
    print(f"  {BOLD}Timestamp  {RESET}  {evidence['timestamp']}")
    print(f"{DIM}{'─' * 68}{RESET}")
    print(f"\n  {colour}{BOLD}{icon}  RESULT: {res}{RESET}")

    if res in ("FAIL", "WARN"):
        print(f"\n  {BOLD}Risk Rating  {RESET}  {colour}{BOLD}{evidence['risk_rating']}{RESET}")

    # Sub-check table
    if evidence.get("sub_checks"):
        print(f"\n  {BOLD}Sub-check detail{RESET}")
        print(f"  {DIM}{'─' * 62}{RESET}")
        print(f"  {DIM}{'CIS':<6}  {'Check':<38}  {'Actual':<10}  {'Result'}{RESET}")
        print(f"  {DIM}{'─' * 62}{RESET}")
        for field, sc in evidence["sub_checks"].items():
            r_col  = GREEN if sc["result"] == "PASS" else (RED if sc["result"] == "FAIL" else YELLOW)
            r_icon = "✓" if sc["result"] == "PASS" else "✗"
            actual = str(sc["actual"]) if sc["actual"] is not None else "NOT SET"
            label  = sc["label"][:38]
            cis    = sc.get("cis", "")
            print(f"  {DIM}{cis:<6}{RESET}  {label:<38}  {actual:<10}  {r_col}{r_icon} {sc['result']}{RESET}")
        print(f"  {DIM}{'─' * 62}{RESET}")

    print(f"\n  {BOLD}Finding{RESET}")
    wrap(evidence["finding"])

    if evidence["remediation"] and evidence["remediation"] != "None required.":
        print(f"\n  {BOLD}Remediation{RESET}")
        wrap(evidence["remediation"])

    print(f"\n  {DIM}Raw policy: {json.dumps(evidence['raw'])}{RESET}")
    print(f"{DIM}{'─' * 68}{RESET}\n")


def save_json_report(evidence: dict, filename: str = None):
    """Save JSON evidence to file."""
    if not filename:
        ts       = evidence["timestamp"].replace(":", "-").replace("Z", "")
        filename = f"{evidence['check_id'].lower()}_{ts}.json"
    with open(filename, "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"  {DIM}JSON report saved → {filename}{RESET}\n")
    return filename


# ── MAIN ──────────────────────────────────────────────────────────────
def main():
    """
    Entry point. Usage:
      python3 aws_03_iam_password_policy.py
      python3 aws_03_iam_password_policy.py --profile my-audit-role
      python3 aws_03_iam_password_policy.py --profile my-audit-role --save
      python3 aws_03_iam_password_policy.py --json-only
    """
    import argparse
    parser = argparse.ArgumentParser(
        description="AWS-03: IAM Account Password Policy — CIS AWS Foundations 1.8–1.11"
    )
    parser.add_argument("--profile",   default=None,        help="AWS named profile")
    parser.add_argument("--region",    default="us-east-1", help="AWS region (default: us-east-1)")
    parser.add_argument("--save",      action="store_true",  help="Save JSON report to file")
    parser.add_argument("--json-only", action="store_true",  help="JSON output only — for pipeline use")
    args = parser.parse_args()

    iam, sts = connect(profile_name=args.profile, region=args.region)
    if iam is None:
        print(f"{RED}ERROR: Could not establish AWS session.{RESET}", file=sys.stderr)
        sys.exit(1)

    result   = check(iam, sts)
    evidence = build_evidence(result)

    if args.json_only:
        print(json.dumps(evidence, indent=2))
    else:
        print_terminal_report(evidence)
        print(json.dumps(evidence, indent=2))

    if args.save:
        save_json_report(evidence)

    # Exit codes: 0 = PASS, 1 = FAIL, 2 = WARN
    sys.exit({"PASS": 0, "FAIL": 1, "WARN": 2}.get(evidence["result"], 2))


if __name__ == "__main__":
    main()
