from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
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
            return redirect('course_list')
        return self.render_to_response({'module': self.module, 'formset': formset})