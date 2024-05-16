from django import forms
from django.forms.models import inlineformset_factory
from taggit.models import Tag

from .models import Course, Module, Lesson, Content

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