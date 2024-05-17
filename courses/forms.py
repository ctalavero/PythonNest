from django import forms
from django.forms.models import inlineformset_factory
from taggit.models import Tag
from django.core.exceptions import ValidationError
from .models import Course, Module, Lesson, Content
import re
ModuleFormSet = inlineformset_factory(Course, Module, fields=['title', 'description','order'], extra=2, can_delete=True)
LessonFormSet = inlineformset_factory(Module, Lesson, fields=['title', 'order',], extra=2, can_delete=True)

class CourseFilterForm(forms.Form):
    course_name = forms.CharField(required=False, label='Пошук курсу')
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    rating = forms.IntegerField(required=False, min_value=0, max_value=5, label='Мінімальний рейтинг')
    passage_time = forms.CharField(required=False, label='Максимальний час проходження (HH:MM:SS)')
    def clean_passage_time(self):
        passage_time = self.cleaned_data.get('passage_time')

        if passage_time:
            if not re.match(r'^\d{2}:\d{2}:\d{2}$', passage_time):
                raise ValidationError('Введіть час у форматі HH:MM:SS')

        return passage_time