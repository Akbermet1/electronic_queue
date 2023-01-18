from django.urls import path 
from the_queue.views import (QueueInFirestoreListCreateView, QueueInFirestoreDetailView, QueueInFirestorePartialUpdateView,
                            CustomerInQueueCreateView, CustomerInQueueDetailView, QueueInFirestoreMoveView, 
                            put_customer_in_queue_view, )


urlpatterns = [
    path("", QueueInFirestoreListCreateView.as_view(), name="queue-in-firebase-list-create"),
    path("<str:queue_id>/customer/", put_customer_in_queue_view, name="put-customer-in-queue"),
    # path("<str:queue_id>/customer/", CustomerInQueueCreateView.as_view(), name="customer-in-queue-list-create"),
    path("<str:queue_id>/customer/<str:confirmation_code>/", CustomerInQueueDetailView.as_view(), name="customer-in-queue-detail"),
    path("<str:queue_id>/move/", QueueInFirestoreMoveView.as_view(), name="queue-in-firebase-move"),
    path("<str:queue_id>/", QueueInFirestoreDetailView.as_view(), name="queue-in-firebase-detail"),
    path("partial_update/<str:queue_id>/", QueueInFirestorePartialUpdateView.as_view(), name="queue-in-firebase-partial_update"),
]