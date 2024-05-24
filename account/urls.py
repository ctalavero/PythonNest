from django.urls import path
from django.views.generic import TemplateView

from . import views
from  django.contrib.auth import views as auth_views



urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('register/',views.register,name='register'),
    path('password-change/',auth_views.PasswordChangeView.as_view(),name='password_change'),
    path('password-change/done/',auth_views.PasswordChangeDoneView.as_view(),name='password_change_done'),
    path('password-reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password-reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('password-reset/complete/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    path('edit/',views.edit_profile,name='edit'),
    path('follow/', views.user_follow, name='user_follow'),
    path('profile/<str:username>/', views.UserDetailView.as_view(), name='user_detail'),
    path('request-access/', views.AccessRequestView.as_view(), name='request_access'),
    path('access-granted/', TemplateView.as_view(template_name='account/access_granted.html'), name='access_granted'),
    path('access-denied/', TemplateView.as_view(template_name='account/access_denied.html'), name='access_denied'),
]

urlpatterns += [
    path('followers/<int:user_pk>/', views.followers_list, name='followers_list'),
    path('following/<int:user_pk>/', views.following_list, name='following_list'),
]
