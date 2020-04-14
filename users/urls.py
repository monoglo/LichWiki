from django.urls import include, path
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'users'
urlpatterns = [
    path('api/users/', views.UserList.as_view()),
    path('api/user/<str:user_name>', views.UserDetail.as_view()),
    path('user_login', views.UserLogin.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
