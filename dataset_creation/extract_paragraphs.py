import os
import re
import fitz  # PyMuPDF for PDFs
from bs4 import BeautifulSoup  # for HTML parsing

INPUT_FOLDER = "/Users/saayella/Documents/GitHub/Digital_Finance_Greenwashing/dataset_creation/reports/"
OUTPUT_FILE = "dataset_creation/paragraphs.txt"

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text

def extract_business_summary_pdf(text):
    text = text.replace("\n", " ")
    start_match = re.search(r"(?i)(business summary|item\s*1\.*\s*business)", text)
    end_match = re.search(r"(?i)(item\s*1a\.*\s*risk\s*factors|item\s*2\.)", text)
    if not start_match:
        return None
    start = start_match.end()
    end = end_match.start() if end_match else len(text)
    return text[start:end].strip()

def extract_business_summary_html(path):
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    start_tag = None
    for tag in soup.find_all(text=re.compile(r"ITEM\s*1\.\s*BUSINESS", re.I)):
        start_tag = tag.parent
        break

    if not start_tag:
        return None

    collected_text = []
    for sibling in start_tag.find_all_next():
        if re.search(r"ITEM\s*1A\.\s*RISK\s*FACTORS", sibling.get_text(" ", strip=True), re.I):
            break
        text = sibling.get_text(" ", strip=True)
        if text:
            collected_text.append(text)

    return " ".join(collected_text).strip()

def split_into_paragraphs(text, lines_per_chunk=5):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks, chunk = [], []
    for i, sent in enumerate(sentences, 1):
        chunk.append(sent.strip())
        if i % lines_per_chunk == 0:
            chunks.append(" ".join(chunk))
            chunk = []
    if chunk:
        chunks.append(" ".join(chunk))
    return chunks

def main():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for fname in os.listdir(INPUT_FOLDER):
            path = os.path.join(INPUT_FOLDER, fname)
            summary = None

            if fname.lower().endswith(".pdf"):
                text = extract_text_from_pdf(path)
                summary = extract_business_summary_pdf(text)
            elif fname.lower().endswith((".html", ".htm")):
                summary = extract_business_summary_html(path)
            else:
                continue

            if not summary:
                print(f"[!] No Business Summary found in {fname}")
                continue

            paragraphs = split_into_paragraphs(summary, lines_per_chunk=5)

            for i, para in enumerate(paragraphs, 1):
                line = f"{fname}|{i}|{para}\n"
                out.write(line)

            print(f"[+] Processed {fname} ({len(paragraphs)} chunks). Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
