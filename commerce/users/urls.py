from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import register, login_view

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(template_name='users/logout.html'), name='logout-user'),
]
