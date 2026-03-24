from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('request/', views.request_page, name='request_page'),
    path('return/', views.return_page, name='return_page'),
    path('manage/', views.manage_page, name='manage_page'),
    path('add/', views.add_page, name='add_page'),
]