from typing import List
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from branch.views import BRANCH_COLLECTION_ID
from electronic_queue.firestore import db
from the_queue.views import INSTITUTIONS_COLLECTION_ID, QUEUES_COLLECTION_ID
from the_queue.serializers import QueueInFirebaseSerializer


def list_institutions(request):
    all_institutions = db.collection(INSTITUTIONS_COLLECTION_ID).stream()
    list_of_institutions = [institution.to_dict() for institution in all_institutions]

    context = {
        "alphabet": [ chr(char) for char in range(65, 91)],
        "institutions": list_of_institutions,
    }
    return render(request, "./institution/list_institutions.html", context=context)


def test_view(request):
    return render(request, "base.html")


def order_days_of_week(all_days_of_week: List):
    order_of_the_days = {}
    for day in all_days_of_week:
        if day.lower()[:3] == "mon": 
            order_of_the_days[day] = 1
        elif day.lower()[:3] == "tue":
            order_of_the_days[day] = 2
        elif day.lower()[:3] == "wed":
            order_of_the_days[day] = 3
        elif day.lower()[:3] == "thu":
            order_of_the_days[day] = 4
        elif day.lower()[:3] == "fri":
            order_of_the_days[day] = 5
        elif day.lower()[:3] == "sat":
            order_of_the_days[day] = 6
        elif day.lower()[:3] == "sun":
            order_of_the_days[day] = 7
    return order_of_the_days


@api_view(["GET"])
def list_all_branches_of_institution_view(request, institution_id):
    branches_ref = db.collection(BRANCH_COLLECTION_ID)
    docs_of_branches = branches_ref.where("institution_id", "==", institution_id).stream()
    branches = [branch.to_dict() for branch in docs_of_branches]

    # sorting the days of the week to display them in the correct order 
    if len(branches) > 0:
        days_of_the_week = branches[0].get("working_hours")
        all_days_of_week = [key for key in days_of_the_week.keys()]
        order_of_the_days = order_days_of_week(all_days_of_week)
    else:
        order_of_the_days = {}
    instituion = db.collection(INSTITUTIONS_COLLECTION_ID).document(institution_id).get().to_dict()
    context = {
        "branches": branches,
        "instituion": instituion,
        "order_of_the_days": order_of_the_days
    }
    return render(request, "./institution/list_branches.html", context=context)


@api_view(["GET"])
def manage_institutions_queue(request, institution_id, queue_id):
    queue_doc = db.collection(QUEUES_COLLECTION_ID).document(queue_id).get()

    if queue_doc.exists:
        serializer = QueueInFirebaseSerializer(data=queue_doc.to_dict())
        serializer.is_valid(raise_exception=True)
        return Response(queue_doc.to_dict())
    return Response("Provided queue ID didn't match any queue!", status=status.HTTP_406_NOT_ACCEPTABLE)
