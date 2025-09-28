import csv
from openai import OpenAI

INPUT_FILE = "dataset_creation/paragraphs.txt"
OUTPUT_FILE = "dataset_creation/dataset.csv"

GUIDELINES = """
You are an expert financial analyst.
Your task is to assign a Digital Finance Adoption Score to company report text.
Use the following guidelines to score between 0.0 (no adoption) and 1.0 (heavy adoption).

Scoring anchors:
- 0.0 = No mention of digital finance
- 0.2 = Vague or aspirational
- 0.4 = General mentions without detail
- 0.6 = Moderate adoption with examples
- 0.8 = Strong adoption with multiple concrete initiatives
- 1.0 = Heavy emphasis with measurable outcomes

Keyword weighting:
- Strong (0.6–1.0): fintech, e-wallet, mobile wallet, QR payments, blockchain, digital-only bank, open banking
- Moderate (0.3–0.6): online banking, mobile app, internet banking, digital payments, contactless payments
- Weak (0.1–0.3): digital transformation, innovation, technology adoption (not finance-specific)

Context adjustments:
+0.2 if numbers/metrics included
-0.2 if purely marketing fluff
Return ONLY a numeric score between 0.0 and 1.0.
"""

# Pass API key directly OR rely on environment variable
client = OpenAI(api_key="")

def score_paragraph(text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": GUIDELINES},
            {"role": "user", "content": f"Text: {text}"}
        ],
        max_tokens=5
    )
    score = response.choices[0].message.content.strip()
    try:
        return float(score)
    except:
        return None

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f, \
         open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        writer.writerow(["company", "paragraph_id", "text", "score"])

        for line in f:
            parts = line.strip().split("|", 2)
            if len(parts) != 3:
                continue
            company, para_id, text = parts

            score = score_paragraph(text)
            writer.writerow([company, para_id, text, score])
            print(f"[+] {company}-{para_id}: {score}")

if __name__ == "__main__":
    main()

