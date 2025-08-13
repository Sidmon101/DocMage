# DocMage – Smart Document Analyzer

> Upload documents, auto-extract text, generate structured summaries with insights, highlight key sections, analyze arbitrary text, and download polished PDF summaries.

!Python
!Django
!License: MIT

## Table of Contents
- Overview
- Features
- How it Works
- Tech Stack
- Project Structure
- Getting Started
- Configuration
- Running Locally
- Endpoints & Screens
- Data Shapes
- PDF Export
- Troubleshooting
- Contributing
- License

---

## Overview
DocMage is a Django web app that lets you **upload documents** (PDF/Docs/etc.), **extract text**, **summarize with insights**, **highlight key fields** by category, and **download a clean summary PDF**. You can also paste free text for quick analysis without uploading a file.

This repo is ideal for teams who want a fast, user-friendly interface around document/text analysis with consistent output.

---

## Features
- 📤 **Document upload** (via form)  
- 🧠 **Text extraction** from files
- 📝 **Structured summaries**: overview, key points, insights
- 🔎 **Category-based highlights** with human-readable labels
- 🧪 **Free text analysis** (no file required)
- 🗂️ **Document listing & detail view** with re-analysis on demand
- 📄 **One-click summary PDF export**
- 🕸️ **Clean templates** for home, upload, list, detail, and text analysis pages

---

## How it Works
- `extract_text(file_path, doc_type)` reads content from the uploaded file.
- `summarize_structured_with_insights(text, category)` produces:
  - `overview` (string)
  - `key_points` (list of strings)
  - `insights` (list of strings or dicts)
- `extract_highlights(text, category)` returns a dictionary of category-specific highlights.
- `CATEGORY_LABELS` maps categories to human-readable keys for UI display.
- `generate_summary_pdf(...)` compiles a formatted PDF with the overview, key points, and highlights.

> PDFs are written to `media/summaries/<title>_summary.pdf` (path configurable).

---

## Tech Stack
- **Python** 3.10+  
- **Django** 4.x  
- Optional/Assumed:
  - A PDF library (e.g., ReportLab/FPDF/PyMuPDF) behind `nlp_utils/pdf_generator.py`
  - A text extraction library for PDFs/Docs behind `nlp_utils/extract_text.py`
- **HTML Templates** under `analyzer/templates/analyzer/`

> If your NLP uses external providers (OpenAI, Azure AI, etc.), add the relevant API keys to your environment. Otherwise, local deterministic logic is fine.

---

## Project Structure
```text
analyzer/
├─ views.py                     # (provided)
├─ models.py                    # (inferred: Document model)
├─ forms.py                     # (inferred: DocumentForm, TextAnalysisForm)
├─ templates/
│  └─ analyzer/
│     ├─ home.html
│     ├─ upload.html
│     ├─ list.html
│     ├─ detail.html
│     └─ analyze_text.html
└─ nlp_utils/
   ├─ extract_text.py           # extract_text(file_path, doc_type)
   ├─ summarizer.py             # summarize_structured_with_insights(text, category)
   ├─ highlighter.py            # extract_highlights(text, category), CATEGORY_LABELS
   └─ pdf_generator.py          # generate_summary_pdf(...)
