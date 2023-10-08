from django.urls import path, include
from user.views import register_user_view, manage_user_account_view


urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("register/", register_user_view, name="register-user-view"),
    path("manage_account/", manage_user_account_view, name="manage-user-account"),
]