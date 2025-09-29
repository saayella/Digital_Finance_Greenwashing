import os
import re
import shutil
from pathlib import Path
from difflib import get_close_matches

INPUT_FOLDER = "/Users/saayella/Documents/GitHub/Digital_Finance_Greenwashing/company_sorted"
FAILED_LIST = "dataset_creation/failed_item1.txt"
OUTPUT_FOLDER = "dataset_creation/failed_filings"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def get_conformed_name(file_path):
    """Extract COMPANY CONFORMED NAME from a 10-K text file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(5000)
        match = re.search(r"COMPANY CONFORMED NAME:\s*(.+)", content, re.IGNORECASE)
        return match.group(1).strip() if match else "UNKNOWN"
    except Exception:
        return "READ_ERROR"


def build_file_index(root_folder):
    """Index all files under INPUT_FOLDER (recursive)."""
    file_index = {}
    for root, _, files in os.walk(root_folder):
        for fname in files:
            file_index[fname] = os.path.join(root, fname)
    return file_index


def main():
    file_index = build_file_index(INPUT_FOLDER)
    all_filenames = list(file_index.keys())

    failed_files = []
    with open(FAILED_LIST, "r", encoding="utf-8") as f:
        failed_files = [line.strip() for line in f if line.strip()]

    print("\nFailed Filings & Company Names:\n")
    for fname in failed_files:
        src = None

        # Exact match first
        if fname in file_index:
            src = file_index[fname]
        else:
            # Try fuzzy match (filename prefix/suffix similarity)
            matches = get_close_matches(fname, all_filenames, n=1, cutoff=0.6)
            if matches:
                match_name = matches[0]
                src = file_index[match_name]
                print(f"[~] Fuzzy matched {fname} -> {match_name}")

        if not src:
            print(f"[!] Could not locate {fname}")
            continue

        dest = os.path.join(OUTPUT_FOLDER, os.path.basename(src))
        shutil.copy(src, dest)

        company = get_conformed_name(src)
        print(f"{os.path.basename(src)} -> {company}")


if __name__ == "__main__":
    main()
