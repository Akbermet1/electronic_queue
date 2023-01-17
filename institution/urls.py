from django.urls import path

from institution.views import list_institutions, test_view


urlpatterns = [
    path('', list_institutions),
    path("test/", test_view),
]