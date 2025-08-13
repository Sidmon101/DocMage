
from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'doc_type', 'uploaded_at')
    search_fields = ('title', 'category')
    list_filter = ('doc_type', 'category', 'uploaded_at')
