from django.urls import path 
from the_queue.views import (QueueInFirestoreListCreateView, QueueInFirestoreDetailView, QueueInFirestorePartialUpdateView)


urlpatterns = [
    path("", QueueInFirestoreListCreateView.as_view(), name="queue-in-firebase-list-create"),
    path("<str:queue_id>/", QueueInFirestoreDetailView.as_view(), name="queue-in-firebase-detail"),
    path("partial_update/<str:queue_id>/", QueueInFirestorePartialUpdateView.as_view(), name="queue-in-firebase-partial_update"),
]