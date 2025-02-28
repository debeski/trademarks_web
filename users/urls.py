# users/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import UserActivityLogView

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("users/", views.UserListView.as_view(), name="manage_users"),
    path('users/create/', views.create_user, name='create_user'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path("logs/", views.UserActivityLogView.as_view(), name="user_activity_log"),
    path('reset_password/<int:user_id>/', views.reset_password, name="reset_password"),

]