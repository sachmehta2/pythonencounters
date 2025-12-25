`netmon.py` captures local active network connections, enriches them with process context where available, prints a live view, and appends results to a CSV for lightweight evidence capture and troubleshooting.

**Inputs:** none (local host). **Outputs:** console + `network_connections.csv`. **Run:** `python netmon.py` (snapshot: `python netmon.py --once`). **Known limitations:** some details require admin/root; hostname resolution may be slow/noisy. **Safety:** authorized systems only; use `--once`/`--interval` for controlled evidence runs.
