#!/usr/bin/env python3
"""netmon.py

Local network connection monitor (authorized systems only).

Changes vs earlier version:
  - Adds --once snapshot mode (prints + writes one sample and exits)
  - Adds --interval (seconds) for loop mode
  - Adds --include-na to include connections without remote endpoint/hostname
  - Removes noisy debug prints

Output CSV schema is stable and appended to by default.
"""

import argparse
import csv
import os
import socket
import sys
import time
from pathlib import Path

import psutil
from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)

DEFAULT_CSV = "network_connections.csv"


def is_admin() -> bool:
    """Best-effort admin/root check."""
    if os.name == "nt":
        try:
            import ctypes  # type: ignore
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False


def resolve_hostname(ip_address: str) -> str:
    try:
        if ip_address and ip_address != "0.0.0.0" and ip_address != "N/A":
            return socket.gethostbyaddr(ip_address)[0]
        return "N/A"
    except (socket.herror, socket.gaierror):
        return "N/A"


def get_network_connections(include_na: bool) -> list[list]:
    connections = []
    try:
        all_connections = psutil.net_connections(kind="inet")
        for conn in all_connections:
            try:
                protocol = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
                local_ip = conn.laddr.ip if conn.laddr else "N/A"
                local_port = conn.laddr.port if conn.laddr else "N/A"
                remote_ip = conn.raddr.ip if conn.raddr else "N/A"
                remote_port = conn.raddr.port if conn.raddr else "N/A"
                remote_hostname = resolve_hostname(remote_ip) if remote_ip != "N/A" else "N/A"
                pid = conn.pid or "N/A"

                process_name = "N/A"
                if conn.pid:
                    try:
                        process_name = psutil.Process(conn.pid).name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        process_name = "N/A"

                state = conn.status or "N/A"
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                row = [
                    protocol, local_ip, local_port, remote_ip, remote_hostname, remote_port,
                    pid, process_name, state, timestamp
                ]

                if include_na:
                    connections.append(row)
                else:
                    # Keep earlier behavior: only include rows with a remote endpoint + hostname
                    if remote_hostname != "N/A" and remote_port != "N/A":
                        connections.append(row)

            except Exception as e:
                print(f"Error processing a connection: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Error retrieving network connections: {e}", file=sys.stderr)

    return connections


def write_to_csv(csv_path: Path, connections: list[list]) -> None:
    headers = [
        "Protocol", "Local IP", "Local Port", "Remote IP", "Remote Hostname", "Remote Port",
        "PID", "Process Name", "State", "Timestamp"
    ]
    file_exists = csv_path.exists()
    with csv_path.open(mode="a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(headers)
        w.writerows(connections)


def colorize_na_columns(row: list) -> list[str]:
    out = []
    for cell in row:
        s = str(cell)
        out.append(Fore.RED + s + Style.RESET_ALL if s == "N/A" else s)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitor local network connections and log to CSV.")
    parser.add_argument("--csv", default=DEFAULT_CSV, help=f"CSV output path (default: {DEFAULT_CSV})")
    parser.add_argument("--interval", type=int, default=5, help="Seconds between updates (default: 5)")
    parser.add_argument("--once", action="store_true", help="Capture one snapshot and exit")
    parser.add_argument("--include-na", action="store_true", help="Include connections without remote endpoint/hostname")
    parser.add_argument("--no-admin-check", action="store_true", help="Skip admin/root check (may reduce visibility)")
    args = parser.parse_args()

    if not args.no_admin_check and not is_admin():
        print("Warning: Not running as admin/root. Some process or connection details may be missing.", file=sys.stderr)

    csv_path = Path(args.csv)

    try:
        while True:
            conns = get_network_connections(include_na=args.include_na)
            headers = [
                "Protocol", "Local IP", "Local Port", "Remote IP", "Remote Hostname", "Remote Port",
                "PID", "Process Name", "State", "Timestamp"
            ]
            colored = [colorize_na_columns(r) for r in conns]
            print(tabulate(colored, headers=headers, tablefmt="grid"))

            if conns:
                write_to_csv(csv_path, conns)

            if args.once:
                print(Fore.YELLOW + Style.BRIGHT + f"Snapshot complete. Wrote {len(conns)} rows to {csv_path}.")
                return 0

            print(Fore.YELLOW + Style.BRIGHT + f"\nRefreshed. Appended {len(conns)} rows. Next update in {args.interval}s...\n")
            time.sleep(max(1, args.interval))

    except KeyboardInterrupt:
        print(Fore.RED + Style.BRIGHT + "\nInterrupted by user. Exiting...", file=sys.stderr)
        return 0
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
