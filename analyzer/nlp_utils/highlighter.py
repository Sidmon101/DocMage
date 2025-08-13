# nlp_utils/highlighter.py
import re
from collections import defaultdict, Counter
import spacy
from spacy.matcher import PhraseMatcher

# Load spaCy model globally
nlp = spacy.load("en_core_web_sm")

CATEGORY_LABELS = {
    "medical": {
        "Conditions": [
            "diabetes", "type 1 diabetes", "type i diabetes", "type 2 diabetes", "type ii diabetes",
            "gestational diabetes", "prediabetes",
            "hypertension", "high blood pressure",
            "cancer", "carcinoma", "sarcoma", "leukemia", "lymphoma", "melanoma",
            "stroke", "cerebrovascular accident", "cva", "tia", "transient ischemic attack",
            "asthma", "copd", "chronic obstructive pulmonary disease", "emphysema", "chronic bronchitis",
            "pneumonia", "tuberculosis", "tb", "influenza", "flu",
            "arthritis", "osteoarthritis", "rheumatoid arthritis", "gout", "psoriatic arthritis",
            "heart attack", "myocardial infarction", "mi", "coronary artery disease", "cad", "angina",
            "heart failure", "congestive heart failure", "chf",
            "kidney failure", "renal failure", "ckd", "chronic kidney disease", "aki", "acute kidney injury",
            "liver disease", "cirrhosis", "hepatitis", "fatty liver", "nafld", "nash",
            "hiv", "aids", "viral load suppression",
            "covid-19", "covid", "sars-cov-2", "long covid", "post-acute sequelae",
            "thyroid disorder", "hypothyroidism", "hyperthyroidism", "graves disease", "hashimoto thyroiditis",
            "dyslipidemia", "hyperlipidemia", "high cholesterol", "hypertriglyceridemia",
            "anemia", "iron deficiency", "b12 deficiency", "folate deficiency",
            "depression", "major depressive disorder", "mdd", "anxiety", "panic disorder", "bipolar disorder",
            "schizophrenia", "adhd", "autism spectrum disorder",
            "migraine", "tension headache", "cluster headache",
            "peptic ulcer", "gerd", "gastroesophageal reflux disease", "gastritis", "ibs", "inflammatory bowel disease", "crohn disease", "ulcerative colitis",
            "osteoporosis", "osteopenia",
            "dermatitis", "eczema", "psoriasis", "urticaria", "hives",
            "sepsis", "bacteremia", "cellulitis",
            "pregnancy", "preeclampsia", "gestational hypertension",
            "obesity", "overweight", "malnutrition",
            "sleep apnea", "osa",
            "arrhythmia", "atrial fibrillation", "afib", "ventricular tachycardia",
            "pulmonary embolism", "pe", "deep vein thrombosis", "dvt",
            "cystic fibrosis", "sickle cell disease", "thalassemia",
            "parkinson disease", "alzheimer disease", "dementia", "epilepsy", "seizure disorder"
        ],
        "Medications": [
            # Analgesics/antipyretics/NSAIDs
            "paracetamol", "acetaminophen", "ibuprofen", "naproxen", "diclofenac", "aspirin",
            "tramadol", "morphine", "oxycodone", "codeine",
            # Antidiabetics
            "insulin", "metformin", "glipizide", "glyburide", "gliclazide", "glimepiride",
            "sitagliptin", "linagliptin", "empagliflozin", "dapagliflozin", "canagliflozin",
            "liraglutide", "semaglutide", "dulaglutide",
            # Antihypertensives
            "lisinopril", "enalapril", "ramipril", "perindopril",
            "losartan", "valsartan", "telmisartan", "olmesartan",
            "amlodipine", "nifedipine", "diltiazem", "verapamil",
            "atenolol", "metoprolol", "propranolol", "bisoprolol",
            "hydrochlorothiazide", "hctz", "chlorthalidone", "furosemide", "spironolactone",
            # Lipids
            "atorvastatin", "simvastatin", "rosuvastatin", "pravastatin", "ezetimibe",
            # GI
            "omeprazole", "pantoprazole", "esomeprazole", "rabeprazole", "lansoprazole",
            "ranitidine", "famotidine", "ondansetron", "domperidone", "metoclopramide",
            # Respiratory
            "albuterol", "salbutamol", "levalbuterol", "ipratropium", "tiotropium",
            "budesonide", "fluticasone", "formoterol", "salmeterol", "montelukast",
            # Anti-infectives
            "amoxicillin", "amoxicillin-clavulanate", "augmentin", "ampicillin",
            "azithromycin", "clarithromycin", "erythromycin",
            "ciprofloxacin", "levofloxacin", "moxifloxacin",
            "doxycycline", "tetracycline",
            "ceftriaxone", "cefixime", "cephalexin",
            "piperacillin-tazobactam", "vancomycin", "linezolid", "meropenem",
            "oseltamivir", "acyclovir", "valacyclovir", "remdesivir",
            # Anticoagulants/antiplatelets
            "warfarin", "heparin", "enoxaparin", "apixaban", "rivaroxaban", "dabigatran",
            "clopidogrel", "prasugrel", "ticagrelor",
            # Steroids/immunomodulators
            "prednisone", "prednisolone", "methylprednisolone", "dexamethasone",
            "methotrexate", "azathioprine", "hydroxychloroquine",
            # Others
            "levothyroxine", "calcitriol", "vitamin d", "cyanocobalamin", "folic acid",
            "sertraline", "fluoxetine", "escitalopram", "venlafaxine", "amitriptyline"
        ],
        "Procedures": [
            "surgery", "minor surgery", "major surgery",
            "angioplasty", "stent placement", "catheterization", "cabg", "bypass surgery",
            "mri", "magnetic resonance imaging",
            "ct scan", "computed tomography", "pet scan", "pet-ct",
            "x-ray", "x ray", "ultrasound", "sonography", "echo", "echocardiogram", "ecg", "ekg",
            "biopsy", "fine needle aspiration", "fna", "core biopsy",
            "chemotherapy", "radiation therapy", "radiotherapy", "immunotherapy",
            "dialysis", "hemodialysis", "peritoneal dialysis",
            "endoscopy", "colonoscopy", "sigmoidoscopy", "egd", "gastroscopy", "bronchoscopy",
            "laparoscopy", "arthroscopy", "hysteroscopy",
            "transplant", "kidney transplant", "liver transplant", "bone marrow transplant",
            "lumbar puncture", "spinal tap", "thoracentesis", "paracentesis",
            "cesarean section", "c-section", "hysterectomy", "appendectomy", "cholecystectomy",
            "vaccination", "immunization", "wound debridement", "suturing", "intubation", "ventilation"
        ],
        "Lab Terms": [
            "hemoglobin", "hgb", "hba1c", "a1c", "hematocrit", "hct",
            "cholesterol", "ldl", "hdl", "triglycerides",
            "blood sugar", "fasting glucose", "random glucose", "ogtt",
            "platelet count", "platelets", "wbc", "white blood cell", "rbc", "red blood cell",
            "creatinine", "bun", "urea", "egfr", "gfr",
            "alt", "sgpt", "ast", "sgot", "alp", "ggt", "bilirubin", "albumin",
            "crp", "esr", "d-dimer", "ferritin", "procalcitonin", "lactate",
            "inr", "pt", "prothrombin time", "aptt", "tsh", "t3", "t4",
            "troponin", "bnp", "nt-probnp",
            "urinalysis", "urine culture", "blood culture",
            "chest x-ray", "ct chest", "mri brain"
        ],
        "Document Types": [
            "prescription", "rx", "medication order",
            "discharge summary", "discharge note",
            "lab report", "pathology report", "imaging report", "radiology report",
            "medical certificate", "fitness certificate",
            "operative report", "procedure note",
            "admission note", "progress note", "nursing note", "consultation note",
            "referral letter", "consent form",
            "vaccination record", "immunization card",
            "case sheet", "clinical summary",
            "death summary", "autopsy report",
            "billing statement", "insurance claim", "prior authorization"
        ],
        "Symptoms": [
            "fever", "pyrexia", "chills", "rigors",
            "cough", "sputum", "shortness of breath", "dyspnea", "wheezing",
            "chest pain", "palpitation",
            "headache", "dizziness", "syncope",
            "nausea", "vomiting", "diarrhea", "constipation", "abdominal pain",
            "fatigue", "weakness", "malaise", "myalgia", "arthralgia",
            "rash", "itching", "pruritus", "swelling", "edema",
            "dysuria", "frequency", "urgency", "hematuria",
            "weight loss", "loss of appetite", "anorexia"
        ],
        "Vitals": [
            "blood pressure", "bp", "heart rate", "pulse",
            "respiratory rate", "rr", "temperature", "oxygen saturation", "spo2",
            "height", "weight", "bmi", "body mass index"
        ],
        "Devices": [
            "pacemaker", "defibrillator", "ventilator", "nebulizer", "cpap", "bipap",
            "insulin pump", "glucometer", "oxygen concentrator", "catheter", "stent"
        ]
    },

    "legal": {
        "Document Types": [
            "contract", "agreement", "master services agreement", "msa",
            "statement of work", "sow", "purchase agreement", "sale agreement",
            "affidavit", "deposition transcript",
            "lease", "rental agreement", "tenancy agreement",
            "nda", "non-disclosure agreement", "confidentiality agreement",
            "mou", "memorandum of understanding", "term sheet", "letter of intent", "loi",
            "power of attorney", "poa",
            "will", "last will and testament", "codicil", "trust deed",
            "deed", "sale deed", "gift deed", "mortgage deed", "assignment deed",
            "settlement", "settlement agreement", "release", "waiver",
            "memorandum", "minutes of meeting", "board resolution", "bylaws",
            "articles of association", "articles of incorporation", "certificate of incorporation",
            "employment agreement", "offer letter", "separation agreement",
            "privacy policy", "terms of service", "cookie policy",
            "license", "licence", "sub-licence", "franchise agreement",
            "service level agreement", "sla", "data processing agreement", "dpa",
            "notice", "legal notice", "cease and desist",
            "complaint", "petition", "plaint", "summons", "subpoena", "writ",
            "motion", "brief", "reply", "rejoinder",
            "order", "interim order", "injunction", "judgment", "decree", "consent order",
            "legal opinion", "due diligence report", "opinion letter",
            "addendum", "amendment", "appendix", "annexure", "schedule", "rider"
        ],
        "Parties": [
            "plaintiff", "defendant", "claimant", "respondent", "petitioner", "appellant", "appellee",
            "lessor", "lessee", "landlord", "tenant",
            "licensor", "licensee", "assignor", "assignee",
            "buyer", "purchaser", "seller", "vendor", "supplier", "customer", "client",
            "guarantor", "surety", "indemnitor", "indemnitee",
            "witness", "counsel", "attorney", "advocate", "barrister", "solicitor",
            "agent", "principal", "shareholder", "director", "officer", "trustee", "beneficiary"
        ],
        "Clauses": [
            "termination", "termination for convenience", "termination for cause",
            "confidentiality", "non-disclosure",
            "liability", "limitation of liability", "cap on liability",
            "arbitration", "mediation", "dispute resolution",
            "indemnity", "indemnification", "defense and hold harmless",
            "force majeure",
            "jurisdiction", "venue", "governing law", "choice of law",
            "assignment", "subcontracting", "change of control",
            "notice", "notices",
            "payment terms", "fees", "invoicing", "taxes",
            "warranty", "representations and warranties",
            "intellectual property", "ip ownership", "license grant",
            "privacy", "data protection", "data security", "conflict of interest",
            "non-compete", "non-solicitation", "non-poaching",
            "audit rights", "records retention",
            "severability", "waiver", "entire agreement", "amendment", "counterparts",
            "injunctive relief", "specific performance",
            "compliance with laws", "anti-bribery", "anti-corruption", "sanctions"
        ],
        "Deadlines": [
            "effective date", "commencement date", "start date",
            "closing date", "completion date", "delivery date",
            "expiry date", "expiration date", "end date", "renewal date", "auto-renewal",
            "termination date",
            "notice period", "cure period", "grace period", "response deadline",
            "statute of limitations", "hearing date", "filing deadline"
        ],
        "Court & Procedure": [
            "case number", "docket", "cause of action", "prayer", "relief sought",
            "precedent", "ratio decidendi", "obiter dicta",
            "burden of proof", "standard of proof",
            "evidence", "exhibit", "discovery", "interrogatories", "subpoena duces tecum",
            "decree", "order", "judgment", "consent decree", "appeal", "remand"
        ],
        "Remedies & Damages": [
            "damages", "compensatory damages", "consequential damages", "liquidated damages",
            "punitive damages", "statutory damages",
            "injunction", "specific performance", "rescission", "restitution"
        ],
        "IP & Tech": [
            "patent", "trademark", "copyright", "trade secret",
            "infringement", "license", "royalty", "assignment", "field of use",
            "open source", "oss", "copyleft", "gpl", "mit license"
        ]
    },

    "financial": {
        "Transaction Terms": [
            "investment", "loan", "credit", "debit", "payment", "payout", "remittance",
            "invoice", "bill", "purchase order", "po", "sales order", "so",
            "receipt", "voucher", "credit note", "debit note",
            "wire transfer", "swift", "neft", "rtgs", "ach", "sepa", "upi",
            "direct debit", "standing order", "escrow", "lien", "collateral",
            "equity", "debt", "bond", "note", "commercial paper", "t-bill",
            "dividend", "coupon", "interest", "principal", "amortization",
            "hedge", "forward", "future", "option", "swap", "derivative",
            "ipo", "follow-on offering", "buyback", "rights issue", "bonus issue",
            "reconciliation", "chargeback", "write-off", "provision", "impairment"
        ],
        "Metrics": [
            "revenue", "sales", "turnover", "expenditure", "operating expense", "opex",
            "capital expenditure", "capex", "profit", "loss",
            "gross margin", "operating margin", "net margin",
            "ebit", "ebitda", "ebita", "net income", "net profit",
            "roi", "roa", "roe", "roc", "roce",
            "eps", "pe ratio", "price to earnings", "book value", "market cap",
            "free cash flow", "fcf", "cash flow", "operating cash flow",
            "working capital", "current ratio", "quick ratio",
            "inventory turnover", "days sales outstanding", "dso",
            "days payables outstanding", "dpo", "days inventory outstanding", "dio",
            "arr", "mrr", "ltv", "cac", "burn rate", "runway"
        ],
        "Compliance": [
            "audit", "internal audit", "external audit", "statutory audit",
            "tax", "withholding tax", "sales tax", "vat", "gst",
            "regulation", "compliance", "kyc", "aml", "cft", "sanctions screening",
            "ifrs", "gaap", "ias", "asc 606", "asc 842",
            "sarbanes-oxley", "sox", "basel iii", "mifid ii",
            "pci dss", "gdpr", "fatca", "ccpa"
        ],
        "Statements & Ledgers": [
            "balance sheet", "statement of financial position",
            "income statement", "profit and loss", "p&l",
            "cash flow statement", "statement of cash flows",
            "statement of changes in equity",
            "trial balance", "general ledger", "gl", "subledger", "journal entry", "chart of accounts"
        ],
        "Instruments": [
            "equity", "preference shares", "preferred stock", "common stock",
            "bond", "debenture", "convertible note", "safe", "warrant",
            "etf", "mutual fund", "reit", "certificate of deposit", "cd",
            "fx", "foreign exchange", "currency swap"
        ],
        "Currencies & Units": [
            "usd", "eur", "gbp", "inr", "jpy", "cny", "cad", "aud", "chf", "sgd",
            "$", "€", "£", "₹", "¥",
            "percent", "%", "basis points", "bps"
        ],
        "Accounting Terms": [
            "accrual", "deferral", "depreciation", "amortization",
            "goodwill", "impairment", "intangible asset", "ppe", "inventory",
            "revenue recognition", "matching principle", "materiality", "conservatism",
            "contingent liability", "provision", "lease liability", "right-of-use asset",
            "prepaid expense", "accounts receivable", "accounts payable", "deferred revenue"
        ],
        "Tax Documents": [
            "tax invoice", "credit memo", "debit memo",
            "form w-9", "form 1099", "form w-8ben", "form 1040",
            "pan", "tan", "gstin", "hsn code", "sac code"
        ],
        "Payment Details": [
            "iban", "swift bic", "routing number", "ifsc", "upi id", "bank account number",
            "check", "cheque", "draft", "neft utr", "rtgs utr", "ach trace"
        ]
    }
}


# ---------- Helpers ----------

def _normalize_key(key: str) -> str:
    return key.replace(" ", "_")

def _unique_preserve_order(items):
    seen = set()
    out = []
    for it in items:
        k = it.strip()
        if not k:
            continue
        if k.lower() not in seen:
            out.append(k)
            seen.add(k.lower())
    return out

def clean_highlights(highlights: dict) -> dict:
    """Normalize keys and join list values into displayable strings."""
    cleaned = {}
    for key, value in highlights.items():
        safe_key = _normalize_key(key)
        if isinstance(value, list):
            cleaned[safe_key] = ", ".join(_unique_preserve_order(value))
        else:
            cleaned[safe_key] = str(value).strip()
    # Drop empties
    return {k: v for k, v in cleaned.items() if v}

# ---------- Build PhraseMatchers per category (global) ----------

_MATCHERS = {}

def _build_matcher(category: str):
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    labels = CATEGORY_LABELS.get(category, {})
    for subcat, keywords in labels.items():
        # Make robust to hyphen vs space (e.g., x-ray / x ray)
        patterns = []
        for kw in keywords:
            patterns.append(nlp.make_doc(kw))
            if "-" in kw:
                patterns.append(nlp.make_doc(kw.replace("-", " ")))
            if " " in kw:
                patterns.append(nlp.make_doc(kw.replace(" ", "-")))
        matcher.add(subcat, patterns)
    return matcher

def _get_matcher(category: str):
    if category not in _MATCHERS and category in CATEGORY_LABELS:
        _MATCHERS[category] = _build_matcher(category)
    return _MATCHERS.get(category)

# ---------- Main extraction ----------

# Pre-compiled regexes
DURATION_RE = re.compile(r"\b\d+\s+(?:day|days|week|weeks|month|months|year|years)\b", re.I)

DOSAGE_RE = re.compile(r"\b\d+(?:\.\d+)?\s?(?:mg|mcg|µg|ml|g|units)\b", re.I)
VITALS_RE = re.compile(
    r"(?:BP[:\s]?\d{2,3}/\d{2,3}\s?(?:mmHg)?)|"
    r"(?:HR[:\s]?\d{2,3}\s?bpm)|"
    r"(?:Temp(?:erature)?[:\s]?\d{2,3}(?:\.\d+)?\s?(?:°C|°F|C|F))|"
    r"(?:SpO2[:\s]?\d{2,3}\s?%)",
    re.I,
)

# Date strings like "Jan 2, 2024" | "2 Jan 2024" | "2024-01-02" | "02/01/2024"
DATE_VALUE_RE = r"([A-Za-z]{3,9}\s\d{1,2},\s?\d{4}|\d{1,2}\s[A-Za-z]{3,9}\s\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})"
EFFECTIVE_RE = re.compile(rf"(Effective|Commencement)\s+Date[:\s]+{DATE_VALUE_RE}", re.I)
EXPIRY_RE = re.compile(rf"(Expiry|Expiration|Termination)\s+Date[:\s]+{DATE_VALUE_RE}", re.I)

MONEY_RE = re.compile(
    r"(?:(?:USD|INR|EUR|GBP|AUD|CAD)\s*)?[$₹€£]?\s?\d{1,3}(?:,\d{3})*(?:\.\d+)?\s?(?:million|billion|mn|bn|cr|crore|lakh|k|m|b)?",
    re.I,
)
PERCENT_RE = re.compile(r"\b\d+(?:\.\d+)?\s?%\b")

def extract_highlights(text: str, category: str = "general") -> dict:
    doc = nlp(text)
    highlights = defaultdict(list)

    # ---- Named Entities (broaden coverage) ----
    for ent in doc.ents:
        if ent.label_ in {"ORG"}:
            highlights["Company"].append(ent.text)
        elif ent.label_ in {"PERSON"}:
            highlights["Person"].append(ent.text)
        elif ent.label_ in {"GPE", "LOC"}:
            highlights["Location"].append(ent.text)
        elif ent.label_ in {"LAW"}:
            highlights["Law_Reference"].append(ent.text)
        elif ent.label_ in {"NORP"}:
            highlights["Groups"].append(ent.text)
        elif ent.label_ in {"MONEY"}:
            highlights["Money"].append(ent.text)
        elif ent.label_ in {"DATE"}:
            highlights["Dates"].append(ent.text)
        elif ent.label_ in {"PERCENT"}:
            highlights["Percentages"].append(ent.text)

    # ---- Duration ----
    highlights["Duration"].extend(DURATION_RE.findall(text))

    # ---- Category-specific PhraseMatcher ----
    matcher = _get_matcher(category)
    if matcher:
        seen_spans = defaultdict(set)
        for match_id, start, end in matcher(doc):
            subcat = nlp.vocab.strings[match_id]
            span_text = doc[start:end].text
            if span_text.lower() not in seen_spans[subcat]:
                highlights[subcat].append(span_text)
                seen_spans[subcat].add(span_text.lower())

    # ---- Category extras ----
    if category == "medical":
        # Dosage
        highlights["Dosage"].extend(DOSAGE_RE.findall(text))
        # Vitals
        vitals = VITALS_RE.findall(text)
        if vitals:
            # regex returns tuples because of groups; flatten to strings
            flat_vitals = []
            for v in vitals:
                if isinstance(v, tuple):
                    # first non-empty part
                    joined = " ".join([p for p in v if p])
                    if joined:
                        flat_vitals.append(joined)
                elif v:
                    flat_vitals.append(v)
            highlights["Vitals"].extend(_unique_preserve_order(flat_vitals))

    if category == "legal":
        eff = EFFECTIVE_RE.findall(text)
        exp = EXPIRY_RE.findall(text)
        if eff:
            # eff is list of tuples like [('Effective', 'Jan 2, 2024')]
            highlights["Effective_Date"].extend(_unique_preserve_order([e[-1] for e in eff]))
        if exp:
            highlights["Expiry_Date"].extend(_unique_preserve_order([e[-1] for e in exp]))
        # Clause headings heuristic (captures lines with clause names)
        clause_keywords = CATEGORY_LABELS["legal"].get("Clauses", [])
        clause_re = re.compile(rf"^\s*(?:{'|'.join(map(re.escape, clause_keywords))})\b.*$", re.I | re.M)
        clauses_found = clause_re.findall(text)
        if clauses_found:
            highlights["Clauses"].extend(_unique_preserve_order(clauses_found))

    if category == "financial":
        # Revenue/Expenditure lines with amounts
        revenue_lines = re.findall(rf"\b(revenue)\b[:\s\-]*{MONEY_RE.pattern}", text, re.I)
        expenditure_lines = re.findall(rf"\b(expenditure|expenses)\b[:\s\-]*{MONEY_RE.pattern}", text, re.I)
        # Raw money and percents
        money_vals = MONEY_RE.findall(text)
        percent_vals = PERCENT_RE.findall(text)

        if revenue_lines:
            # revenue_lines is list of tuples from the group; reconstruct line values separately
            revenues = re.findall(rf"\brevenue\b[:\s\-]*({MONEY_RE.pattern})", text, re.I)
            if revenues:
                highlights["Revenue"].extend(_unique_preserve_order(revenues))
        if expenditure_lines:
            expenses = re.findall(rf"\b(?:expenditure|expenses)\b[:\s\-]*({MONEY_RE.pattern})", text, re.I)
            if expenses:
                highlights["Expenditure"].extend(_unique_preserve_order(expenses))
        if money_vals:
            # MONEY_RE with groups may return the unit part; capture full money via a second pass
            money_full = re.findall(rf"({MONEY_RE.pattern})", text, re.I)
            highlights["Money"].extend(_unique_preserve_order(money_full))
        if percent_vals:
            percent_full = re.findall(r"(\b\d+(?:\.\d+)?\s?%\b)", text)
            highlights["Percentages"].extend(_unique_preserve_order(percent_full))

    # ---- General fallback keywords (noun chunks + tokens) ----
    if category == "general":
        tokens = [t.lemma_.lower() for t in doc if t.is_alpha and not t.is_stop]
        chunks = [nc.text.lower() for nc in doc.noun_chunks if nc.text.strip()]
        counts = Counter(tokens + chunks)
        top_keywords = [w for w, _ in counts.most_common(10)]
        highlights["Top_Keywords"].extend(top_keywords)

    # De-duplicate and clean
    for k in list(highlights.keys()):
        highlights[k] = _unique_preserve_order(highlights[k])

    return clean_highlights(dict(highlights))
