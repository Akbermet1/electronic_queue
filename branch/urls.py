from django.urls import path
from branch.views import BranchInFirestoreDetailView


urlpatterns = [
    path("<str:branch_id>/", BranchInFirestoreDetailView.as_view(), name="branch-firetore-detail-view"),
]