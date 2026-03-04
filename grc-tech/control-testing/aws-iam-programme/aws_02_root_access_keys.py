#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AWS-02 — Root Account Access Keys
  Control Testing Automation Theatre — rtapulse.com/labs/control-testing/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  CIS Reference : CIS AWS Foundations Benchmark v2.0 — Control 1.4 / 1.12
  Regulation map: NIST CSF PR.AC-4 | SOX ITGC AC-02 | PCI DSS 8.2.1
                  ISO 27001 A.9.2.3 | FFIEC CAT Baseline | DORA Art.9

  What it checks: Whether any access keys exist on the AWS root account.
                  AccountAccessKeysPresent = 0 → PASS  (no keys — correct)
                  AccountAccessKeysPresent > 0 → FAIL (CRITICAL)

  Why it matters: Root access keys bypass all IAM boundary controls and
                  cannot be restricted by SCPs or permission policies.
                  AWS explicitly states root access keys should never exist.
                  Any key found — active or inactive — is a critical finding.

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
CHECK_ID   = "AWS-02"
CHECK_NAME = "Root Account Access Keys"
CIS_REF    = "CIS AWS Foundations Benchmark v2.0 — Controls 1.4 / 1.12"
REGULATION = "NIST CSF PR.AC-4 | SOX ITGC AC-02 | PCI DSS 8.2.1 | ISO 27001 A.9.2.3 | FFIEC CAT | DORA Art.9"

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
      2. Environment variables (AWS_ACCESS_KEY_ID etc.)
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
    Run the control check.

    AccountAccessKeysPresent from GetAccountSummary counts the number
    of access keys associated with the root account — both active and
    inactive. The correct value is 0. Any non-zero value is CRITICAL.

    Note: this field counts root-level keys only. IAM user keys are
    a separate check (AWS-04 inactive users covers stale user keys).
    """
    timestamp  = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    account_id = "UNKNOWN"

    try:
        account_id = sts_client.get_caller_identity().get("Account", "UNKNOWN")
    except Exception:
        pass

    try:
        summary     = iam_client.get_account_summary()
        summary_map = summary.get("SummaryMap", {})
        keys_count  = summary_map.get("AccountAccessKeysPresent", None)

        if keys_count is None:
            return {
                "result":      "WARN",
                "risk_rating": "UNKNOWN",
                "finding":     "AccountAccessKeysPresent field absent from GetAccountSummary response. "
                               "Permission may be partially granted or API response malformed.",
                "remediation": "Verify iam:GetAccountSummary permission and re-run.",
                "account_id":  account_id,
                "timestamp":   timestamp,
                "raw":         summary_map,
            }

        if keys_count == 0:
            return {
                "result":      "PASS",
                "risk_rating": "N/A",
                "finding":     "No access keys exist on the root account. Correct configuration.",
                "remediation": "None required.",
                "account_id":  account_id,
                "timestamp":   timestamp,
                "raw":         {"AccountAccessKeysPresent": keys_count},
            }
        else:
            key_word = "key" if keys_count == 1 else "keys"
            return {
                "result":      "FAIL",
                "risk_rating": "CRITICAL",
                "finding":     (
                    f"{keys_count} root account access {key_word} detected "
                    f"(active or inactive). Root access keys bypass all IAM "
                    f"policies, SCPs, and permission boundaries. AWS states "
                    f"root access keys should never exist. Delete immediately."
                ),
                "remediation": (
                    "Sign in as root → Account menu → Security credentials → "
                    "Access keys → Delete all keys. Do not deactivate — delete. "
                    "Use an IAM role with least-privilege for any automation "
                    "that previously used root keys."
                ),
                "account_id":  account_id,
                "timestamp":   timestamp,
                "raw":         {"AccountAccessKeysPresent": keys_count},
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
    """Assemble full audit evidence package — this is the workpaper artefact."""
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
    """Human-readable terminal output — structured for screen review and ticketing."""
    result = evidence["result"]
    colour = GREEN if result == "PASS" else (RED if result == "FAIL" else YELLOW)
    icon   = "✓"   if result == "PASS" else ("✗" if result == "FAIL" else "⚠")

    print(f"\n{DIM}{'─' * 68}{RESET}")
    print(f"{BOLD}{CYAN}  Control Testing Automation Theatre — rtapulse.com{RESET}")
    print(f"{DIM}{'─' * 68}{RESET}")
    print(f"  {BOLD}Check      {RESET}  {evidence['check_id']} — {evidence['check_name']}")
    print(f"  {BOLD}CIS Ref    {RESET}  {evidence['cis_reference']}")
    print(f"  {BOLD}Regs       {RESET}  {DIM}{evidence['regulation_map']}{RESET}")
    print(f"  {BOLD}Account    {RESET}  {evidence['account_id']}")
    print(f"  {BOLD}Timestamp  {RESET}  {evidence['timestamp']}")
    print(f"{DIM}{'─' * 68}{RESET}")
    print(f"\n  {colour}{BOLD}{icon}  RESULT: {result}{RESET}")

    if result in ("FAIL", "WARN"):
        print(f"\n  {BOLD}Risk Rating  {RESET}  {colour}{BOLD}{evidence['risk_rating']}{RESET}")

    def wrap_print(text):
        words = text.split()
        line  = "  "
        for w in words:
            if len(line) + len(w) + 1 > 64:
                print(line)
                line = "  " + w + " "
            else:
                line += w + " "
        if line.strip():
            print(line)

    print(f"\n  {BOLD}Finding{RESET}")
    wrap_print(evidence["finding"])

    if evidence["remediation"] and evidence["remediation"] != "None required.":
        print(f"\n  {BOLD}Remediation{RESET}")
        wrap_print(evidence["remediation"])

    print(f"\n  {DIM}Raw: {json.dumps(evidence['raw'])}{RESET}")
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
      python3 aws_02_root_access_keys.py
      python3 aws_02_root_access_keys.py --profile my-audit-role
      python3 aws_02_root_access_keys.py --profile my-audit-role --save
      python3 aws_02_root_access_keys.py --json-only
    """
    import argparse
    parser = argparse.ArgumentParser(
        description="AWS-02: Root Account Access Keys — CIS AWS Foundations 1.12"
    )
    parser.add_argument("--profile",   default=None,  help="AWS named profile")
    parser.add_argument("--region",    default="us-east-1", help="AWS region (default: us-east-1)")
    parser.add_argument("--save",      action="store_true", help="Save JSON report to file")
    parser.add_argument("--json-only", action="store_true", help="JSON output only — for pipeline use")
    args = parser.parse_args()

    iam, sts = connect(profile_name=args.profile, region=args.region)
    if iam is None:
        print(f"{RED}ERROR: Could not establish AWS session. Check credentials.{RESET}", file=sys.stderr)
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
