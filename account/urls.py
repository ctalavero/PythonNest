from django.urls import path
from . import views
from  django.contrib.auth import views as auth_views

app_name = 'account'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('register/',views.register,name='register'),
    path('test/', views.test, name='test'),
]
