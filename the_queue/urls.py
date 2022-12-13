from django.urls import path 
from the_queue.views import (QueueInFirebaseListCreateView, QueueInFirestoreDetailView, QueueInFirestorePartialUpdateView)


urlpatterns = [
    path("", QueueInFirebaseListCreateView.as_view(), name="queue-in-firebase-list-create"),
    path("<str:queue_id>/", QueueInFirestoreDetailView.as_view(), name="queue-in-firebase-detail"),
    path("partial_update/<str:queue_id>/", QueueInFirestorePartialUpdateView.as_view(), name="queue-in-firebase-partial_update"),
]