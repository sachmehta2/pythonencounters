#!/usr/bin/env python3
"""generate_md5_hash.py

Inspection-only integrity helper: compute an MD5 hash for a file and write it to an output file
along with a small validation note. No auto-install / no environment mutation.

Note: MD5 is fine for basic integrity checks in trusted workflows. For stronger guarantees,
prefer SHA-256.
"""

import argparse
import hashlib
import os
from pathlib import Path


def calculate_md5(file_path: Path) -> str:
    md5 = hashlib.md5()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate MD5 for a file and write outputs.")
    parser.add_argument("-f", "--file", dest="file_path", help="Path to the input file.")
    parser.add_argument("-o", "--out", default="md5_hash_output.txt", help="Output file for the MD5 hash.")
    parser.add_argument("--instructions", default="hash_validation_instructions.txt",
                        help="Output file for validation instructions.")
    args = parser.parse_args()

    file_path = args.file_path or input("Enter the path to the file: ").strip()
    if not file_path:
        print("No file path provided.")
        return 1

    p = Path(file_path)
    if not p.is_file():
        print("Invalid file path. Please provide a valid file.")
        return 1

    try:
        md5_hex = calculate_md5(p)
    except Exception as e:
        print(f"Error reading file: {e}")
        return 1

    out_path = Path(args.out)
    instr_path = Path(args.instructions)

    write_text(out_path, md5_hex + "\n")
    write_text(
        instr_path,
        textwrap.dedent(f"""            How to Validate the MD5 Hash (Basic Integrity Check)
        ===============================================

        File:
          {p}

        Expected MD5:
          {md5_hex}

        Option 1 (Python):
          python - << 'PY'
          import hashlib
          from pathlib import Path
          p = Path(r"{str(p)}")
          h = hashlib.md5()
          with p.open('rb') as f:
              for chunk in iter(lambda: f.read(4096), b''):
                  h.update(chunk)
          print(h.hexdigest())
          PY

        Option 2 (Windows PowerShell):
          Get-FileHash -Algorithm MD5 "{str(p)}"

        Option 3 (macOS/Linux):
          md5 "{str(p)}"        # macOS
          md5sum "{str(p)}"     # Linux

        If the calculated value matches the expected MD5, the file is intact.
        """)
    )

    print(f"MD5: {md5_hex}")
    print(f"Saved hash to: {out_path}")
    print(f"Saved instructions to: {instr_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
