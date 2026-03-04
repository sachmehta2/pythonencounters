# File Hash MD5

**Part of [Python Encounters](https://rtapulse.com/python-encounters/) — rtapulse.com**
Script: [`generate_md5_hash.py`](https://github.com/sachmehta2/pythonencounters/blob/main/grc-tech/file-hash-md5/generate_md5_hash.py) · [Published page](https://rtapulse.com/python-encounters/grc-tech/file-hash-md5/)

---

## The problem

File integrity is a frequently cited control and infrequently tested one. A vendor delivers a configuration file, a patch package, or a data extract. The organisation loads it. Nobody hashed the delivery. Six months later, during an audit, the question is whether the file that arrived was the file that was applied. There is no answer. The same problem appears internally — a script last reviewed in Q1 may have been modified without a change ticket. Without a hash taken at the point of review, the question of whether it changed since then cannot be answered.

---

## Use case

During a SOX ITGC review, you are testing change management controls for a critical financial reporting system. A developer claims no unauthorised changes were made to configuration files since the last review. You ask for the hash taken at the last review. There is none. You run this script against the current files to establish a baseline. Those hash values go into the workpaper as the point-in-time reference for the next review cycle — converting an untestable assertion into a verifiable one.

---

## What the script does

generate_md5_hash.py reads the target file in binary chunks, computes the MD5 digest using Python's hashlib library, and writes two output files: md5_hash_output.txt containing the hash value and file metadata, and hash_validation_instructions.txt containing the steps a recipient can follow to verify the hash independently. No external dependencies. Note: MD5 is appropriate for integrity verification in non-adversarial contexts. Where cryptographic collision resistance matters, use SHA-256.

---

## Install and run

```bash
# No external dependencies — stdlib only
$ python3 generate_md5_hash.py -f path/to/file

# Output: md5_hash_output.txt and hash_validation_instructions.txt
$ cat md5_hash_output.txt
```

---

## Dependencies

- `hashlib (stdlib)` — Computes the MD5 digest — no external install required
- `os, sys (stdlib)` — File path handling and error output
- `No network access` — Entirely local — processes the file in place

---

## Sample output

**Success:**
```
File   : /etc/app/config.yaml
  Size   : 4,218 bytes
  MD5    : a3f2c891d4e7b0123456789abcdef012
  Time   : 2026-03-02T19:45:00Z

  Written → md5_hash_output.txt
  Written → hash_validation_instructions.txt

  Hash computed successfully. Attach md5_hash_output.txt to workpaper.
```

**Error / warning:**
```
ERROR: File not found — /etc/app/missing_config.yaml
  Check the file path and ensure the script has read access.

  If verifying a received file:
  Expected : a3f2c891d4e7b0123456789abcdef012
  Computed : 99b1c44f23a8d701fedcba9876543210
  ⚠  Hash mismatch — file may have been modified after delivery.
```

---

## Regulation map

| Framework | Control / Clause | Obligation |
|-----------|-----------------|------------|
| **ISO 27001:2022** | A.12.2.1 | Controls against malware and unauthorised changes must include the ability to verify file integrity. |
| **SOX ITGC** | Change Management | Change management controls must be testable. Hash baselines make configuration change assertions auditable. |
| **PCI DSS v4.0** | 11.5.2 | A change detection mechanism must be deployed to alert personnel to unauthorised changes to critical files. |
| **NIST CSF 2.0** | PR.DS-6 | Integrity checking mechanisms must be used to verify software, firmware, and information integrity. |
| **CIS Controls v8** | Control 3 — Data Protection | File integrity monitoring is a component of data protection — hashing enables baseline comparison. |
| **DORA (EU)** | Article 9 | ICT assets must be protected against unauthorised modification; integrity verification supports this requirement. |

---

## Safety

- Run only in environments you are authorised to inspect.
- Do not commit credentials or API keys. Use environment variables or `.env` files.
- Treat all outputs as evidence — store with retrieval timestamps.

---

MIT licence · [rtapulse.com](https://rtapulse.com) · grcguy@rtapulse.com
