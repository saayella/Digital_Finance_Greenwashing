import os
import re
import argparse
import fitz  # PyMuPDF


IMPORTANT_SECTIONS = [
    "Item 1\\.?\\s*Business",
    "Item 1A\\.?\\s*Risk Factors",
    "Item 7\\.?\\s*Management’s Discussion and Analysis",
    "Item 7A\\.?\\s*Quantitative and Qualitative Disclosures About Market Risk",
]

END_SECTIONS = [
    "Item 8\\.?\\s*Financial Statements",  # stop at financial statements onward
    "Item 9\\.", "PART III", "Item 10"
]


def extract_plain_text(pdf_path: str) -> str:
    """Extract cleaned plain text from PDF, removing TOC and repeated item headers."""
    doc = fitz.open(pdf_path)
    text_parts = []

    for page in doc:
        page_text = page.get_text("text")

        # Remove TOC lines like "Item 1. Business ..... 1"
        page_text = re.sub(r'Item\s+\d+[A-Z]?\..{0,80}\s+\d{1,3}\s*$', '', page_text, flags=re.MULTILINE)

        # Remove page numbers and headers/footers
        page_text = re.sub(r'\n?\s*\d+\s*\n', '', page_text)
        page_text = re.sub(r'\n•\n', '', page_text)
        page_text = re.sub(r'•\n','', page_text)
        page_text = re.sub(r'PART\s+[IVXLC]+\s*', '', page_text, flags=re.IGNORECASE)

        text_parts.append(page_text)

    all_text = "\n".join(text_parts)

    # Find relevant section ranges
    relevant_chunks = []
    for pattern in IMPORTANT_SECTIONS:
        start_match = re.search(pattern, all_text, flags=re.IGNORECASE)
        if start_match:
            start = start_match.start()
            # find where to stop (next END_SECTION)
            end_positions = [re.search(e, all_text[start:], flags=re.IGNORECASE) for e in END_SECTIONS]
            valid_ends = [start + e.start() for e in end_positions if e]
            end = min(valid_ends) if valid_ends else len(all_text)
            relevant_chunks.append(all_text[start:end])

    # Merge all relevant chunks
    cleaned_text = "\n\n".join(relevant_chunks).strip()

    return cleaned_text


def main():
    ap = argparse.ArgumentParser(description="Extract relevant sections from 10-K PDF (Business, Risk Factors, MD&A).")
    ap.add_argument("input", help="Path to a PDF file or directory of PDFs")
    ap.add_argument("-o", "--out", default="out_text", help="Output directory (default: out_text)")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    if os.path.isdir(args.input):
        pdfs = [os.path.join(args.input, f) for f in sorted(os.listdir(args.input)) if f.lower().endswith(".pdf")]
    else:
        pdfs = [args.input]

    for pdf in pdfs:
        base = os.path.splitext(os.path.basename(pdf))[0]
        out_path = os.path.join(args.out, f"{base}.txt")

        try:
            cleaned = extract_plain_text(pdf)
            if not cleaned:
                print(f"[WARN] No relevant sections found in {pdf}")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            print(f"[OK] Extracted relevant sections from {pdf} -> {out_path}")
        except Exception as e:
            print(f"[ERROR] {pdf}: {e}")


if __name__ == "__main__":
    main()
