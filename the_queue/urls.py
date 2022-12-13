from django.urls import path 
from the_queue.views import (QueueInFirebaseListCreateView)


urlpatterns = [
    path("", QueueInFirebaseListCreateView.as_view(), name="queue-in-firebase-list-create"),
    # path("list_create/<str:institution_id>/", QueueInFirebaseListCreateView.as_view(), name="queue-in-firebase-list-create"),
]