from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import TrigramSimilarity
from django.forms import modelform_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.views.generic.base import TemplateResponseMixin, View

from .forms import ArticleFilterForm, FollowUserForm
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




class ArticleListView(TemplateResponseMixin, View):
    model = Article
    template_name = 'article/list.html'

    def get(self, request):
        form = ArticleFilterForm(request.GET)
        articles = self.model.objects.filter(published=True)

        if form.is_valid():
            tags = form.cleaned_data.get('tags')
            article_name = form.cleaned_data.get('article_name')
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')

            if tags:
                tags = [tag.name.lower() for tag in tags]
                articles = articles.filter(tags__name__iregex=r'(' + '|'.join(tags) + ')').distinct()
            if article_name:
                articles = articles.annotate(tittle_semilar=TrigramSimilarity('title', article_name)).filter(tittle_semilar__gt=0.1).order_by('-tittle_semilar')
            if date_from:
                articles = articles.filter(updated_at__gte=date_from)
            if date_to:
                articles = articles.filter(updated_at__lte=date_to)
        context = {
            'articles': articles,
            'form': form
        }

        return self.render_to_response(context)

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'article/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contents'] = self.object.contents.all()
        return context

class SubscribedArticlesView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'article/subscribed_articles.html'
    context_object_name = 'articles'

    def get_queryset(self):
        user = self.request.user
        following_ids = user.following.values_list('id', flat=True)
        articles = Article.objects.filter(author_id__in=following_ids, published=True)
        self.form = FollowUserForm(user=user)

        if self.request.GET.get('follow_users'):
            form = FollowUserForm(self.request.GET, user=user)
            if form.is_valid():
                following_ids = form.cleaned_data['following_users']
                tags = form.cleaned_data.get('tags')
                article_name = form.cleaned_data.get('article_name')
                date_from = form.cleaned_data.get('date_from')
                date_to = form.cleaned_data.get('date_to')

                if tags:
                    tags = [tag.name.lower() for tag in tags]
                    articles = articles.filter(tags__name__iregex=r'(' + '|'.join(tags) + ')').distinct()
                if article_name:
                    articles = articles.annotate(tittle_semilar=TrigramSimilarity('title', article_name)).filter(
                        tittle_semilar__gt=0.1).order_by('-tittle_semilar')
                if date_from:
                    articles = articles.filter(updated_at__gte=date_from)
                if date_to:
                    articles = articles.filter(updated_at__lte=date_to)
                self.form = form
        return articles

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        return context
