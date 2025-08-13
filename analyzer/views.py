from django.shortcuts import render, redirect, get_object_or_404
from .forms import DocumentForm, TextAnalysisForm
from .models import Document
from .nlp_utils.extract_text import extract_text
from .nlp_utils.summarizer import summarize_structured_with_insights
from .nlp_utils.highlighter import extract_highlights, CATEGORY_LABELS
from django.http import FileResponse, Http404
from .nlp_utils.pdf_generator import generate_summary_pdf
from django.utils.text import slugify
from itertools import chain
from django.conf import settings
import os


def home(request):
    return render(request, 'analyzer/home.html')


def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save()
            file_path = document.file.path

            raw_text = extract_text(file_path, document.doc_type)
            structured_summary = summarize_structured_with_insights(raw_text, document.category)
            highlights = extract_highlights(raw_text, document.category)

            document.raw_text = raw_text
            document.summary = structured_summary.get("overview", "")
            document.key_points = structured_summary.get("key_points", [])
            document.highlights = highlights
            document.save(update_fields=['raw_text', 'summary', 'key_points', 'highlights'])

            return redirect('document_list')
    else:
        form = DocumentForm()
    return render(request, 'analyzer/upload.html', {'form': form})


def document_list(request):
    documents = Document.objects.all().order_by('-uploaded_at')
    return render(request, 'analyzer/list.html', {'documents': documents})


def document_detail(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    raw_text = doc.raw_text or extract_text(doc.file.path, doc.doc_type)
    highlights = doc.highlights or extract_highlights(raw_text, doc.category)

    structured_summary = summarize_structured_with_insights(raw_text, doc.category)
    overview = structured_summary.get("overview", "")
    key_points = structured_summary.get("key_points", [])

    formatted_highlights = {key.replace("_", " "): value for key, value in highlights.items()}
    all_category_keys = list(chain.from_iterable(CATEGORY_LABELS[cat].keys() for cat in CATEGORY_LABELS))

    return render(request, 'analyzer/detail.html', {
        'document': doc,
        'raw_text': raw_text,
        'highlights': formatted_highlights,
        'overview': overview,
        'key_points': key_points,
        'insights': structured_summary.get("insights", []),
        'category_labels': CATEGORY_LABELS,
        'all_category_keys': [k.replace("_", " ") for k in all_category_keys]
    })


def analyze_text(request):
    result = None
    if request.method == 'POST':
        form = TextAnalysisForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            category = form.cleaned_data['category']
            highlights = extract_highlights(text, category)
            structured_summary = summarize_structured_with_insights(text, category)

            formatted_highlights = {key.replace("_", " "): value for key, value in highlights.items()}

            result = {
                'text': text,
                'highlights': formatted_highlights,
                'overview': structured_summary.get("overview", ""),
                'key_points': structured_summary.get("key_points", []),
                'insights': structured_summary.get("insights", []),
                'category': category
            }
    else:
        form = TextAnalysisForm()

    return render(request, 'analyzer/analyze_text.html', {'form': form, 'result': result})





def download_summary_pdf(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    raw_text = doc.raw_text or extract_text(doc.file.path, doc.doc_type)

    structured_summary = summarize_structured_with_insights(raw_text, doc.category)
    overview = structured_summary.get("overview", "No overview available.")
    key_points = structured_summary.get("key_points", [])

    highlights_dict = doc.highlights or extract_highlights(raw_text, doc.category) or {}
    formatted_highlights = {k.replace("_", " "): v for k, v in highlights_dict.items()}

    output_path = f"media/summaries/{doc.title}_summary.pdf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    generate_summary_pdf(
        title=doc.title,
        summary=overview,  # narrative overview
        output_path=output_path,
        category=doc.category,
        highlights=formatted_highlights,
        tool_name="DocMage - Smart Document Analyzer",
        paragraphs=[overview],
        bullets=key_points
    )

    return FileResponse(open(output_path, 'rb'), as_attachment=True, filename=f"{doc.title}_summary.pdf")
