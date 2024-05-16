from django.urls import reverse_lazy
from .models import Course
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

class IsCreatorMixin:
    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)

class CreatorEditMixin:
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class CreatorCourseMixin(IsCreatorMixin,
                         LoginRequiredMixin,
                         PermissionRequiredMixin):
    model = Course
    fields = ['title','published','logo', 'slug', 'description', 'tags']
    success_url = reverse_lazy('manage_course_list')

class CreatorCourseUpdateMixin(CreatorCourseMixin, CreatorEditMixin):
    template_name = 'manage/course/form.html'


