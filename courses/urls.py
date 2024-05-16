from django.urls import path
from . import views

urlpatterns = [
    path('manage/list/', views.ManageCourseListView.as_view(), name='manage_course_list'),
    path('create/', views.CourseCreateView.as_view(), name='course_create'),
    path('<pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('<pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
    path('<pk>/module/', views.CourseModuleUpdateView.as_view(), name='course_module_update'),
    path('<pk>/lesson/', views.CourseLessonUpdateView.as_view(), name='course_lesson_update'),
    path('lesson/<int:lesson_id>/content/<model_name>/create/',
         views.CourseContentCreateUpdateView.as_view(),
         name='content_create'),
    path('lesson/<int:lesson_id>/content/<model_name>/<id>/',
         views.CourseContentCreateUpdateView.as_view(),
         name='content_update'),
    path('lesson/<int:lesson_id>/',views.CourseContentListEditView.as_view(), name='lesson_content_list'),
    path('content/<int:id>/delete/', views.CourseContentDeleteView.as_view(), name='content_delete'),


    path('list/', views.CourseListView.as_view(), name='course_list'),
]