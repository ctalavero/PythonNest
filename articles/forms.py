from django import forms
from django.core.exceptions import ValidationError
from taggit.models import Tag


class DateInput(forms.DateInput):
    input_type = 'date'

class ArticleFilterForm(forms.Form):
    article_name = forms.CharField(required=False, label='Пошук артиклу')
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Теги'
    )
    date_from = forms.DateField(required=False, label='Дата від', widget=DateInput())
    updated_at = forms.DateField(required=False, label='Дата до', widget=DateInput())
