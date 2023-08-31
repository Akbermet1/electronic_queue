from django.urls import path

from institution.views import (list_institutions, list_all_branches_of_institution_view,
                                manage_institutions_queue)


urlpatterns = [
    path('', list_institutions, name="list-institutions"),
    path("<str:institution_id>/queue/<str:queue_id>/", manage_institutions_queue, name="manage-institutions-queue"),
    path("<str:institution_id>/branches/", list_all_branches_of_institution_view, name="list-branches-of-institution"),
]