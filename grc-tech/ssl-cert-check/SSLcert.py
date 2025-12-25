#!/usr/bin/env python3
"""SSLcert.py (inspection-only)

Purpose: Retrieve and display SSL/TLS *certificate metadata* for a hostname (issuer/subject/SAN/expiry).
This script is intentionally **inspection-only**:
  - It does NOT claim to enumerate supported TLS versions/ciphers.
  - It does NOT perform deep chain/path validation beyond what the underlying SSL context does.

By default, it uses the system trust store (verification ON). If you need to retrieve metadata
from a host with an invalid/self-signed cert, use --insecure (verification OFF) and the output
will be labeled accordingly.
"""

import argparse
import socket
import ssl
from datetime import datetime, timezone
from urllib.parse import urlparse

from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)


def normalize_host(user_input: str) -> str:
    user_input = user_input.strip()
    if user_input.startswith(("http://", "https://")):
        parsed = urlparse(user_input)
        return parsed.netloc.split(":")[0]
    return user_input.split(":")[0]


def fetch_cert(hostname: str, port: int, insecure: bool) -> tuple[dict | None, str | None, bool]:
    """Return (cert_dict, error, verified)."""
    try:
        if insecure:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            verified = False
        else:
            ctx = ssl.create_default_context()
            verified = True

        with socket.create_connection((hostname, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                return cert, None, verified
    except Exception as e:
        return None, str(e), (not insecure)  # verified flag is "intended", not guaranteed


def _get_name_tuple(name_list) -> str:
    # name_list is like ((('commonName','example.com'),),)
    parts = []
    for rdn in name_list or []:
        for k, v in rdn:
            parts.append(f"{k}={v}")
    return ", ".join(parts) if parts else "N/A"


def parse_expiry(cert: dict) -> tuple[str, str]:
    if not cert or "notAfter" not in cert:
        return "N/A", Fore.RED + "ERROR" + Style.RESET_ALL
    # Example: 'Jun  1 12:00:00 2026 GMT'
    not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    remaining_days = int((not_after - datetime.now(timezone.utc)).total_seconds() // 86400)
    if remaining_days < 0:
        return f"Expired ({abs(remaining_days)} days ago)", Fore.RED + "CRITICAL" + Style.RESET_ALL
    if remaining_days < 30:
        return f"Expires in {remaining_days} days", Fore.YELLOW + "WARN" + Style.RESET_ALL
    return f"Valid (expires in {remaining_days} days)", Fore.GREEN + "OK" + Style.RESET_ALL


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect certificate metadata for a domain (inspection-only).")
    parser.add_argument("domain", nargs="?", help="Domain to inspect (e.g., example.com or https://example.com).")
    parser.add_argument("--port", type=int, default=443, help="Port (default: 443).")
    parser.add_argument("--insecure", action="store_true",
                        help="Disable verification to retrieve metadata from invalid/self-signed certs.")
    args = parser.parse_args()

    domain = args.domain or input("Enter the domain to check (e.g., example.com): ").strip()
    if not domain:
        print("No domain provided. Exiting.")
        return 1

    host = normalize_host(domain)

    cert, err, verified = fetch_cert(host, args.port, args.insecure)
    if err:
        print(Fore.RED + f"Failed to retrieve certificate: {err}" + Style.RESET_ALL)
        return 1

    exp_status, exp_sev = parse_expiry(cert)

    subject = _get_name_tuple(cert.get("subject"))
    issuer = _get_name_tuple(cert.get("issuer"))
    not_before = cert.get("notBefore", "N/A")
    not_after = cert.get("notAfter", "N/A")
    serial = cert.get("serialNumber", "N/A")

    san = "N/A"
    if "subjectAltName" in cert:
        try:
            san = ", ".join([v for (t, v) in cert["subjectAltName"] if t.lower() in {"dns", "ip address"}])
        except Exception:
            san = "N/A"

    table_data = [
        ["Mode", "Inspection-only (metadata)"],
        ["Verification", "ON (system trust store)" if (not args.insecure) else "OFF (--insecure)"],
        ["Subject", subject],
        ["Issuer", issuer],
        ["Serial", serial],
        ["SAN", san],
        ["Not Before", not_before],
        ["Not After", not_after],
        ["Expiry Status", exp_status],
        ["Severity", exp_sev],
    ]

    print(tabulate(table_data, headers=["Field", "Value"], tablefmt="grid"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
