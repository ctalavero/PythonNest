from datetime import timedelta

from django.contrib.postgres.search import SearchVector, TrigramSimilarity
from django.db.models import Q
from taggit.models import Tag
from django.apps import apps
from django.forms import modelform_factory, modelformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateResponseMixin, View

from .forms import ModuleFormSet, LessonFormSet
from .models import Course, Module, Content, Lesson
from .mixin import CreatorCourseMixin, CreatorCourseUpdateMixin

class ManageCourseListView(CreatorCourseMixin, ListView):
    template_name = 'manage/course/list.html'
    permission_required = 'courses.view_course'

class CourseCreateView(CreatorCourseUpdateMixin, CreateView):
    permission_required = 'courses.add_course'

class CourseUpdateView(CreatorCourseUpdateMixin, UpdateView):
    permission_required = 'courses.change_course'

class CourseDeleteView(CreatorCourseMixin, DeleteView):
    permission_required = 'courses.delete_course'
    template_name = 'manage/course/delete.html'

class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'manage/module/form.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course, id=pk, created_by=request.user)
        return super().dispatch(request, pk)

    def get(self, request, pk):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course, 'formset': formset})

    def post(self, request, pk):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('course_list')
        return self.render_to_response({'course': self.course, 'formset': formset})



class CourseLessonUpdateView(TemplateResponseMixin, View):
    template_name = 'manage/lesson/form.html'
    module = None

    def get_formset(self, data=None):
        return LessonFormSet(instance=self.module, data=data)

    def dispatch(self, request, pk):
        self.module = get_object_or_404(Module, id=pk, course__created_by=request.user)
        return super().dispatch(request, pk)

    def get(self, request, pk):
        formset = self.get_formset()
        return self.render_to_response({'module': self.module, 'formset': formset})

    def post(self, request, pk):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('lesson_content_list', lesson_id=self.lesson.id)
        return self.render_to_response({'module': self.module, 'formset': formset})


class CourseContentListEditView(TemplateResponseMixin, View):
    template_name = 'manage/content/list.html'

    def get(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id, module__course__created_by=request.user)
        return self.render_to_response({'lesson': lesson})



class CourseContentCreateUpdateView(TemplateResponseMixin, View):
    lesson = None
    model = None
    obj = None
    template_name = 'manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['created_at', 'updated_at'])
        return Form(*args, **kwargs)

    def dispatch(self, request, lesson_id, model_name, id=None):
        self.lesson = get_object_or_404(Lesson, id=lesson_id, module__course__created_by=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id)
        return super().dispatch(request, lesson_id, model_name, id)

    def get(self, request, lesson_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, lesson_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            if not id:
                Content.objects.create(lesson=self.lesson,item=obj)
            return redirect('lesson_content_list', lesson_id=self.lesson.id)
        return self.render_to_response({'form': form, 'object': self.obj})

class CourseContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content, id=id, lesson__module__course__created_by=request.user)
        content.item.delete()
        content.delete()
        return redirect('lesson_content_list', lesson_id=int(request.POST.get('lesson_id')))


class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'course/list.html'

    def get(self, request):
        courses = self.model.objects.all().filter(published=True)
        tags = request.GET.getlist('tags')
        rating = request.GET.get('rating')
        passage_time = request.GET.get('passage_time')
        course_name = request.GET.get('course_name')

        context = {}

        if tags:
            courses = courses.filter(tags__name__in=tags).distinct()
            context['selected_tags'] = tags

        if rating:
            courses = courses.filter(rating__gte=rating)
            context['rating'] = rating

        if passage_time:
            hours, minutes, seconds = map(int, passage_time.split(':'))
            passage_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            courses = courses.filter(passage_time__lte=passage_time)
            context['passage_time'] = passage_time

        if course_name:
            courses = courses.annotate(
                similarity=TrigramSimilarity('title', course_name)
            ).filter(similarity__gt=0.1).order_by('-similarity')
            context['course_name'] = course_name

        context['courses'] = courses
        context['tags'] = Tag.objects.all()

        return self.render_to_response(context)