from django.urls import path, include
from user.views import register_user_view


urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("register/", register_user_view, name="register-user-view"),
]