`pst_to_eml.py` converts an Outlook PST archive into `.eml` files (with attachments) using the external `readpst` tool, then converts extracted MBOX content into an EML folder tree.

**Inputs:** PST path + output directory + `readpst` installed. **Outputs:** `eml/` folder tree. **Run:** `python pst_to_eml.py` and follow prompts. **Known limitations:** PSTs can be huge; conversion is disk-heavy and depends on external tooling. **Safety:** run on a copy first; make `READPST_PATH` configurable and do not commit email data.
