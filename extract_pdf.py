import os
import argparse

try:
    import fitz 
except Exception as e:
    raise SystemExit("PyMuPDF (fitz) is required. Install with: pip install pymupdf") from e


def extract_plain_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    parts = []
    for pno in range(len(doc)):
        page = doc.load_page(pno)
        parts.append(page.get_text("text"))  # plain reading-order text
    return "\n".join(parts).strip()


def main():
    ap = argparse.ArgumentParser(description="Plain text extraction from PDFs using PyMuPDF (no OCR/heading/sectioning)." )
    ap.add_argument("input", help="Path to a PDF file or a directory containing PDFs")
    ap.add_argument("-o", "--out", default="out_text", help="Output directory (default: out_text)")
    args = ap.parse_args()

    in_path = args.input
    out_dir = args.out
    os.makedirs(out_dir, exist_ok=True)

    inputs = []
    if os.path.isdir(in_path):
        for fn in sorted(os.listdir(in_path)):
            if fn.lower().endswith(".pdf"):
                inputs.append(os.path.join(in_path, fn))
    else:
        inputs.append(in_path)

    for pdf in inputs:
        if not os.path.exists(pdf):
            print(f"[WARN] Missing file: {pdf}")
            continue
        base = os.path.splitext(os.path.basename(pdf))[0]
        out_txt = os.path.join(out_dir, f"{base}.txt")
        try:
            text = extract_plain_text(pdf)
            with open(out_txt, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"[OK] {pdf} -> {out_txt}")
        except Exception as e:
            print(f"[ERROR] {pdf}: {e}")


if __name__ == "__main__":
    main()
