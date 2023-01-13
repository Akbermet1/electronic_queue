from django.urls import path

from institution.views import list_institutions


urlpatterns = [
    path('', list_institutions),
]