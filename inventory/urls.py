from django.urls import path, include
from . import views
from .views import signup

urlpatterns = [
    path('', views.index, name='index'),
    path('request/', views.request_page, name='request_page'),
    path('return/', views.return_page, name='return_page'),
    path('manage/', views.manage_page, name='manage_page'),
    path('add/', views.add_page, name='add_page'),
    path('users/', views.user_list, name='user_list'),
    path('user/create/', views.user_create, name='user_create'),
    path('user/<int:pk>/update/', views.user_update, name='user_update'),
    path('user/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/signup/", signup, name="signup"),
    path('request/<int:pk>/update/', views.request_update, name='request_update'),
]