from django.urls import path 
from the_queue.views import (QueueInFirebaseListCreateView, QueueInFirestoreDetailView)


urlpatterns = [
    path("", QueueInFirebaseListCreateView.as_view(), name="queue-in-firebase-list-create"),
    path("<str:queue_id>/", QueueInFirestoreDetailView.as_view(), name="queue-in-firebase-detail"),
]