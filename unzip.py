import zipfile
import os
import re
from pathlib import Path

# Define root path
root_path = r"/Users/saayella/Documents/GitHub/Digital_Finance_Greenwashing"  # Ensure this path is correct

# Define ZIP filename and construct full input path
zip_file = "10-X_C_2024.zip"  # Ensure the correct filename
input_path = os.path.join(root_path, zip_file)

# Define output directory (no subfolders like 2024/QTRx)
output_folder = "2024_10_K"
output_path = os.path.join(root_path, output_folder)

# Ensure output folder exists
os.makedirs(output_path, exist_ok=True)

# Define the subfolders inside "2024" to target
input_subfolders = ["QTR1", "QTR2", "QTR3", "QTR4"]

# Function to extract only 10-K files **without subfolders** and count them
def extract_10k_files(zip_path, subfolders, output_dir):
    file_count = 0  # Counter for extracted files

    with zipfile.ZipFile(zip_path, 'r') as z:
        for subfolder in subfolders:
            for file in z.namelist():
                # Check if the file is in a QTR folder and is a 10-K (not 10-K-A)
                if re.search(fr"2024/{subfolder}/.*_10-K_", file) and not re.search(r"10-K-[A-Za-z]", file):  # some folders didn't have {year} > QTR1
                    # Get only the filename (remove folder structure)
                    filename = os.path.basename(file)
                    output_file_path = os.path.join(output_dir, filename)

                    # Extract the file without keeping the subfolder structure
                    with z.open(file) as src, open(output_file_path, "wb") as dest:
                        dest.write(src.read())

                    file_count += 1  # Increment counter
                print(f'# of files extracted = {file_count}')
    print(f"✅ Extraction completed. {file_count} files were saved in '{output_path}'.")

# Run extraction
extract_10k_files(input_path, input_subfolders, output_path)