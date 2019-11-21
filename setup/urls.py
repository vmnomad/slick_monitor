from django.urls import path
from . import views

urlpatterns = [
    path('', views.default , name='index'),
    path(r'settings/', views.settings, name='settings'),
    path(r'settings/email/', views.settings_email, name='email'),
    path(r'settings/slack/', views.settings_slack, name='slack'),
    path(r'change_password/', views.change_password, name='change_password'),
    path(r'login/', views.my_login, name='login'),
    path(r'logout/', views.my_logout, name='logout'),
]