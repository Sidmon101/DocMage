from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file', 'doc_type', 'category']

class TextAnalysisForm(forms.Form):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('medical', 'Medical'),
        ('legal', 'Legal'),
        ('financial', 'Financial'),
    ]
    text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'placeholder': 'Paste your text here...'}),
        label="Enter Text"
    )
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        label="Document Category"
    )
