from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('input/', views.input, name='input'),
    path('status/', views.status, name='status'),
    path('unread_notification_count/', views.unread_notification_count, name='unread_notification_count'),
    path('notifications/', views.notifications, name='notifications'),
]