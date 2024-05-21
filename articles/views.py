from django.apps import apps
from django.forms import modelform_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.views.generic.base import TemplateResponseMixin, View

from .mixin import isAuthorMixin, AuthorEditMixin, AuthorArticleMixin, AuthorArticleUpdateMixin
from .models import Article, Content

class ManageArticleListView(AuthorArticleMixin,ListView):
    template_name = 'manage/article/list.html'
    permission_required = 'articles.view_article'
    raise_exception = True

class ArticleCreateView(AuthorArticleUpdateMixin,CreateView):
    permission_required = 'articles.add_article'
    success_url = reverse_lazy('articles:manage_article_list')

class ArticleUpdateView(AuthorArticleUpdateMixin,UpdateView):
    permission_required = 'articles.change_article'
    success_url = reverse_lazy('articles:manage_article_list')

class ManegeArticleContentListView(isAuthorMixin, ListView):
    model = Content
    template_name = 'manage/article/content_list.html'
    permission_required = 'articles.view_content'

    def dispatch(self, request, *args, **kwargs):
        self.article = get_object_or_404(Article, pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Content.objects.filter(article_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['article'] = self.article
        return context

class ArcticleContentCreateUpdateView(TemplateResponseMixin, View):
    template_name = 'manage/article/content_form.html'
    article = None
    model = None
    obj = None

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['created_at', 'updated_at'])
        return Form(*args, **kwargs)

    def dispatch(self, request, article_id, model_name, id=None):
        self.article = get_object_or_404(Article, id=article_id, author=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id)
        return super().dispatch(request, article_id, model_name, id)

    def get(self, request, lesson_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, lesson_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            print(id)
            if not id:
                Content.objects.create(article=self.article, item=obj)
            return redirect('articles:manage_article_content_list', pk=self.article.id)
        return self.render_to_response({'form': form, 'object': self.obj})

class ArticleContentDeleteView(isAuthorMixin, View):
    def post(self, request, id):
        content = get_object_or_404(Content, id=id, article__author=request.user)
        article = content.article
        content.item.delete()
        content.delete()
        return redirect('articles:manage_article_content_list', pk=article.id)


