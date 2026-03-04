#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AWS-04 — Inactive IAM Users (No activity > 90 days)
  Control Testing Automation Theatre — rtapulse.com/labs/control-testing/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  CIS Reference : CIS AWS Foundations Benchmark v2.0 — Control 1.15
  Regulation map: NIST CSF PR.AC-1 | SOX ITGC AC-04 | PCI DSS 8.8
                  ISO 27001 A.9.2.6 | FFIEC CAT Baseline | DORA Art.9

  What it checks: All IAM users with console or programmatic access
                  whose last activity (console sign-in OR access key
                  usage) was more than 90 days ago, or who have never
                  logged in at all.

                  PASS   → zero inactive users found
                  FAIL   → one or more inactive users (HIGH)

  Inactive definition:
    - PasswordLastUsed > 90 days ago  (console access)
    - AccessKey LastUsedDate > 90 days ago  (programmatic access)
    - Never used (PasswordLastUsed = None AND no key activity)

  Note          : Users with no console password AND no access keys
                  (e.g. role-only identities) are excluded — they
                  present no direct login surface.

  Prerequisites : pip install boto3
                  IAM permissions:
                    iam:ListUsers
                    iam:GetUser
                    iam:ListAccessKeys
                    iam:GetAccessKeyLastUsed
                    iam:GenerateCredentialReport  (optional — improves accuracy)
                    iam:GetCredentialReport       (optional)

  Output        : JSON report + human-readable terminal
                  Inactive user list included in evidence for workpaper

  Runtime       : ~5–30 seconds depending on user count

  Author        : rtapulse.com
  Published     : 2026-03-02
  Licence       : MIT — use freely, attribute appreciated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import boto3
import json
import sys
from datetime import datetime, timezone, timedelta
from botocore.exceptions import ClientError, NoCredentialsError

# ── Configuration ────────────────────────────────────────────────────
CHECK_ID          = "AWS-04"
CHECK_NAME        = "Inactive IAM Users (>90 days)"
CIS_REF           = "CIS AWS Foundations Benchmark v2.0 — Control 1.15"
REGULATION        = "NIST CSF PR.AC-1 | SOX ITGC AC-04 | PCI DSS 8.8 | ISO 27001 A.9.2.6 | FFIEC CAT | DORA Art.9"
INACTIVITY_DAYS   = 90

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
    Enumerate all IAM users and classify each as active or inactive.

    Activity is determined by the most recent of:
      - PasswordLastUsed  (console login)
      - Most recent AccessKey LastUsedDate across all keys for the user

    A user is inactive if their most recent activity is older than
    INACTIVITY_DAYS, or if they have never been used at all.

    Users with no login mechanism (no password, no access keys) are
    skipped — they cannot log in and are not an access risk.
    """
    timestamp  = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    now        = datetime.now(timezone.utc)
    cutoff     = now - timedelta(days=INACTIVITY_DAYS)
    account_id = "UNKNOWN"

    try:
        account_id = sts_client.get_caller_identity().get("Account", "UNKNOWN")
    except Exception:
        pass

    try:
        # Paginate all IAM users
        paginator  = iam_client.get_paginator("list_users")
        all_users  = []
        for page in paginator.paginate():
            all_users.extend(page.get("Users", []))

        if not all_users:
            return {
                "result":         "PASS",
                "risk_rating":    "N/A",
                "finding":        "No IAM users exist in this account. "
                                  "Consistent with an SSO / Identity Centre-only deployment.",
                "remediation":    "None required.",
                "inactive_users": [],
                "total_users":    0,
                "account_id":     account_id,
                "timestamp":      timestamp,
                "raw":            {"total_users": 0, "inactive_count": 0},
            }

        inactive_users = []

        for user in all_users:
            username      = user["UserName"]
            created       = user.get("CreateDate")
            pwd_last_used = user.get("PasswordLastUsed")  # None if never used or no password

            # Collect all access key last-used dates for this user
            key_last_used_dates = []
            try:
                keys_resp = iam_client.list_access_keys(UserName=username)
                for key in keys_resp.get("AccessKeyMetadata", []):
                    kid = key["AccessKeyId"]
                    try:
                        lu = iam_client.get_access_key_last_used(AccessKeyId=kid)
                        last_used = lu.get("AccessKeyLastUsed", {}).get("LastUsedDate")
                        if last_used:
                            key_last_used_dates.append(last_used)
                    except ClientError:
                        pass
            except ClientError:
                pass

            # Determine most recent activity across console + keys
            activity_dates = []
            if pwd_last_used:
                activity_dates.append(pwd_last_used)
            activity_dates.extend(key_last_used_dates)

            # Skip users with no login surface at all
            has_password  = pwd_last_used is not None
            has_keys      = len(key_last_used_dates) > 0
            # Check if user has a login profile (password enabled)
            try:
                iam_client.get_login_profile(UserName=username)
                has_password_enabled = True
            except ClientError as e:
                has_password_enabled = False if e.response["Error"]["Code"] == "NoSuchEntity" else True

            if not has_password_enabled and not key_last_used_dates:
                # No usable login mechanism — skip
                continue

            if not activity_dates:
                # Has a login mechanism but has never been used
                days_inactive = (now - created).days if created else None
                inactive_users.append({
                    "username":       username,
                    "last_activity":  "NEVER",
                    "days_inactive":  days_inactive,
                    "has_password":   has_password_enabled,
                    "has_keys":       has_keys,
                    "status":         "NEVER_USED",
                })
            else:
                most_recent = max(activity_dates)
                if most_recent < cutoff:
                    days_inactive = (now - most_recent).days
                    inactive_users.append({
                        "username":       username,
                        "last_activity":  most_recent.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "days_inactive":  days_inactive,
                        "has_password":   has_password_enabled,
                        "has_keys":       has_keys,
                        "status":         "INACTIVE",
                    })

        # Sort by most inactive first
        inactive_users.sort(key=lambda u: u["days_inactive"] or 9999, reverse=True)

        total     = len(all_users)
        n_inactive = len(inactive_users)

        if n_inactive == 0:
            return {
                "result":         "PASS",
                "risk_rating":    "N/A",
                "finding":        f"All {total} IAM users with active login mechanisms have been "
                                  f"active within the last {INACTIVITY_DAYS} days. No inactive accounts found.",
                "remediation":    "None required.",
                "inactive_users": [],
                "total_users":    total,
                "account_id":     account_id,
                "timestamp":      timestamp,
                "raw":            {"total_users": total, "inactive_count": 0},
            }
        else:
            s = "s" if n_inactive > 1 else ""
            usernames = ", ".join(u["username"] for u in inactive_users[:5])
            more      = f" (and {n_inactive - 5} more)" if n_inactive > 5 else ""
            return {
                "result":         "FAIL",
                "risk_rating":    "HIGH",
                "finding":        (
                    f"{n_inactive} IAM user{s} inactive for more than {INACTIVITY_DAYS} days "
                    f"or never used: {usernames}{more}. "
                    f"Stale accounts retain their original permissions — "
                    f"they are valid attack targets for credential stuffing and "
                    f"privilege escalation. Each represents an unmonitored access path."
                ),
                "remediation":    (
                    f"Disable or delete all {n_inactive} inactive user{s}. "
                    "Preferred approach: disable console access and deactivate access keys first, "
                    "confirm no service dependency for 30 days, then delete. "
                    "Document disposition in access review evidence."
                ),
                "inactive_users": inactive_users,
                "total_users":    total,
                "account_id":     account_id,
                "timestamp":      timestamp,
                "raw":            {"total_users": total, "inactive_count": n_inactive},
            }

    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg  = e.response["Error"]["Message"]
        return {
            "result":         "WARN",
            "risk_rating":    "UNKNOWN",
            "finding":        f"AWS API error ({code}): {msg}. Check could not complete.",
            "remediation":    "Ensure iam:ListUsers and iam:GetAccessKeyLastUsed permissions are granted.",
            "inactive_users": [],
            "total_users":    0,
            "account_id":     account_id,
            "timestamp":      timestamp,
            "raw":            {"error_code": code, "error_message": msg},
        }

    except NoCredentialsError:
        return {
            "result":         "WARN",
            "risk_rating":    "UNKNOWN",
            "finding":        "No AWS credentials found.",
            "remediation":    "Run: aws configure  or set AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY",
            "inactive_users": [],
            "total_users":    0,
            "account_id":     "UNKNOWN",
            "timestamp":      timestamp,
            "raw":            {},
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
        "inactive_users": result["inactive_users"],
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
    print(f"  {BOLD}Scope      {RESET}  {evidence['total_users']} total IAM users evaluated")
    print(f"{DIM}{'─' * 68}{RESET}")
    print(f"\n  {colour}{BOLD}{icon}  RESULT: {res}{RESET}")

    if res in ("FAIL", "WARN"):
        print(f"\n  {BOLD}Risk Rating  {RESET}  {colour}{BOLD}{evidence['risk_rating']}{RESET}")

    # Inactive user table
    if evidence.get("inactive_users"):
        print(f"\n  {BOLD}Inactive user detail{RESET}")
        print(f"  {DIM}{'─' * 62}{RESET}")
        print(f"  {DIM}{'Username':<28}  {'Last activity':<22}  {'Days':<6}  Status{RESET}")
        print(f"  {DIM}{'─' * 62}{RESET}")
        for u in evidence["inactive_users"]:
            days_str = str(u["days_inactive"]) if u["days_inactive"] is not None else "?"
            print(
                f"  {RED}{u['username']:<28}{RESET}  "
                f"{DIM}{u['last_activity']:<22}{RESET}  "
                f"{days_str:<6}  "
                f"{RED}{u['status']}{RESET}"
            )
        print(f"  {DIM}{'─' * 62}{RESET}")

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
        description="AWS-04: Inactive IAM Users — CIS AWS Foundations 1.15"
    )
    parser.add_argument("--profile",        default=None,        help="AWS named profile")
    parser.add_argument("--region",         default="us-east-1", help="AWS region")
    parser.add_argument("--days",           default=90, type=int, help="Inactivity threshold in days (default: 90)")
    parser.add_argument("--save",           action="store_true",  help="Save JSON report to file")
    parser.add_argument("--json-only",      action="store_true",  help="JSON output only")
    args = parser.parse_args()

    global INACTIVITY_DAYS
    INACTIVITY_DAYS = args.days

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
