import os
import subprocess
import mailbox

def run_readpst(pst_file, output_folder):
    readpst_path = r"C:\tools\libpst\bin\readpst.exe"

    if not os.path.exists(readpst_path):
        print(f"❌ readpst.exe not found at: {readpst_path}")
        return False

    if not os.path.exists(pst_file):
        print(f"❌ PST file not found: {pst_file}")
        return False

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cmd = [
        readpst_path,
        "-r",  # recursive folder processing
        "-u",  # UTC-safe filenames (Windows compatible)
        "-o", output_folder,
        pst_file
    ]

    print("\n🚀 Running readpst to extract .mbox files...")
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.stdout.strip():
            print("📤 Output:\n", result.stdout.strip())
        if result.stderr.strip():
            print("⚠️ Warnings/Errors:\n", result.stderr.strip())

        print("✅ MBOX extraction complete.\n")
        return True

    except Exception as e:
        print(f"❌ Failed to run readpst: {e}")
        return False

def convert_mbox_to_eml(mbox_path, eml_output_dir):
    os.makedirs(eml_output_dir, exist_ok=True)
    count = 0

    try:
        mbox = mailbox.mbox(mbox_path)
    except Exception as e:
        print(f"❌ Cannot open mbox file: {mbox_path}\n  ↳ {e}")
        return 0

    for idx, msg in enumerate(mbox):
        try:
            msg_bytes = msg.as_bytes()

            eml_filename = f"message_{idx+1:05d}.eml"
            eml_path = os.path.join(eml_output_dir, eml_filename)

            with open(eml_path, 'wb') as f:
                f.write(msg_bytes)

            count += 1

        except Exception as e:
            print(f"❌ Error saving message {idx+1} from {os.path.basename(mbox_path)}:\n  ↳ {e}")

    print(f"📨 Converted {count} emails from {os.path.basename(mbox_path)} (attachments preserved)")
    return count

def cleanup_residual_files(folder):
    deleted = []
    for name in ['.type', '.size']:
        file_path = os.path.join(folder, name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                deleted.append(name)
            except Exception as e:
                print(f"⚠️ Couldn't delete {name} in {folder}: {e}")
    if deleted:
        print(f"🧹 Deleted residual files in {folder}: {', '.join(deleted)}")

def process_all_mbox_files(root_output_dir):
    total_emails = 0
    for root, dirs, files in os.walk(root_output_dir):
        for file in files:
            if file.lower() == "mbox":
                mbox_file_path = os.path.join(root, file)
                eml_output_path = os.path.join(root, "eml")
                print(f"\n🔍 Found MBOX: {mbox_file_path}")
                count = convert_mbox_to_eml(mbox_file_path, eml_output_path)
                cleanup_residual_files(root)
                if count > 0:
                    try:
                        os.remove(mbox_file_path)
                        print(f"🗑️ Deleted mbox file: {mbox_file_path}")
                    except Exception as e:
                        print(f"⚠️ Failed to delete mbox file: {e}")
                total_emails += count
    print(f"\n✅ All conversions complete. Total emails extracted: {total_emails}")

# ---------------- Entry Point ----------------

if __name__ == "__main__":
    print("=== PST to MBOX to EML Extractor (Preserves Attachments & Images) ===\n")

    pst_path = input("Enter full path to PST file (e.g., C:\\Users\\Sam\\archive.pst): ").strip('"').strip()
    output_dir = input("Enter full path to output folder (e.g., C:\\Users\\Sam\\converted_eml): ").strip('"').strip()

    if run_readpst(pst_path, output_dir):
        process_all_mbox_files(output_dir)
