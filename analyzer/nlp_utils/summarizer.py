import re
import spacy
from typing import List, Dict
from datetime import datetime

# Load spaCy model globally for performance
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None  # Fallback if model is not available

# ---------------------------
# Helper: Extract Patient Info
# ---------------------------
import re
from datetime import datetime
from typing import Dict

def extract_patient_info(text: str) -> Dict[str, str]:
    name_match = re.search(r"Patient Name:\s*(.+)", text)
    dob_match = re.search(r"DOB:\s*(\d{4}-\d{2}-\d{2})", text)
    age_match = re.search(r"Age:\s*(\d{1,3})", text)

    name = name_match.group(1).strip() if name_match else "The patient"
    age = "unknown age"
    dob_str = dob_match.group(1) if dob_match else "unknown DOB"

    if age_match:
        age = age_match.group(1)
    elif dob_match:
        dob = datetime.strptime(dob_str, "%Y-%m-%d")
        today = datetime.now()
        age = str(today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day)))

    gender = "unspecified gender"
    if re.search(r"\bfemale\b", text, re.IGNORECASE):
        gender = "female"
    elif re.search(r"\bmale\b", text, re.IGNORECASE):
        gender = "male"

    return {"name": name, "age": age, "gender": gender, "dob": dob_str}


# ---------------------------
# Generate Narrative Overview
# ---------------------------
def generate_narrative_overview_spacy(text: str, category: str) -> str:
    cat = (category or "default").lower()
    doc = nlp(text) if nlp else None

    persons = list(set([ent.text for ent in doc.ents if ent.label_ == "PERSON"])) if doc else []
    orgs = list(set([ent.text for ent in doc.ents if ent.label_ == "ORG"])) if doc else []

    if cat == "medical":
        info = extract_patient_info(text)
        hospital = next((o for o in orgs if "hospital" in o.lower()), "the medical facility")
        doctor = next((p for p in persons if "Dr." in p), "the attending physician")
        complaints_match = re.search(r"Clinical Summary\s*(.*?)Impressions", text, re.DOTALL)
        complaints = complaints_match.group(1).strip().replace("\n", " ") if complaints_match else "clinical symptoms"
        impressions_match = re.search(r"Impressions\s*(.*?)Parameter", text, re.DOTALL)
        impressions = impressions_match.group(1).strip().replace("\n", "; ") if impressions_match else "clinical concerns noted"

        return (
            f"{info['name']}, a {info['age']}-year-old {info['gender']}, was evaluated at {hospital} under {doctor}. "
            f"She presented with {complaints}. "
            f"Impressions include: {impressions}. "
            f"Management includes medication, lifestyle changes, and follow-up as advised."
        )

    elif cat == "legal":
        case_title = re.search(r"Case Title:\s*(.+)", text)
        case_number = re.search(r"Case Number:\s*(.+)", text)
        court = re.search(r"Jurisdiction:\s*(.+)", text)
        judge = next((p for p in persons if "Justice" in p), "the presiding judge")
        plaintiff = re.search(r"Plaintiff:\s*(.+)", text)
        defendant = re.search(r"Defendant:\s*(.+)", text)
        summary = re.search(r"Case Summary:\s*([\s\S]*?)\n[A-Z]", text)
        summary_text = summary.group(1).strip().replace("\n", " ") if summary else "Details of the case are under review."

        return (
            f"{case_title.group(1) if case_title else 'A legal case'} (Case No. {case_number.group(1) if case_number else 'N/A'}) "
            f"is being heard in {court.group(1) if court else 'the relevant court'} under {judge}. "
            f"The dispute involves {plaintiff.group(1) if plaintiff else 'the plaintiff'} and {defendant.group(1) if defendant else 'the defendant'}. "
            f"Summary: {summary_text}"
        )

    elif cat == "financial":
        company = re.search(r"Company:\s*(.+)", text)
        period = re.search(r"Fiscal Period:\s*(.+)", text)
        revenue = re.search(r"Revenue\s*\n\s*([\d.]+ Cr)", text)
        net_income = re.search(r"Net Income\s*\n\s*([\d.]+ Cr)", text)
        arr = re.search(r"ARR:\s*([\d.]+ Cr)", text)
        margin = re.search(r"Gross Margin:\s*([\d.%]+)", text)
        org_name = company.group(1) if company else "the company"

        return (
            f"{org_name} reported financial results for {period.group(1) if period else 'the reporting period'}. "
            f"Key metrics include Revenue of {revenue.group(1) if revenue else 'N/A'}, Net Income of {net_income.group(1) if net_income else 'N/A'}, "
            f"ARR of {arr.group(1) if arr else 'N/A'}, and Gross Margin of {margin.group(1) if margin else 'N/A'}."
        )

    elif cat == "general":
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        sentences = [s for s in sentences if len(s.split()) > 3]
        top_sentences = sentences[:3]
        summary = " ".join(top_sentences)
        return f"This document provides the following key information: {summary}"

    return "This document contains relevant summarized information."

# ---------------------------
# Sentence Scoring
# ---------------------------
def score_sentence(sentence: str, category: str) -> int:
    score = 0
    if nlp:
        doc = nlp(sentence)
        score += len(doc.ents)
    keywords = {
        "medical": ["symptom", "diagnosis", "treatment", "patient", "clinical", "impression", "follow-up", "medication", "plan", "recommendation"],
        "legal": ["case", "ruling", "plaintiff", "defendant", "contract", "compliance", "clause", "hearing", "jurisdiction"],
        "financial": ["revenue", "profit", "loss", "quarter", "growth", "market", "cash", "margin", "income"]
    }
    for word in keywords.get(category, []):
        if word in sentence.lower():
            score += 2
    return score

# ---------------------------
# Main Summarizer
# ---------------------------
def summarize_structured_with_insights(text: str, category: str = None) -> Dict[str, object]:
    if not text.strip():
        return {"overview": "No overview available.", "key_points": [], "insights": []}

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s for s in sentences if len(s.split()) > 3]

    ranked = sorted(sentences, key=lambda s: score_sentence(s, category or "default"), reverse=True)
    key_points = ranked[:8]

    overview = generate_narrative_overview_spacy(text, category)

    insights = []
    cat = (category or "default").lower()
    if cat == "financial":
        if "growth" in text.lower():
            insights.append("Revenue growth observed, possibly driven by subscriptions or renewals.")
        if "margin" in text.lower():
            insights.append("Margin improvements may reflect cost optimization.")
        if "cash flow" in text.lower():
            insights.append("Positive cash flow indicates financial stability.")
    elif cat == "medical":
        if "ldl" in text.lower() and re.search(r"LDL[- ]?C.*?(\\d+)", text):
            ldl_val = int(re.search(r"LDL[- ]?C.*?(\\d+)", text).group(1))
            if ldl_val > 100:
                insights.append(f"LDL level ({ldl_val} mg/dL) is above target; consider intensifying statin therapy.")
        if "gerd" in text.lower() or "reflux" in text.lower():
            insights.append("GERD suspected; PPI trial and lifestyle changes recommended.")
        if "follow-up" in text.lower():
            insights.append("Follow-up scheduled; monitor symptoms and adjust treatment as needed.")
    elif cat == "legal":
        if "confidentiality" in text.lower():
            insights.append("Confidentiality clause is a key point of contention.")
        if "force majeure" in text.lower():
            insights.append("Force majeure defense may be challenged based on context.")
        if "next hearing" in text.lower():
            next_hearing = re.search(r"Next Hearing:\s*(.+)", text)
            if next_hearing:
                insights.append(f"Next hearing scheduled for {next_hearing.group(1)}.")
    elif cat == "general":
        insights.append("Document covers general information; no domain-specific insights detected.")

    return {
        "overview": overview,
        "key_points": key_points,
        "insights": insights
    }
