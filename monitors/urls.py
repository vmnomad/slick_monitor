from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.test, name='test'),
    path('get_form/<str:type>/', views.get_form, name='get_form'),
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_monitor, name='add_monitor'),
    path('edit/', views.edit_monitor, name='edit_monitor'),
]