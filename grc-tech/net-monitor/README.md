# Net Monitor

**Part of [Python Encounters](https://rtapulse.com/python-encounters/) — rtapulse.com**
Script: [`netmon.py`](https://github.com/sachmehta2/pythonencounters/blob/main/grc-tech/net-monitor/netmon.py) · [Published page](https://rtapulse.com/python-encounters/grc-tech/net-monitor/)

---

## The problem

Ask a system owner what ports are listening on a server and they will give you the documentation. Ask what was actually listening during an incident, or at the time of last audit evidence collection, and the answer is usually a guess. Network baselines exist on paper in most organisations — but the paper was last updated when the server was built. Unexpected listeners, persistent outbound connections to unknown external IPs, and services running on non-standard ports are findings that documentation will never surface.

---

## Use case

A change management review has flagged a production database server as 'no changes in the last quarter'. You run this script before and after a scheduled maintenance window to establish a connection baseline. Post-window, the output shows a new outbound connection on port 5432 to an IP that was not present in the pre-window snapshot. That connection is not in the change ticket. The CSV timestamps and process names become the evidence that an undocumented change was made.

---

## What the script does

netmon.py uses Python's psutil library to enumerate active TCP/UDP connections on the local host, resolves each connection to a process name and PID where permissions allow, and writes the enriched output to network_connections.csv with a timestamp per row. Use --once for a single snapshot or --interval for continuous polling. Admin or root privileges are recommended for full process attribution — the script degrades gracefully without them.

---

## Install and run

```bash
# Install dependency
$ pip install psutil

# Single snapshot
$ python3 netmon.py --once

# Continuous — poll every 10 seconds
$ python3 netmon.py --interval 10

# Run with elevated privileges for full process attribution
$ sudo python3 netmon.py --once
```

---

## Dependencies

- `psutil` — Enumerates active connections and resolves process names/PIDs
- `Admin / root (recommended)` — Required for full process attribution; script runs without it but shows partial data
- `Local host access` — Inspects connections on the machine where the script runs — not remote

---

## Sample output

**Success:**
```
Timestamp            Proto  Local addr          Remote addr         PID    Process
  2026-03-02 19:45:00  TCP    0.0.0.0:22          *:*                 1024   sshd
  2026-03-02 19:45:00  TCP    127.0.0.1:5432      127.0.0.1:54821     2301   postgres
  2026-03-02 19:45:00  TCP    192.168.1.10:443    *:*                 3102   nginx
  2026-03-02 19:45:00  TCP    192.168.1.10:54821  52.94.1.1:443       3405   python3

  Output appended → network_connections.csv  (4 rows)
```

**Error / warning:**
```
Timestamp            Proto  Local addr          Remote addr         PID    Process
  2026-03-02 21:12:04  TCP    0.0.0.0:22          *:*                 1024   sshd
  2026-03-02 21:12:04  TCP    192.168.1.10:54900  185.220.101.5:4444  7821   python3
  2026-03-02 21:12:04  TCP    0.0.0.0:31337       *:*                 7821   python3

  ⚠  Unexpected listener on port 31337. Outbound to 185.220.101.5:4444 — investigate.
```

---

## Regulation map

| Framework | Control / Clause | Obligation |
|-----------|-----------------|------------|
| **NIST CSF 2.0** | DE.CM-1 | Networks must be monitored to detect potential cybersecurity events. Baseline comparison directly supports this control. |
| **ISO 27001:2022** | A.12.4.1 | Event logging must capture network activity sufficient to detect anomalous behaviour. |
| **PCI DSS v4.0** | 10.2 / 11.5 | Audit logs must capture network connections; change detection mechanisms must alert on unexpected changes. |
| **FFIEC CAT** | Evolving — Threat Intelligence | Active monitoring of network connections is an evolving maturity requirement for financial institutions. |
| **DORA (EU)** | Article 9 / Article 17 | ICT systems must be monitored and anomalous connections must be detectable as part of incident management obligations. |
| **CIS Controls v8** | Control 13 — Network Monitoring | Organisations must actively manage and monitor network connections to detect and respond to threats. |

---

## Safety

- Run only in environments you are authorised to inspect.
- Do not commit credentials or API keys. Use environment variables or `.env` files.
- Treat all outputs as evidence — store with retrieval timestamps.

---

MIT licence · [rtapulse.com](https://rtapulse.com) · grcguy@rtapulse.com
