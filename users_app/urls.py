from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegisterUserView
from hotel_app.views import register_view, login_view, logout_view

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'),
]