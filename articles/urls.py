from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('manage-article-list/', views.ManageArticleListView.as_view(), name='manage_article_list'),
    path('article-create/',  views.ArticleCreateView.as_view(), name='article_create'),
    path('article-update/<int:pk>/',  views.ArticleUpdateView.as_view(), name='article_update'),
    path('manage-article-content-list/<int:pk>/',  views.ManegeArticleContentListView.as_view(), name='manage_article_content_list'),
    path('article/<int:article_id>/content/<model_name>/create/', views.ArcticleContentCreateUpdateView.as_view(),
         name='content_create'),
    path('article/<int:article_id>/content/<model_name>/<id>/', views.ArcticleContentCreateUpdateView.as_view(),
         name='content_update'),
    path('article-content/<int:id>/delete/', views.ArticleContentDeleteView.as_view(), name='content_delete'),
]