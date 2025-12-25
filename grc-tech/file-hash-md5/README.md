`generate_md5_hash.py` computes the MD5 hash for a chosen file and writes the hash plus validation instructions to text outputs. It’s a practical integrity receipt for routine file sharing.

**Inputs:** file path. **Outputs:** `md5_hash_output.txt` and `hash_validation_instructions.txt`. **Run:** `python generate_md5_hash.py -f path/to/file`. **Known limitations:** MD5 is not collision-resistant for adversarial scenarios (use SHA-256 if needed). **Safety:** deterministic script; no environment mutation or auto-installs.
