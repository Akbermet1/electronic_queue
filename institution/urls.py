from django.urls import path

from institution.views import (list_institutions, test_view, list_all_branches_of_institution_view)


urlpatterns = [
    path('', list_institutions),
    path("test/", test_view),
    path("<str:institution_id>/branches/", list_all_branches_of_institution_view, name="list-branches-of-institution"),
]