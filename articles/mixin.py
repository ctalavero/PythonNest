from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy

from .models import Article, Content
class isAuthorMixin:
    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)

class AuthorEditMixin:
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class AuthorArticleMixin(isAuthorMixin, LoginRequiredMixin, PermissionRequiredMixin):
    model = Article
    fields = ['title','logo', 'published', 'slug', 'tags']

class AuthorArticleUpdateMixin(AuthorArticleMixin, AuthorEditMixin):
    template_name = 'manage/article/form.html'