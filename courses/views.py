from datetime import timedelta

from django.contrib.postgres.search import SearchVector, TrigramSimilarity
from django.db.models import Q, F
from taggit.models import Tag
from django.apps import apps
from django.forms import modelform_factory, modelformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.edit import FormView

from .forms import ModuleFormSet, LessonFormSet, CourseFilterForm, CourseEnrollForm
from .models import Course, Module, Content, Lesson
from .mixin import CreatorCourseMixin, CreatorCourseUpdateMixin

class ManageCourseListView(CreatorCourseMixin, ListView):
    template_name = 'manage/course/list.html'
    permission_required = 'courses.view_course'
    login_url = reverse_lazy('dashboard')
    raise_exception = True

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
        form = CourseFilterForm(request.GET)
        courses = self.model.objects.all().filter(published=True)

        if form.is_valid():
            tags = form.cleaned_data.get('tags')
            rating = form.cleaned_data.get('rating')
            passage_time = form.cleaned_data.get('passage_time')
            course_name = form.cleaned_data.get('course_name')

            if tags:
                tags = [tag.name.lower() for tag in tags]
                courses = courses.filter(tags__name__iregex=r'(' + '|'.join(tags) + ')').distinct()

            if rating:
                courses = courses.filter(rating__gte=rating)

            if passage_time:
                hours, minutes, seconds = map(int, passage_time.split(':'))
                passage_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                courses = courses.filter(passage_time__lte=passage_time)

            if course_name:
                courses = courses.annotate(
                    title_similarity=TrigramSimilarity('title', course_name),
                    description_similarity=TrigramSimilarity('description', course_name),
                ).annotate(
                    total_similarity=F('title_similarity') + F('description_similarity')
                ).filter(total_similarity__gt=0.1).order_by('-total_similarity')

        context = {
            'courses': courses,
            'form': form
        }

        return self.render_to_response(context)

class CourseDetailView(DetailView):
    model = Course
    template_name = 'course/detail.html'

    def get_queryset(self):
        return super().get_queryset().filter(published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modules'] = self.object.modules.all()
        context['lessons'] = Lesson.objects.filter(module__in=context['modules'])
        context['enrolled'] = self.object.user.filter(id=self.request.user.id).exists()
        return context


############################################################################################################
# Enroll courses view
############################################################################################################

def course_enroll(request):
    if request.method == 'POST':
        form = CourseEnrollForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']
            course.user.add(request.user)
            return redirect('course_detail', slug=course.slug)
    return redirect('course_list')

class EnrollCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'course/enroll_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)



class EnrollCourseDetailView(DetailView):
    model = Course
    template_name = 'course/enroll_detail.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            course = self.get_object()
            modules = course.modules.all()
            lessons = Lesson.objects.filter(module__in=modules)
            context['modules'] = modules
            context['lessons'] = lessons
        except Exception as e:
            pass
        return context


class EnrollModuleDetailView(DetailView):
    model = Module
    template_name = 'course/enroll_module_detail.html'

    def get_object(self):
        course_id = self.kwargs.get('pk')
        module_id = self.kwargs.get('module_id')
        course = get_object_or_404(Course, id=course_id, user=self.request.user)
        module = get_object_or_404(Module, id=module_id, course=course)
        return module

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module = self.get_object()
        context['course'] = module.course
        context['lessons'] = module.lessons.all()
        return context


class EnrollLessonDetailView(DetailView):
    model = Lesson
    template_name = 'course/enroll_lesson_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.get_object()
        context['lesson'] = lesson
        return context