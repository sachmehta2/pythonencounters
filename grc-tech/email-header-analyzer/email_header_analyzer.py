#!/usr/bin/env python3
"""email_header_analyzer.py

Quick triage helper for email headers. Reads a raw header text file and reports:
- SPF/DKIM signals (best-effort; prefers Authentication-Results when present)
- DMARC publication status (DNS TXT lookup for _dmarc.<domain>)
- TLS hints (heuristic)
- Basic From vs Return-Path mismatch check

No auto-install / no auto-upgrade. Use requirements + a virtual environment.
"""

import argparse
import re
from email.utils import parseaddr
from pathlib import Path

import dns.resolver
from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)


def _status_color(status: str) -> str:
    s = status.upper()
    if s in {"PASS", "OK"}:
        return Fore.GREEN + status + Style.RESET_ALL
    if s in {"WARN", "WARNING"}:
        return Fore.YELLOW + status + Style.RESET_ALL
    if s in {"FAIL", "ERROR"}:
        return Fore.RED + status + Style.RESET_ALL
    return status


def extract_domain_from_header(header_value: str) -> str | None:
    if not header_value:
        return None
    _, addr = parseaddr(header_value)
    if "@" not in addr:
        return None
    return addr.split("@", 1)[1].strip().lower()


def parse_auth_results(header_text: str) -> dict:
    """Best-effort parse for Authentication-Results: spf=, dkim=, dmarc= tokens."""
    m = re.search(r"^Authentication-Results:.*$", header_text, flags=re.IGNORECASE | re.MULTILINE)
    if not m:
        return {}
    line = m.group(0)
    out = {}
    for key in ("spf", "dkim", "dmarc"):
        m2 = re.search(rf"\b{key}=([a-zA-Z]+)\b", line, flags=re.IGNORECASE)
        if m2:
            out[key] = m2.group(1).lower()
    return out


def check_spf(header_text: str) -> tuple[str, str]:
    auth = parse_auth_results(header_text)
    if "spf" in auth:
        return ("PASS" if auth["spf"] == "pass" else "FAIL", f"Authentication-Results spf={auth['spf']}")
    # fallback: Received-SPF:
    m = re.search(r"^Received-SPF:\s*([a-zA-Z]+)", header_text, flags=re.IGNORECASE | re.MULTILINE)
    if not m:
        return ("WARN", "No SPF result found (missing Authentication-Results and Received-SPF).")
    val = m.group(1).lower()
    return ("PASS" if val == "pass" else "FAIL", f"Received-SPF: {val}")


def check_dkim(header_text: str) -> tuple[str, str]:
    auth = parse_auth_results(header_text)
    if "dkim" in auth:
        return ("PASS" if auth["dkim"] == "pass" else "FAIL", f"Authentication-Results dkim={auth['dkim']}")
    if re.search(r"^DKIM-Signature:", header_text, flags=re.IGNORECASE | re.MULTILINE):
        return ("OK", "DKIM-Signature header present (no pass/fail result found).")
    return ("WARN", "No DKIM-Signature header found.")


def check_tls_hint(header_text: str) -> tuple[str, str]:
    # Heuristic: look for TLS tokens or ESMTPS
    if re.search(r"TLSv\d\.\d", header_text, flags=re.IGNORECASE):
        return ("OK", "TLS version token found in headers.")
    if re.search(r"\bESMTPS\b", header_text, flags=re.IGNORECASE):
        return ("OK", "ESMTPS found (likely TLS, provider-dependent).")
    return ("WARN", "No clear TLS hint detected in headers (heuristic check).")


def check_dmarc_published(domain: str | None) -> tuple[str, str]:
    if not domain:
        return ("WARN", "Cannot determine From domain to check DMARC.")
    try:
        answers = dns.resolver.resolve(f"_dmarc.{domain}", "TXT")
        for record in answers:
            if "v=DMARC1" in str(record):
                return ("OK", f"DMARC TXT record published for _dmarc.{domain}")
        return ("WARN", f"TXT records found but no v=DMARC1 for _dmarc.{domain}")
    except dns.resolver.NoAnswer:
        return ("WARN", f"No DMARC TXT record found for _dmarc.{domain}")
    except dns.resolver.NXDOMAIN:
        return ("WARN", f"Domain not found or no DMARC record for _dmarc.{domain}")
    except dns.resolver.Timeout:
        return ("ERROR", "DNS query timed out.")
    except Exception as e:
        return ("ERROR", f"DNS query failed: {e}")


def check_from_returnpath_mismatch(header_text: str, from_domain: str | None) -> tuple[str, str]:
    rp = re.search(r"^Return-Path:\s*<?([^>\s]+)>?", header_text, flags=re.IGNORECASE | re.MULTILINE)
    return_path_domain = None
    if rp:
        addr = rp.group(1).strip()
        if "@" in addr:
            return_path_domain = addr.split("@", 1)[1].lower()

    if from_domain and return_path_domain and from_domain != return_path_domain:
        return ("WARN", f"From domain '{from_domain}' != Return-Path domain '{return_path_domain}'")
    if not return_path_domain:
        return ("WARN", "Return-Path not found or not parseable.")
    return ("OK", "From and Return-Path domains match (or mismatch not detectable).")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze a raw email header file (triage).")
    parser.add_argument("-i", "--input", help="Path to the email header text file.")
    args = parser.parse_args()

    input_path = args.input or input("Enter the path to the email header text file: ").strip()
    if not input_path:
        print("No input provided.")
        return 1

    p = Path(input_path)
    if not p.is_file():
        print(f"Error: File not found: {p}")
        return 1

    header_text = p.read_text(encoding="utf-8", errors="replace")

    from_domain = extract_domain_from_header(re.search(r"^From:\s*(.*)$", header_text, flags=re.IGNORECASE | re.MULTILINE).group(1)
                                            ) if re.search(r"^From:\s*(.*)$", header_text, flags=re.IGNORECASE | re.MULTILINE) else None

    checks = []
    spf_s, spf_m = check_spf(header_text); checks.append(["SPF", spf_s, spf_m])
    dkim_s, dkim_m = check_dkim(header_text); checks.append(["DKIM", dkim_s, dkim_m])
    tls_s, tls_m = check_tls_hint(header_text); checks.append(["TLS (hint)", tls_s, tls_m])
    dm_s, dm_m = check_dmarc_published(from_domain); checks.append(["DMARC (published)", dm_s, dm_m])
    mm_s, mm_m = check_from_returnpath_mismatch(header_text, from_domain); checks.append(["From vs Return-Path", mm_s, mm_m])

    table = []
    for name, status, message in checks:
        table.append([name, _status_color(status), message])

    print(tabulate(table, headers=["Check", "Status", "Message"], tablefmt="grid"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
