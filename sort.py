import os
import re
import shutil
from pathlib import Path

# Paths
input_folder = Path("/Users/saayella/Documents/GitHub/Digital_Finance_Greenwashing/2024_10_K")
output_folder = Path("/Users/saayella/Documents/GitHub/Digital_Finance_Greenwashing/company_sorted_2")
output_folder.mkdir(exist_ok=True)

# List of required company names (normalized for matching)
target_companies = ["Exxon Mobil", "Chevron", "Occidental Petroleum", "Walmart", "Costco", "Home Depot", "Pepsi Co"]
                    

def get_conformed_name(file_path):
    """Extract COMPANY CONFORMED NAME from a 10-K text file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read(5000)  # just the header
    match = re.search(r"COMPANY CONFORMED NAME:\s*(.+)", content, re.IGNORECASE)
    return match.group(1).strip() if match else None

def normalize(text):
    """Normalize text for matching (lowercase, strip punctuation)."""
    return re.sub(r"[^a-z0-9 ]", "", text.lower())

def main():
    for file in input_folder.glob("*.txt"):
        name = get_conformed_name(file)
        if not name:
            print(f"[!] No conformed name found in {file.name}")
            continue

        norm_name = normalize(name)

        for target in target_companies:
            if normalize(target) in norm_name:
                # Make subfolder for this target
                company_dir = output_folder / target.replace(" ", "_")
                company_dir.mkdir(exist_ok=True)

                # Copy file
                dest = company_dir / file.name
                shutil.copy(file, dest)
                print(f"[+] {file.name} ({name}) -> {company_dir}")
                break

if __name__ == "__main__":
    main()
