from django.urls import path
from branch.views import (BranchInFirestoreDetailView, BranchInFirestoreListCreateView, BranchInFirestorePartialUpdateView)


urlpatterns = [
    path("", BranchInFirestoreListCreateView.as_view(), name="branch-firetore-list-create-view"),
    path("<str:branch_id>/", BranchInFirestoreDetailView.as_view(), name="branch-firetore-detail-view"),
    path("partial_update/<str:branch_id>/", BranchInFirestorePartialUpdateView.as_view(), name="branch-in-firebase-partial_update"),
]