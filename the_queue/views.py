import uuid
import string
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer
from firebase_admin import firestore

from electronic_queue.firestore import db
from the_queue.serializers import QueueInFirebaseSerializer
from branch.views import BRANCH_COLLECTION_ID

INSTITUTIONS_COLLECTION_ID = "institutions"
QUEUES_COLLECTION_ID = "queues"
CONFIRMATION_CODES_COLLECTION_ID = "confirmation_codes"


def check_if_institution_exists(institution_id):
    collection_title = "institutions"

    if db.collection(collection_title).document(institution_id).get().exists:
        return True
    return False


class QueueInFirestoreListCreateView(APIView):
    # renderer_classes = [TemplateHTMLRenderer]
    # template_name = 'queue_list.html'
    def get(self, request):
        all_queues = db.collection(QUEUES_COLLECTION_ID).stream()
        list_of_queues = [queue.to_dict() for queue in all_queues]

        return Response({"queues": list_of_queues}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        serializer = QueueInFirebaseSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        queue_id = serializer.data.get("queue_id")
        queue_name = serializer.data.get("name")
        branch_id = serializer.data.get("branch_id")
        try:
            if not db.collection(QUEUES_COLLECTION_ID).document(queue_id).get().exists:
                queue_ref =  db.collection(QUEUES_COLLECTION_ID).document(queue_id)
                queue_ref.set(serializer.data)
            else:
                return Response("Queue was not created", status=status.HTTP_204_NO_CONTENT)

            branch_snapshot = db.collection(BRANCH_COLLECTION_ID).document(branch_id)
            if branch_snapshot.get().exists == True:
                branch_snapshot.update({"queues": firestore.ArrayUnion([{queue_id: queue_name}])})
            else:
                return Response("The provided branch doesn't exist. Couldn't add info about the queue to the branch. But the queue was successfully created.", status=status.HTTP_204_NO_CONTENT)
        except Exception as exception:
            return Response(f"Something went wrong when creating a document in the collection.\nException: {exception}")

        return Response(queue_ref.get().to_dict(), status=status.HTTP_200_OK)


class QueueInFirestoreDetailView(APIView):
    def get(self, request, queue_id):
        queue = db.collection(QUEUES_COLLECTION_ID).document(queue_id).get()

        if queue.exists:
            return Response({"queue": queue.to_dict()}, status=status.HTTP_200_OK)
        else:
            return Response("Provided ID didn't match any queue!", status=status.HTTP_406_NOT_ACCEPTABLE)

    
    def delete(self, request, queue_id):
        queue_ref = db.collection(QUEUES_COLLECTION_ID).document(queue_id)

        if queue_ref.get().exists:
            queue = queue_ref.get().to_dict()
            queue_name = queue.get("name")
            branch_id = queue.get("branch_id")

            branch_ref = db.collection(BRANCH_COLLECTION_ID).document(branch_id)
            if branch_ref.get().exists:
                branch_ref.update({
                    "queues": firestore.ArrayRemove([{queue_id: queue_name}])
                })
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


def put_customer_in_queue_view(request, queue_id):
    context = {
        "queue_exists": False,
        "email_sent": False
    }

    queue_ref = db.collection(QUEUES_COLLECTION_ID).document(queue_id)
    queue_doc = queue_ref.get().to_dict()
    context["queue_name"] = queue_doc.get("name")

    if request.method == "POST":
        recipients_email = request.POST.get("email", None)

        if recipients_email is not None and queue_id is not None:
            queue_ref = db.collection(QUEUES_COLLECTION_ID).document(queue_id)

            if queue_ref.get().exists:
                context["queue_exists"] = True
                context["email"] = recipients_email
                context["queue_id"] = queue_id

                queue_doc = queue_ref.get().to_dict().get("name")
                institution_id = queue_ref.get().to_dict().get("institution_id")
                institution_doc = db.collection(INSTITUTIONS_COLLECTION_ID).document(institution_id).get().to_dict()
                institution_name = institution_doc.get("name", None)
                confirmation_code = str(uuid.uuid4())[:10]

                queue_ref.update({
                    "queue": firestore.ArrayUnion([confirmation_code])
                })

                queue_ref.update({
                    "customer_count": firestore.Increment(1)
                })

                # save information about the confirmation code
                db.collection(CONFIRMATION_CODES_COLLECTION_ID).document(confirmation_code).set({"document_id": confirmation_code,
                                                                                                "user_email": recipients_email,
                                                                                                "user_phone_number": ""})

                send_mail(
                    subject=f"Confirmation of reserving a place in {queue_doc} queue of {institution_name}",
                    message=f"Your confirmation code: {confirmation_code}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[recipients_email],
                    fail_silently=False
                )
                context["email_sent"] = True

    return render(request, "./queue/put_customer_in_queue.html",
                context=context)


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

            # save information about the confirmation code
            db.collection(CONFIRMATION_CODES_COLLECTION_ID).document(confirmation_code).set({"document_id": confirmation_code,
                                                                                            "user_email": recipients_email,
                                                                                            "user_phone_number": ""})

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


class CustomerInQueueDetailView(APIView):
    def get(self, request, queue_id, confirmation_code):
        queue_ref = db.collection(QUEUES_COLLECTION_ID).document(queue_id)
        if not queue_ref.get().exists:
            return Response("Invalid queue_id was provied.", status=status.HTTP_204_NO_CONTENT)
        
        the_queue = queue_ref.get().to_dict().get("queue")
        
        if confirmation_code in the_queue:
            customer_index = the_queue.index(confirmation_code)
            message = ""

            if customer_index == 0:
                message = "are no people"
            elif customer_index == 1:
                message = "is 1 person"
            else:
                message = f"are {customer_index} people"

            return Response({
                "message": f"There {message} ahead of you in line.",
                "number_in_line": customer_index + 1 
            }, status=status.HTTP_200_OK)
        else:
            return Response("Invalid confirmation_code was provied.", status=status.HTTP_204_NO_CONTENT)    

    
    def delete(self, request, queue_id, confirmation_code):
        queue_ref = db.collection(QUEUES_COLLECTION_ID).document(queue_id)
        if not queue_ref.get().exists:
            return Response("Invalid queue_id was provied.", status=status.HTTP_204_NO_CONTENT)
        
        queue_ref.update(
            {
                "queue": firestore.ArrayRemove([confirmation_code])    
            }
        )

        return Response(f"Customer with the confimation code: {confirmation_code} was removed from the queue.", status=status.HTTP_204_NO_CONTENT)


class QueueInFirestoreMoveView(APIView):
    def delete(self, request, queue_id):
        queue_ref = db.collection(QUEUES_COLLECTION_ID).document(queue_id)
        if not queue_ref.get().exists:
            return Response("Invalid queue_id was provied.", status=status.HTTP_204_NO_CONTENT)

        the_queue = queue_ref.get().to_dict().get("queue", None)

        if the_queue is None:
            return Response("Something is wrong with the queue. Please contact the admin.", status=status.HTTP_204_NO_CONTENT)

        confirmation_code = the_queue.pop(0) if len(the_queue) >= 1 else None

        if confirmation_code is not None:
            queue_ref.update(
                {
                    "queue": firestore.ArrayRemove([confirmation_code])    
                }
            )
            queue_ref.update(
                {
                    "customer_count": firestore.Increment(-1)    
                }
            )
            return Response(f"Customer with the confimation code: {confirmation_code} was removed from the queue.", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("The queue is empty.", status=status.HTTP_204_NO_CONTENT)


def move_queue(queue_id):
    queue_ref = db.collection(QUEUES_COLLECTION_ID).document(queue_id)
    if queue_ref.get().exists:
        the_queue = queue_ref.get().to_dict().get("queue", None)

        if the_queue is not None:
            confirmation_code = the_queue.pop(0) if len(the_queue) >= 1 else None

            if confirmation_code is not None:
                queue_ref.update(
                    {
                        "queue": firestore.ArrayRemove([confirmation_code])    
                    }
                )
                queue_ref.update(
                    {
                        "customer_count": firestore.Increment(-1)    
                    }
                )
                return confirmation_code
    return None


def update_queue_name(branch_id, queue_id, old_name,  new_name):
    branch_snap = db.collection(BRANCH_COLLECTION_ID).document(branch_id)
    branch_ref = branch_snap.get()

    if branch_ref.exists:
        branch_doc = branch_ref.to_dict()
        queues_of_branch = branch_doc.get("queues")
        
        queue_snap = db.collection(QUEUES_COLLECTION_ID).document(queue_id)
        queue_ref = queue_snap.get()
        if queue_ref.exists and queues_of_branch:
            branches_ref = db.collection(BRANCH_COLLECTION_ID)
            result = branches_ref.where("queues", "array_contains", {queue_id: old_name}).stream()
            list_result = [q.to_dict() for q in result]

            if list_result:
                queue_snap.update({
                    "name": new_name
                })
                branch_snap.update({
                    "queues": firestore.ArrayRemove([{queue_id: old_name}])
                })

                branch_snap.update({
                    "queues": firestore.ArrayUnion([{queue_id: new_name}])
                })
                return True
        else:
            return False

