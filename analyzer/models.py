from django.db import models


class Document(models.Model):
    DOC_TYPES = [
        ('pdf', 'PDF'),
        ('docx', 'Word'),
        ('txt', 'Text'),
    ]

    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('medical', 'Medical'),
        ('legal', 'Legal'),
        ('financial', 'Financial'),
    ]

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    doc_type = models.CharField(max_length=10, choices=DOC_TYPES, default='pdf')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    summary = models.TextField(blank=True, null=True)  # Overview
    key_points = models.JSONField(blank=True, null=True)  # ✅ New field
    raw_text = models.TextField(blank=True, null=True)
    highlights = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.title
