from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Course
from .mixin import CreatorCourseMixin, CreatorCourseUpdateMixin

class ManageCourseListView(CreatorCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'

class CourseCreateView(CreatorCourseUpdateMixin, CreateView):
    permission_required = 'courses.add_course'

class CourseUpdateView(CreatorCourseUpdateMixin, UpdateView):
    permission_required = 'courses.change_course'

class CourseDeleteView(CreatorCourseMixin, DeleteView):
    permission_required = 'courses.delete_course'
    template_name = 'courses/manage/course/delete.html'



