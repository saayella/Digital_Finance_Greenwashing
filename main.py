# main.py
import sys
from extract_pdf import extract_plain_text
from finbertaverage import score_document, lexicon_tokens

def run_pipeline(pdf_path: str):
    print(f"[INFO] Processing {pdf_path}")

    # Step 1: Extract text from PDF
    text = extract_plain_text(pdf_path)
    print(f"[INFO] Extracted {len(text)} characters of text")

    # Step 2: Score document
    doc_score, details = score_document(text, lexicon_tokens)
    print(f"[INFO] Digital Finance Adoption Score: {doc_score:.2f}/100")

    return doc_score, details

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <pdf_file>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    run_pipeline(pdf_path)
