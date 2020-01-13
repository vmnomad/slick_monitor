from django.urls import path
from . import views

urlpatterns = [
    path('', views.default , name='default'),
    path(r'alerts/', views.alerts, name='alerts'),
    path(r'loggers/', views.loggers, name='loggers'),
    path(r'settings/alerts_email/', views.alerts_email, name='email'),
    path(r'settings/alerts_slack/', views.alerts_slack, name='slack'),
    path(r'loggers_console/', views.loggers_console, name='console'),
    path(r'loggers_netcat/', views.loggers_netcat, name='netcat'),
    path(r'loggers_file/', views.loggers_file, name='file'),
    path(r'change_password/', views.change_password, name='change_password'),
    path(r'set_password/', views.set_password, name='set_password'),
    path(r'login/', views.my_login, name='login'),
    path(r'logout/', views.my_logout, name='logout'),
]