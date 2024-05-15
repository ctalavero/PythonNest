from django import forms
from django.forms.models import inlineformset_factory
from .models import Course, Module, Lesson, Content

ModuleFormSet = inlineformset_factory(Course, Module, fields=['title', 'description','order'], extra=2, can_delete=True)
LessonFormSet = inlineformset_factory(Module, Lesson, fields=['title', 'order',], extra=2, can_delete=True)