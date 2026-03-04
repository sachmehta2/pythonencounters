# PST to EML

**Part of [Python Encounters](https://rtapulse.com/python-encounters/) — rtapulse.com**
Script: [`pst_to_eml.py`](https://github.com/sachmehta2/pythonencounters/blob/main/user-tech/pst-to-eml/pst_to_eml.py) · [Published page](https://rtapulse.com/python-encounters/user-tech/pst-to-eml/)

---

## The problem

Outlook PST files are a closed format. They cannot be opened without Outlook, cannot be searched at scale without specialist tooling, and cannot be produced in legal or regulatory proceedings without first converting them into a standard format. When an organisation receives a data subject access request, faces an eDiscovery obligation, or needs to migrate away from Outlook — the PST becomes a blocker. Manual export through the Outlook GUI is slow, inconsistent across large archives, and drops metadata.

---

## Use case

An employee has left the organisation under disputed circumstances and their mailbox PST has been preserved as a legal hold item. The organisation's legal team needs the mailbox contents in a reviewable format for disclosure. You run this script against the PST archive on a controlled machine. The output is a date-stamped EML folder tree — each message as an individual file with headers and attachments intact — that can be ingested into a legal review tool or searched by the legal team directly.

---

## What the script does

pst_to_eml.py first calls the system readpst utility to extract the PST into MBOX format, then processes each MBOX file to write individual .eml messages into a mirrored folder tree. Attachments are preserved within each EML file. The script requires readpst to be installed (available on Linux/macOS via package manager; Windows via WSL). Always run on a copy of the PST — never on the original. Large archives are disk-intensive.

---

## Install and run

```bash
# Install readpst (Ubuntu/Debian)
$ sudo apt-get install pst-utils

# macOS
$ brew install libpst

# Run the conversion
$ python3 pst_to_eml.py

# Follow prompts: enter PST path and output directory
```

---

## Dependencies

- `readpst (system tool)` — PST extraction — must be installed separately via apt or brew
- `mailbox (stdlib)` — MBOX parsing after readpst extraction
- `email (stdlib)` — EML message assembly and header preservation
- `Disk space` — PST extraction is disk-heavy — output is typically 1.5–2× the PST size

---

## Sample output

**Success:**
```
PST path    : /evidence/mailbox_john_doe.pst
  Output dir  : /evidence/eml_output/
  Extracting  : readpst → MBOX  ...  done  (3 folders, 4,821 messages)
  Converting  : MBOX → EML     ...  done

  Output tree:
    /evidence/eml_output/
      Inbox/         (2,104 .eml files)
      Sent Items/    (1,893 .eml files)
      Deleted Items/ (  824 .eml files)

  Conversion complete — 4,821 messages written.
```

**Error / warning:**
```
PST path    : /evidence/mailbox_archive.pst
  Output dir  : /evidence/eml_output/

  ERROR: readpst not found at /usr/bin/readpst
  Install with: sudo apt-get install pst-utils
  Or set READPST_PATH in the script to the correct binary location.

  If PST is password-protected or corrupt, readpst will report
  errors per folder — partial output may still be usable.
```

---

## Regulation map

| Framework | Control / Clause | Obligation |
|-----------|-----------------|------------|
| **GDPR / UK GDPR** | Article 15 — Subject Access Request | Data subject access requests require the ability to produce personal data held in any format, including email archives. |
| **eDiscovery (US)** | FRCP Rule 34 | Electronically stored information must be producible in a reasonably usable form. EML conversion satisfies this requirement. |
| **ISO 27001:2022** | A.16.1.7 | Evidence relating to information security incidents must be collected and preserved. PST-to-EML supports forensic preservation. |
| **DORA (EU)** | Article 17 | ICT incident investigations may require retrieval of email evidence from legacy or preserved mailboxes. |
| **SOX** | Records Retention | Financial institution email records must be retrievable for the defined retention period regardless of storage format. |
| **SEBI (India)** | LODR / Surveillance | Regulatory investigations may require email evidence production from employee mailboxes in accessible formats. |

---

## Safety

- Run only in environments you are authorised to inspect.
- Do not commit credentials or API keys. Use environment variables or `.env` files.
- Treat all outputs as evidence — store with retrieval timestamps.

---

MIT licence · [rtapulse.com](https://rtapulse.com) · grcguy@rtapulse.com
