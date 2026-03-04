#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AWS-01 — Root Account MFA Status
  Control Testing Automation Theatre — rtapulse.com/labs/control-testing/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  CIS Reference : CIS AWS Foundations Benchmark v2.0 — Control 1.4
  Regulation map: NIST CSF PR.AC-7 | SOX ITGC AC-01 | PCI DSS 8.5
                  ISO 27001 A.9.4  | FFIEC CAT Baseline | DORA Art.9

  What it checks: Whether MFA is enabled on the AWS root account.
                  AccountMFAEnabled = 1 → PASS
                  AccountMFAEnabled = 0 → FAIL (CRITICAL)

  Prerequisites : pip install boto3
                  AWS credentials with iam:GetAccountSummary permission
                  Recommended: read-only IAM role (no write access needed)

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
CHECK_ID      = "AWS-01"
CHECK_NAME    = "Root Account MFA Status"
CIS_REF       = "CIS AWS Foundations Benchmark v2.0 — Control 1.4"
REGULATION    = "NIST CSF PR.AC-7 | SOX ITGC AC-01 | PCI DSS 8.5 | ISO 27001 A.9.4 | FFIEC CAT | DORA Art.9"

# ── Colour codes for terminal output ─────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
DIM    = "\033[2m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

# ── CONNECT ──────────────────────────────────────────────────────────
def connect(profile_name: str = None, region: str = "us-east-1"):
    """
    Establish AWS session and return IAM + STS clients.
    Credentials are resolved in this order:
      1. Named profile (if profile_name provided)
      2. Environment variables (AWS_ACCESS_KEY_ID etc.)
      3. Instance profile / ECS task role
      4. ~/.aws/credentials default profile
    """
    try:
        session = boto3.Session(profile_name=profile_name, region_name=region)
        iam = session.client("iam")
        sts = session.client("sts")
        return iam, sts
    except Exception as e:
        return None, None


# ── CHECK ─────────────────────────────────────────────────────────────
def check(iam_client, sts_client) -> dict:
    """
    Run the control check. Returns a result dict with:
      result       : PASS | FAIL | WARN
      risk_rating  : CRITICAL | HIGH | MEDIUM | N/A
      finding      : human-readable finding string
      remediation  : one-line remediation instruction
      raw          : raw API response values for evidence trail
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Resolve account ID
    account_id = "UNKNOWN"
    try:
        identity = sts_client.get_caller_identity()
        account_id = identity.get("Account", "UNKNOWN")
    except Exception:
        pass  # Non-critical — continue with check

    # Run the control check
    try:
        summary = iam_client.get_account_summary()
        summary_map = summary.get("SummaryMap", {})
        mfa_enabled = summary_map.get("AccountMFAEnabled", None)

        if mfa_enabled is None:
            # Field absent — unexpected API response
            return {
                "result":      "WARN",
                "risk_rating": "UNKNOWN",
                "finding":     "AccountMFAEnabled field was absent from IAM GetAccountSummary response. "
                               "API response may be malformed or permission is partially granted.",
                "remediation": "Verify iam:GetAccountSummary permission and re-run.",
                "account_id":  account_id,
                "timestamp":   timestamp,
                "raw":         summary_map,
            }

        if mfa_enabled == 1:
            return {
                "result":      "PASS",
                "risk_rating": "N/A",
                "finding":     "Root account MFA is enabled.",
                "remediation": "None required.",
                "account_id":  account_id,
                "timestamp":   timestamp,
                "raw":         {"AccountMFAEnabled": mfa_enabled},
            }
        else:
            return {
                "result":      "FAIL",
                "risk_rating": "CRITICAL",
                "finding":     "Root account MFA is NOT enabled. "
                               "The root account is accessible with a password alone. "
                               "Full account takeover risk — no IAM policy can restrict root.",
                "remediation": "Enable virtual or hardware MFA on the root account immediately "
                               "via AWS Console → Account menu → Security credentials → Assign MFA device.",
                "account_id":  account_id,
                "timestamp":   timestamp,
                "raw":         {"AccountMFAEnabled": mfa_enabled},
            }

    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg  = e.response["Error"]["Message"]
        return {
            "result":      "WARN",
            "risk_rating": "UNKNOWN",
            "finding":     f"AWS API error ({code}): {msg}. Check could not complete.",
            "remediation": "Ensure the executing IAM identity has iam:GetAccountSummary permission.",
            "account_id":  account_id,
            "timestamp":   timestamp,
            "raw":         {"error_code": code, "error_message": msg},
        }

    except NoCredentialsError:
        return {
            "result":      "WARN",
            "risk_rating": "UNKNOWN",
            "finding":     "No AWS credentials found. Configure via environment variables, "
                           "named profile, or instance role.",
            "remediation": "Run: aws configure  or set AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY",
            "account_id":  "UNKNOWN",
            "timestamp":   timestamp,
            "raw":         {},
        }


# ── EVIDENCE ──────────────────────────────────────────────────────────
def build_evidence(result: dict) -> dict:
    """
    Assemble full audit evidence package from the check result.
    This is what goes into the workpaper.
    """
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
        "raw":            result["raw"],
    }


# ── REPORT ────────────────────────────────────────────────────────────
def print_terminal_report(evidence: dict):
    """
    Human-readable terminal output. Structured for screen review
    and copy-paste into ticketing systems or email findings.
    """
    result = evidence["result"]

    # Colour-code the result
    if result == "PASS":
        result_colour = GREEN
        result_icon   = "✓"
    elif result == "FAIL":
        result_colour = RED
        result_icon   = "✗"
    else:
        result_colour = YELLOW
        result_icon   = "⚠"

    print(f"\n{DIM}{'─' * 68}{RESET}")
    print(f"{BOLD}{CYAN}  Control Testing Automation Theatre — rtapulse.com{RESET}")
    print(f"{DIM}{'─' * 68}{RESET}")
    print(f"  {BOLD}Check      {RESET}  {evidence['check_id']} — {evidence['check_name']}")
    print(f"  {BOLD}CIS Ref    {RESET}  {evidence['cis_reference']}")
    print(f"  {BOLD}Regs       {RESET}  {DIM}{evidence['regulation_map']}{RESET}")
    print(f"  {BOLD}Account    {RESET}  {evidence['account_id']}")
    print(f"  {BOLD}Timestamp  {RESET}  {evidence['timestamp']}")
    print(f"{DIM}{'─' * 68}{RESET}")
    print(f"\n  {result_colour}{BOLD}{result_icon}  RESULT: {result}{RESET}")

    if result in ("FAIL", "WARN"):
        print(f"\n  {BOLD}Risk Rating  {RESET}  {result_colour}{BOLD}{evidence['risk_rating']}{RESET}")

    print(f"\n  {BOLD}Finding{RESET}")
    # Word-wrap the finding at 60 chars for clean terminal display
    words   = evidence["finding"].split()
    line    = "  "
    for word in words:
        if len(line) + len(word) + 1 > 64:
            print(line)
            line = "  " + word + " "
        else:
            line += word + " "
    if line.strip():
        print(line)

    if evidence["remediation"] and evidence["remediation"] != "None required.":
        print(f"\n  {BOLD}Remediation{RESET}")
        words = evidence["remediation"].split()
        line  = "  "
        for word in words:
            if len(line) + len(word) + 1 > 64:
                print(line)
                line = "  " + word + " "
            else:
                line += word + " "
        if line.strip():
            print(line)

    print(f"\n  {DIM}Raw: {json.dumps(evidence['raw'])}{RESET}")
    print(f"{DIM}{'─' * 68}{RESET}\n")


def save_json_report(evidence: dict, filename: str = None):
    """Save JSON evidence to file. Filename defaults to check_id + timestamp."""
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
      python3 aws_01_root_mfa.py
      python3 aws_01_root_mfa.py --profile my-audit-role
      python3 aws_01_root_mfa.py --profile my-audit-role --save
    """
    import argparse
    parser = argparse.ArgumentParser(
        description="AWS-01: Root Account MFA Status — CIS AWS Foundations 1.4"
    )
    parser.add_argument(
        "--profile", default=None,
        help="AWS named profile to use (default: environment/instance role)"
    )
    parser.add_argument(
        "--region", default="us-east-1",
        help="AWS region for STS endpoint (default: us-east-1)"
    )
    parser.add_argument(
        "--save", action="store_true",
        help="Save JSON report to file"
    )
    parser.add_argument(
        "--json-only", action="store_true",
        help="Output JSON only (suppress terminal report — for pipeline use)"
    )
    args = parser.parse_args()

    # Connect
    iam, sts = connect(profile_name=args.profile, region=args.region)
    if iam is None:
        print(f"{RED}ERROR: Could not establish AWS session. Check credentials.{RESET}", file=sys.stderr)
        sys.exit(1)

    # Check
    result   = check(iam, sts)
    evidence = build_evidence(result)

    # Report
    if args.json_only:
        print(json.dumps(evidence, indent=2))
    else:
        print_terminal_report(evidence)
        print(json.dumps(evidence, indent=2))

    # Save
    if args.save:
        save_json_report(evidence)

    # Exit codes: 0 = PASS, 1 = FAIL, 2 = WARN
    sys.exit({"PASS": 0, "FAIL": 1, "WARN": 2}.get(evidence["result"], 2))


if __name__ == "__main__":
    main()
