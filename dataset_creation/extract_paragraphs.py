import os
import re
import fitz  # PyMuPDF for PDFs
from bs4 import BeautifulSoup

# -------- CONFIG --------
INPUT_FOLDER = "/Users/saayella/Documents/GitHub/Digital_Finance_Greenwashing/company_sorted"
OUTPUT_FILE = "dataset_creation/paragraphs.txt"
LINES_PER_CHUNK = 5
MAX_CHARS_PER_CHUNK = 2000
FAILED_FILE = "dataset_creation/failed_item1.txt"


def normalize_text(t: str) -> str:
    """Normalize whitespace and NBSPs."""
    if not t:
        return ""
    t = t.replace("\u00A0", " ")  # NBSP -> space
    t = re.sub(r"\s+", " ", t)
    return t.strip()


# -------- LOADERS --------
def extract_text_from_pdf(path: str) -> str:
    try:
        doc = fitz.open(path)
        text = "".join(page.get_text("text") for page in doc)
        return normalize_text(text)
    except Exception as e:
        print(f"[!] PDF read error {path}: {e}")
        return ""


def extract_text_from_html_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()
        text = soup.get_text(separator=" ")
        return normalize_text(text)
    except Exception as e:
        print(f"[!] HTML read error {path}: {e}")
        return ""


def read_txt(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return normalize_text(f.read())
    except Exception as e:
        print(f"[!] TXT read error {path}: {e}")
        return ""


# -------- ITEM 1 EXTRACTOR --------
def extract_item_1_section(text: str) -> str | None:
    """
    Extract section between ITEM 1 (Business) and earliest of ITEM 1A/1B/2.
    Avoids TOC by picking the longest plausible slice.
    """
    if not text:
        return None

    # Flexible regex: handles ITEM 1. BUSINESS / ITEM 1 – BUSINESS / ITEM 1 BUSINESS
    start_pattern = re.compile(r"ITEM\s*1\s*(?:[.:–-]\s*)?BUSINESS", re.IGNORECASE)
    fallback_pattern = re.compile(r"ITEM\s*1\b", re.IGNORECASE)

    end_patterns = [
        re.compile(r"ITEM\s*1A", re.IGNORECASE),
        re.compile(r"ITEM\s*1B", re.IGNORECASE),
        re.compile(r"ITEM\s*2", re.IGNORECASE),
        re.compile(r"RISK\s*FACTORS", re.IGNORECASE),
    ]

    starts = list(start_pattern.finditer(text))
    if not starts:
        starts = list(fallback_pattern.finditer(text))

    if not starts:
        return None

    best_slice = ""
    best_len = 0

    for m in starts:
        s = m.end()

        end_positions = []
        for ep in end_patterns:
            e_match = ep.search(text, s)
            if e_match:
                end_positions.append(e_match.start())

        e = min(end_positions) if end_positions else len(text)
        snippet = text[s:e].strip()

        if len(snippet) < 200:  # too short, likely TOC
            continue

        if len(snippet) > best_len:
            best_slice = snippet
            best_len = len(snippet)

    return best_slice if best_slice else None


# -------- CHUNKING --------
def split_into_paragraphs(text: str, lines_per_chunk: int = LINES_PER_CHUNK, max_chars: int = MAX_CHARS_PER_CHUNK):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks, chunk = [], []
    cur_len = 0
    for i, s in enumerate(sentences, 1):
        s = s.strip()
        if not s:
            continue
        chunk.append(s)
        cur_len += len(s) + 1
        if i % lines_per_chunk == 0 or cur_len >= max_chars:
            chunks.append(" ".join(chunk))
            chunk, cur_len = [], 0
    if chunk:
        chunks.append(" ".join(chunk))
    return chunks


def main():
    total_files = 0
    found = 0

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # open failed log in append mode (so we don't overwrite every run)
    failed_log = open(FAILED_FILE, "w", encoding="utf-8")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for root, _, files in os.walk(INPUT_FOLDER):
            for fname in files:
                path = os.path.join(root, fname)
                lower = fname.lower()

                if lower.endswith(".pdf"):
                    text = extract_text_from_pdf(path)
                elif lower.endswith((".html", ".htm")):
                    text = extract_text_from_html_file(path)
                elif lower.endswith(".txt"):
                    text = read_txt(path)
                else:
                    continue

                total_files += 1
                section = extract_item_1_section(text)
                if not section:
                    print(f"[!] ITEM 1 not found or too short: {fname}")
                    failed_log.write(fname + "\n")
                    continue

                paragraphs = split_into_paragraphs(section)
                if not paragraphs:
                    print(f"[!] No paragraphs after split: {fname}")
                    failed_log.write(fname + "\n")
                    continue

                for i, para in enumerate(paragraphs, 1):
                    out.write(f"{fname}|{i}|{para}\n")

                found += 1
                print(f"[+] Processed {fname} ({len(paragraphs)} chunks). Saved to {OUTPUT_FILE}")

    failed_log.close()
    print(f"\nDone. Files scanned: {total_files} | Item 1 found: {found}")
    print(f"Failed files list saved to: {FAILED_FILE}")



if __name__ == "__main__":
    main()
