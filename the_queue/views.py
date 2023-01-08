import uuid
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from firebase_admin import firestore

from electronic_queue.firestore import db
from the_queue.serializers import QueueInFirebaseSerializer

INSTITUTIONS_COLLECTION_ID = "institutions"
QUEUES_COLLECTION_ID = "queues"


def check_if_institution_exists(institution_id):
    collection_title = "institutions"

    if db.collection(collection_title).document(institution_id).get().exists:
        return True
    return False


class QueueInFirestoreListCreateView(APIView):
    def get(self, request):
        all_queues = db.collection(QUEUES_COLLECTION_ID).stream()
        list_of_queues = [queue.to_dict() for queue in all_queues]

        return Response(list_of_queues, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        serializer = QueueInFirebaseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        queue_id = serializer.data.get("queue_id")
        try:
            if not db.collection(QUEUES_COLLECTION_ID).document(queue_id).get().exists:
                queue_ref =  db.collection(QUEUES_COLLECTION_ID).document(queue_id)
                queue_ref.set(serializer.data)
            else:
                return Response("Queue not created", status=status.HTTP_204_NO_CONTENT)
        except Exception as exception:
            return Response(f"Something went wrong when creating a document in the collection.\nException: {exception}")

        return Response(queue_ref.get().to_dict(), status=status.HTTP_200_OK)


class QueueInFirestoreDetailView(APIView):
    def get(self, request, queue_id):
        queue = db.collection(QUEUES_COLLECTION_ID).document(queue_id).get()

        if queue.exists:
            return Response(queue.to_dict(), status=status.HTTP_200_OK)
        else:
            return Response("Provided ID didn't match any queue!", status=status.HTTP_406_NOT_ACCEPTABLE)

    
    def delete(self, request, queue_id):
        queue_ref = db.collection(QUEUES_COLLECTION_ID).document(queue_id)

        if queue_ref.get().exists:
            print("queue contents:\n", queue_ref.get().to_dict())
            queue_ref.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("Provided ID didn't match any queue!", status=status.HTTP_406_NOT_ACCEPTABLE)


class QueueInFirestorePartialUpdateView(APIView):
    def post(self, request, queue_id):
        new_name = request.data.get("new_name", None)
        customer_count_visible = request.data.get("customer_count_visible", None)
        queue_ref = db.collection(QUEUES_COLLECTION_ID).document(queue_id)

        if new_name is None and customer_count_visible is None:
            return Response(status=status.HTTP_204_NO_CONTENT)

        if queue_ref.get().exists:
            if new_name is not None:
                queue_ref.update({
                    "name": new_name
                })
        
            if customer_count_visible is not None and isinstance(customer_count_visible, bool):
                queue_ref.update({
                    "customer_count_visible": customer_count_visible
                })

            return Response(queue_ref.get().to_dict(), status=status.HTTP_200_OK)
        else:
            return Response("Provided ID didn't match any queue!", status=status.HTTP_406_NOT_ACCEPTABLE)


class CustomerInQueueCreateView(APIView):
    def post(self, request, queue_id):
        recipients_email = request.data.get("recipients_email", None)

        if recipients_email is not None and queue_id is not None:
            queue_ref = db.collection(QUEUES_COLLECTION_ID).document(queue_id)

            if not queue_ref.get().exists:
                return Response("An invalid queue_id was provided.", status=status.HTTP_204_NO_CONTENT)

            queue_doc = queue_ref.get().to_dict().get("name")
            institution_id = queue_ref.get().to_dict().get("institution_id")
            institution_doc = db.collection(INSTITUTIONS_COLLECTION_ID).document(institution_id).get().to_dict()
            institution_name = institution_doc.get("name", None)
            confirmation_code = str(uuid.uuid4())[:10]

            queue_ref.update({
                "queue": firestore.ArrayUnion([confirmation_code])
                })

            send_mail(
                subject=f"Confirmation of reserving a place in {queue_doc} queue of {institution_name}",
                message=f"Your confirmation code: {confirmation_code}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[recipients_email],
                fail_silently=False
            )
            return Response("You have been added to the queue, and your confimation code has been sent to the email that you provided.", 
                            status=status.HTTP_200_OK)
        else:
            return Response("Enter the email of a recepient and the ID of the queue!", status=status.HTTP_204_NO_CONTENT)
