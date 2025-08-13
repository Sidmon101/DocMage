from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_document, name='upload_document'),
    path('documents/', views.document_list, name='document_list'),
    path('documents/<int:doc_id>/', views.document_detail, name='document_detail'),
    path('analyze-text/', views.analyze_text, name='analyze_text'),  # ✅ Add this line
    path('download-summary/<int:doc_id>/', views.download_summary_pdf, name='download_summary_pdf'),


]
