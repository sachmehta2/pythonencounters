`SSLcert.py` retrieves and displays SSL/TLS **certificate metadata** (subject/issuer/SAN/expiry) for a hostname. It is intentionally **inspection-only** and does not claim to enumerate supported TLS versions/ciphers.

**Inputs:** domain (e.g., `example.com`). **Outputs:** console table. **Run:** `python SSLcert.py example.com` (use `--insecure` only to retrieve metadata from invalid/self-signed certs). **Known limitations:** negotiated session ≠ supported protocol range. **Safety:** treat results as indicative; keep wording strict (“observed” vs “supported”).
