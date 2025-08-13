import spacy
import re

# Load spaCy's small English model
nlp = spacy.load("en_core_web_sm")

# Regex patterns for domain-specific entities
MONEY_RE = re.compile(r"(₹|\$|€|£)?\s?\d{1,3}(?:,\d{3})*(?:\.\d+)?\s?(million|billion|cr|lakh|k|m|bn)?", re.I)
PERCENT_RE = re.compile(r"\b\d+(?:\.\d+)?\s?%")
RATIO_RE = re.compile(r"\b(?:Debt-to-Asset Ratio|Savings Rate|Investment-to-Income Ratio|Profit Margin|ROI|EBITDA|Net Worth|Liquidity Ratio|Operating Margin|Cash Conversion Cycle|Current Ratio|Quick Ratio)\b", re.I)

CLAUSE_RE = re.compile(r"\b(?:Termination Clause|Confidentiality Clause|Liability Clause|Arbitration Clause|Indemnity Clause|Jurisdiction Clause|Force Majeure Clause|Governing Law Clause|Assignment Clause|Notice Clause)\b", re.I)
DATE_RE = re.compile(r"\b(?:Effective Date|Commencement Date|Expiry Date|Termination Date|Renewal Date)\b", re.I)

VITALS_RE = re.compile(r"\b(?:BP\s*[:\-]?\s*\d{2,3}/\d{2,3}|HR\s*[:\-]?\s*\d{2,3}\s*bpm|Temp\s*[:\-]?\s*\d{2,3}(?:\.\d+)?\s*(°C|°F)|SpO2\s*[:\-]?\s*\d{2,3}\s?%)\b", re.I)
CONDITION_RE = re.compile(r"\b(?:diabetes|hypertension|cancer|stroke|asthma|arthritis|heart attack|kidney failure|liver disease|HIV|COVID-19|pneumonia|obesity|depression|anxiety)\b", re.I)
MEDICATION_RE = re.compile(r"\b(?:aspirin|insulin|metformin|statins|antibiotics|beta-blockers|paracetamol|ibuprofen|amoxicillin|atorvastatin|omeprazole|antidepressants|antihypertensives)\b", re.I)

def extract_entities(text: str, category: str = "general"):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    # Add regex-based entities
    if category == "financial":
        entities += [(m.group(), "MONEY") for m in MONEY_RE.finditer(text)]
        entities += [(p.group(), "PERCENT") for p in PERCENT_RE.finditer(text)]
        entities += [(r.group(), "RATIO") for r in RATIO_RE.finditer(text)]

    elif category == "legal":
        entities += [(c.group(), "CLAUSE") for c in CLAUSE_RE.finditer(text)]
        entities += [(d.group(), "DATE_TERM") for d in DATE_RE.finditer(text)]

    elif category == "medical":
        entities += [(v.group(), "VITAL") for v in VITALS_RE.finditer(text)]
        entities += [(c.group(), "CONDITION") for c in CONDITION_RE.finditer(text)]
        entities += [(m.group(), "MEDICATION") for m in MEDICATION_RE.finditer(text)]

    return entities
