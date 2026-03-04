#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AWS-05 — MFA Enforcement: All Console Users
  Control Testing Automation Theatre — rtapulse.com/labs/control-testing/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  CIS Reference : CIS AWS Foundations Benchmark v2.0 — Control 1.10
  Regulation map: NIST CSF PR.AC-7 | SOX ITGC AC-05 | PCI DSS 8.5
                  ISO 27001 A.9.4.2 | FFIEC CAT Baseline | DORA Art.9

  What it checks: Every IAM user with a console password (login profile)
                  must have an MFA device assigned.

                  For each console-enabled user:
                    MFA devices > 0  → user PASS
                    MFA devices = 0  → user FAIL

                  Overall result:
                    All users pass  → PASS
                    Any user fails  → FAIL (HIGH)
                    No console users exist → PASS (noted)

  Why it matters: AWS-01 covers root MFA. This check covers every other
                  human operator. A single console user without MFA is an
                  open door — password-only accounts are trivially
                  compromised via phishing, credential stuffing, or leaked
                  credentials in version control.

  Note          : Users without a login profile (programmatic/API-only)
                  are excluded — they have no console access to protect
                  with MFA. Service accounts with only access keys fall
                  outside this check's scope.

  Prerequisites : pip install boto3
                  IAM permissions:
                    iam:ListUsers
                    iam:GetLoginProfile
                    iam:ListMFADevices

  Output        : JSON report + human-readable terminal
                  Per-user MFA status table in evidence output

  Runtime       : ~5–20 seconds depending on user count

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
CHECK_ID   = "AWS-05"
CHECK_NAME = "MFA Enforcement — All Console Users"
CIS_REF    = "CIS AWS Foundations Benchmark v2.0 — Control 1.10"
REGULATION = "NIST CSF PR.AC-7 | SOX ITGC AC-05 | PCI DSS 8.5 | ISO 27001 A.9.4.2 | FFIEC CAT | DORA Art.9"

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
    try:
        session = boto3.Session(profile_name=profile_name, region_name=region)
        return session.client("iam"), session.client("sts")
    except Exception:
        return None, None


# ── CHECK ─────────────────────────────────────────────────────────────
def check(iam_client, sts_client) -> dict:
    """
    For every IAM user:
      1. Check whether a login profile exists (console password enabled)
      2. If yes, check whether at least one MFA device is assigned
      3. Classify as PASS or FAIL per user
      4. Roll up to overall PASS/FAIL

    Users without a login profile are listed as SKIPPED — they are
    programmatic-only and outside this check's scope.
    """
    timestamp  = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    account_id = "UNKNOWN"

    try:
        account_id = sts_client.get_caller_identity().get("Account", "UNKNOWN")
    except Exception:
        pass

    try:
        paginator = iam_client.get_paginator("list_users")
        all_users = []
        for page in paginator.paginate():
            all_users.extend(page.get("Users", []))

        if not all_users:
            return {
                "result":        "PASS",
                "risk_rating":   "N/A",
                "finding":       "No IAM users exist in this account.",
                "remediation":   "None required.",
                "user_results":  [],
                "console_users": 0,
                "failing_users": 0,
                "total_users":   0,
                "account_id":    account_id,
                "timestamp":     timestamp,
                "raw":           {"total_users": 0},
            }

        user_results   = []
        failing_users  = []
        console_count  = 0

        for user in all_users:
            username = user["UserName"]

            # Step 1: Does user have a console login profile?
            has_console = False
            try:
                iam_client.get_login_profile(UserName=username)
                has_console = True
                console_count += 1
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchEntity":
                    has_console = False
                # Other errors: treat conservatively as unknown
                else:
                    has_console = True
                    console_count += 1

            if not has_console:
                user_results.append({
                    "username":    username,
                    "has_console": False,
                    "mfa_count":   None,
                    "result":      "SKIPPED",
                    "note":        "No console password — API/programmatic only",
                })
                continue

            # Step 2: How many MFA devices does this user have?
            mfa_count = 0
            try:
                mfa_resp  = iam_client.list_mfa_devices(UserName=username)
                mfa_count = len(mfa_resp.get("MFADevices", []))
            except ClientError:
                pass

            u_result = "PASS" if mfa_count > 0 else "FAIL"
            if u_result == "FAIL":
                failing_users.append(username)

            user_results.append({
                "username":    username,
                "has_console": True,
                "mfa_count":   mfa_count,
                "result":      u_result,
                "note":        "MFA active" if mfa_count > 0 else "NO MFA — console exposed",
            })

        n_failing = len(failing_users)

        # Sort: failing first, then passing, skipped last
        order = {"FAIL": 0, "PASS": 1, "SKIPPED": 2}
        user_results.sort(key=lambda u: order.get(u["result"], 3))

        if n_failing == 0:
            return {
                "result":        "PASS",
                "risk_rating":   "N/A",
                "finding":       (
                    f"All {console_count} IAM users with console access have at least "
                    f"one MFA device assigned. Console access is protected across all users."
                ),
                "remediation":   "None required.",
                "user_results":  user_results,
                "console_users": console_count,
                "failing_users": 0,
                "total_users":   len(all_users),
                "account_id":    account_id,
                "timestamp":     timestamp,
                "raw":           {"total_users": len(all_users), "console_users": console_count, "failing_count": 0},
            }
        else:
            s        = "s" if n_failing > 1 else ""
            names    = ", ".join(failing_users[:5])
            more     = f" (and {n_failing - 5} more)" if n_failing > 5 else ""
            return {
                "result":        "FAIL",
                "risk_rating":   "HIGH",
                "finding":       (
                    f"{n_failing} of {console_count} console-enabled IAM user{s} "
                    f"have no MFA device assigned: {names}{more}. "
                    f"These accounts can be accessed with a password alone — "
                    f"a phished or leaked credential is sufficient for full console access."
                ),
                "remediation":   (
                    f"Assign MFA to all {n_failing} failing user{s} immediately. "
                    "Via console: IAM → Users → [username] → Security credentials → "
                    "Assign MFA device. Consider enforcing MFA via an IAM policy "
                    "condition (aws:MultiFactorAuthPresent: true) to deny console "
                    "actions until MFA is satisfied."
                ),
                "user_results":  user_results,
                "console_users": console_count,
                "failing_users": n_failing,
                "total_users":   len(all_users),
                "account_id":    account_id,
                "timestamp":     timestamp,
                "raw":           {"total_users": len(all_users), "console_users": console_count, "failing_count": n_failing},
            }

    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg  = e.response["Error"]["Message"]
        return {
            "result":        "WARN",
            "risk_rating":   "UNKNOWN",
            "finding":       f"AWS API error ({code}): {msg}. Check could not complete.",
            "remediation":   "Ensure iam:ListUsers, iam:GetLoginProfile, iam:ListMFADevices permissions are granted.",
            "user_results":  [],
            "console_users": 0,
            "failing_users": 0,
            "total_users":   0,
            "account_id":    account_id,
            "timestamp":     timestamp,
            "raw":           {"error_code": code, "error_message": msg},
        }

    except NoCredentialsError:
        return {
            "result":        "WARN",
            "risk_rating":   "UNKNOWN",
            "finding":       "No AWS credentials found.",
            "remediation":   "Run: aws configure  or set AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY",
            "user_results":  [],
            "console_users": 0,
            "failing_users": 0,
            "total_users":   0,
            "account_id":    "UNKNOWN",
            "timestamp":     timestamp,
            "raw":           {},
        }


# ── EVIDENCE ──────────────────────────────────────────────────────────
def build_evidence(result: dict) -> dict:
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
        "user_results":   result["user_results"],
        "console_users":  result["console_users"],
        "failing_users":  result["failing_users"],
        "total_users":    result["total_users"],
        "raw":            result["raw"],
    }


# ── REPORT ────────────────────────────────────────────────────────────
def print_terminal_report(evidence: dict):
    res    = evidence["result"]
    colour = GREEN if res == "PASS" else (RED if res == "FAIL" else YELLOW)
    icon   = "✓"   if res == "PASS" else ("✗" if res == "FAIL" else "⚠")

    def wrap(text, w=64):
        words = text.split(); line = "  "
        for wd in words:
            if len(line) + len(wd) + 1 > w: print(line); line = "  " + wd + " "
            else: line += wd + " "
        if line.strip(): print(line)

    print(f"\n{DIM}{'─' * 68}{RESET}")
    print(f"{BOLD}{CYAN}  Control Testing Automation Theatre — rtapulse.com{RESET}")
    print(f"{DIM}{'─' * 68}{RESET}")
    print(f"  {BOLD}Check      {RESET}  {evidence['check_id']} — {evidence['check_name']}")
    print(f"  {BOLD}CIS Ref    {RESET}  {evidence['cis_reference']}")
    print(f"  {BOLD}Regs       {RESET}  {DIM}{evidence['regulation_map']}{RESET}")
    print(f"  {BOLD}Account    {RESET}  {evidence['account_id']}")
    print(f"  {BOLD}Timestamp  {RESET}  {evidence['timestamp']}")
    print(f"  {BOLD}Scope      {RESET}  {evidence['total_users']} total users · "
          f"{evidence['console_users']} with console access · "
          f"{evidence['failing_users']} failing")
    print(f"{DIM}{'─' * 68}{RESET}")
    print(f"\n  {colour}{BOLD}{icon}  RESULT: {res}{RESET}")

    if res in ("FAIL", "WARN"):
        print(f"\n  {BOLD}Risk Rating  {RESET}  {colour}{BOLD}{evidence['risk_rating']}{RESET}")

    # Per-user table — only show console users (skip SKIPPED)
    console_rows = [u for u in evidence.get("user_results", []) if u["result"] != "SKIPPED"]
    if console_rows:
        print(f"\n  {BOLD}Console user MFA status{RESET}")
        print(f"  {DIM}{'─' * 60}{RESET}")
        print(f"  {DIM}{'Username':<30}  {'MFA devices':<12}  Result{RESET}")
        print(f"  {DIM}{'─' * 60}{RESET}")
        for u in console_rows:
            rc   = GREEN if u["result"] == "PASS" else RED
            ri   = "✓" if u["result"] == "PASS" else "✗"
            mfa  = str(u["mfa_count"]) if u["mfa_count"] is not None else "?"
            print(f"  {u['username']:<30}  {mfa:<12}  {rc}{ri} {u['result']}{RESET}")
        print(f"  {DIM}{'─' * 60}{RESET}")

    print(f"\n  {BOLD}Finding{RESET}")
    wrap(evidence["finding"])

    if evidence["remediation"] and evidence["remediation"] != "None required.":
        print(f"\n  {BOLD}Remediation{RESET}")
        wrap(evidence["remediation"])

    print(f"\n  {DIM}Raw: {json.dumps(evidence['raw'])}{RESET}")
    print(f"{DIM}{'─' * 68}{RESET}\n")


def save_json_report(evidence: dict, filename: str = None):
    if not filename:
        ts = evidence["timestamp"].replace(":", "-").replace("Z", "")
        filename = f"{evidence['check_id'].lower()}_{ts}.json"
    with open(filename, "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"  {DIM}JSON report saved → {filename}{RESET}\n")
    return filename


# ── MAIN ──────────────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="AWS-05: MFA Enforcement — All Console Users — CIS AWS 1.10"
    )
    parser.add_argument("--profile",   default=None,        help="AWS named profile")
    parser.add_argument("--region",    default="us-east-1", help="AWS region")
    parser.add_argument("--save",      action="store_true",  help="Save JSON report to file")
    parser.add_argument("--json-only", action="store_true",  help="JSON output only")
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

    sys.exit({"PASS": 0, "FAIL": 1, "WARN": 2}.get(evidence["result"], 2))


if __name__ == "__main__":
    main()
