from django.urls import path
from branch.views import (BranchInFirestoreDetailView, BranchInFirestoreListCreateView)


urlpatterns = [
    path("", BranchInFirestoreListCreateView.as_view(), name="branch-firetore-list-create-view"),
    path("<str:branch_id>/", BranchInFirestoreDetailView.as_view(), name="branch-firetore-detail-view"),
]