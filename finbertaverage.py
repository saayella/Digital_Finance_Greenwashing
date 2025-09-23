import re
import nltk
nltk.download("punkt_tab")
from nltk.tokenize import sent_tokenize, word_tokenize
nltk.download("punkt")

# --- Step 1: Define lexicon ---
digital_finance_lexicon = [
     # Core terms
    "digital finance", "fintech", "financial technology", "digital banking", "neo-bank",
    "online banking", "mobile banking", "internet banking", "e-banking", "virtual bank",
    "challenger bank", "open banking", "embedded finance", "banking-as-a-service",
    "digital wallet", "e-wallet", "mobile wallet", "virtual wallet",
    "digital payment", "mobile payment", "contactless payment", "qr code payment",
    "online payment", "peer-to-peer payment", "p2p lending", "digital lending",
    "crowdfunding", "crowdlending", "microfinance platform",
    "blockchain", "distributed ledger", "dlt", "cryptocurrency",
    "bitcoin", "ethereum", "stablecoin", "central bank digital currency", "cbdc",
    "tokenization", "smart contracts", "decentralized finance", "defi",
    "robo-advisor", "digital wealth management", "automated investment",
    "algorithmic trading", "high-frequency trading", "digital brokerage",
    "insurtech", "digital insurance", "parametric insurance",
    "regtech", "regulatory technology", "suptech", "supervisory technology",
    "digital identity", "e-kyc", "electronic know your customer", "digital onboarding",
    "biometric authentication", "two-factor authentication",
    "cybersecurity", "fraud detection", "anti-money laundering", "aml",
    "know your customer", "kyc", "transaction monitoring",
    "digital remittance", "cross-border payment", "instant payment",
    "buy now pay later", "bnpl", "digital credit", "virtual credit card",
    "open api", "api banking", "api integration", "cloud banking",
    "artificial intelligence", "machine learning", "natural language processing",
    "chatbot", "conversational banking",
    "digital financial inclusion", "financial inclusion platform",
    "digital microfinance", "agent banking",
    "big data analytics", "predictive analytics", "real-time analytics",
    "token economy", "digital asset", "digital securities",
    "robo-underwriting", "digital mortgage", "online loan application",
    "virtual advisory", "remote financial advisory",
    "instant settlement", "real-time gross settlement", "rtgs",
    "payment gateway", "merchant acquiring", "digital point-of-sale", "pos system",
    "digital ecosystem", "super app", "platform banking", "software-as-a-service", "saas",
    "banking-as-a-service", "b2b fintech", "b2c fintech", "b2b2c fintech",
    "fintech partnership", "fintech collaboration", "fintech innovation", "digital transformation",
    "financial cloud", "cloud computing", "edge computing", "5g banking",
    "quantum computing", "quantum-safe encryption", "digital twin",
    "sustainable finance", "green fintech", "esg investing", "environmental social governance",
    "digital reporting", "xbrl", "e-invoicing", "digital audit", "continuous auditing",
    "digital tax", "e-tax filing", "digital compliance", "regtech solution",
    "digital currency exchange", "crypto exchange", "decentralized exchange", "dex",
    "non-fungible token", "nft", "nft marketplace", "digital collectible",
    "digital rights management", "drm", "smart property", "digital contract",
    "digital trust", "digital notary", "e-notary", "digital signature", "e-signature",
    "digital banking platform", "core banking system", "software solutions"
]

# Normalize lexicon (lowercase, handle multiwords)
lexicon_tokens = [term.lower().split() for term in digital_finance_lexicon]

# --- Step 2: Scoring function ---
def score_sentence(sentence, lexicon):
    words = word_tokenize(sentence.lower())
    total_words = len(words)-1
    if total_words == 0:
        return 0.0

    match_count = 0
    # unigram/bigram matching
    for tokens in lexicon:
        n = len(tokens)
        for i in range(total_words - n + 1):
            if words[i:i+n] == tokens:
                match_count += 1

    return (match_count / total_words)*50  # normalized score (0–50)

def score_document(document, lexicon):
    sentences = sent_tokenize(document)
    if not sentences:
        return 0.0

    sentence_scores = [score_sentence(sent, lexicon)*50 for sent in sentences]
    doc_score = sum(sentence_scores) / len(sentence_scores)  # mean score
    return doc_score, list(zip(sentences, sentence_scores))

def score_sentence(sentence: str, lexicon) -> float:
    """Score a single sentence based on lexicon matches."""
    words = word_tokenize(sentence.lower())
    total_words = len(words) - 1
    if total_words <= 0:
        return 0.0

    match_count = 0
    for tokens in lexicon:
        n = len(tokens)
        for i in range(total_words - n + 1):
            if words[i:i+n] == tokens:
                match_count += 1

    return (match_count / total_words) * 50  # normalize to 0–50

def score_document(document: str, lexicon):
    """Score an entire document (string of text)."""
    sentences = sent_tokenize(document)
    if not sentences:
        return 0.0, []

    sentence_scores = [score_sentence(sent, lexicon) * 2 for sent in sentences]  # scale to 100
    doc_score = sum(sentence_scores) / len(sentence_scores)
    return doc_score, list(zip(sentences, sentence_scores))

# --- Optional demo when run directly ---
if __name__ == "__main__":
    sample_doc = """
    In 2023, the bank expanded its mobile banking and digital wallet services.
    We invested heavily in blockchain technology to improve transparency.
    Our employees worked hard to deliver strong results across all divisions.
    The company launched a crowdfunding platform for SMEs to access finance.
    """
    doc_score, details = score_document(sample_doc, lexicon_tokens)
    print("Demo score:", round(doc_score, 3))
    for sent, sc in details:
        if sc > 0:
            print(f"- {sent.strip()} --> {round(sc, 3)}")