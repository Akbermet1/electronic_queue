from typing import List
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from branch.views import BRANCH_COLLECTION_ID
from electronic_queue.firestore import db
from the_queue.views import (INSTITUTIONS_COLLECTION_ID, QUEUES_COLLECTION_ID, move_queue, update_queue_name)
from the_queue.serializers import QueueInFirebaseSerializer
from institution.utils import confirm_queue_owner


def list_institutions(request):
    all_institutions = db.collection(INSTITUTIONS_COLLECTION_ID).stream()
    list_of_institutions = [institution.to_dict() for institution in all_institutions]

    context = {
        "alphabet": [ chr(char) for char in range(65, 91)],
        "institutions": list_of_institutions,
    }
    return render(request, "./institution/list_institutions.html", context=context)


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


@login_required(login_url="/api/user/login/")
@api_view(["GET", "POST"])
def manage_institutions_queue(request, institution_id, queue_id):
    user_email = request.user.email
    user_owns_queue = confirm_queue_owner(queue_id=queue_id, institution_email=user_email)

    if not user_owns_queue:
        return redirect("list-institutions")

    queue_doc = db.collection(QUEUES_COLLECTION_ID).document(queue_id)
    context = {
        "line_moved": False,
        "institution_id": institution_id,
    }

    if request.method == "POST":
        new_queue_name = request.POST["new_title"]
        checked_input_fields = request.POST.getlist("checks")
        move_this_queue = True if "move_queue" in checked_input_fields else False
        visible_customer_count = True if "visible_customer_count" in checked_input_fields else False

        if move_this_queue:
            removed_confirmation_code = move_queue(queue_id)
            if removed_confirmation_code is not None:
                context["line_moved"] = True
                context["confirmation_code"] = removed_confirmation_code
        
        if queue_doc.get().exists:
            queue_content = queue_doc.get().to_dict()
            current_customer_count_visible = queue_content.get("customer_count_visible")

            if visible_customer_count:
                queue_doc.update({
                    "customer_count_visible": not current_customer_count_visible
                })

            if new_queue_name:
                current_queue_name = queue_content.get("name")
                branch_id = queue_content.get("branch_id")
                update_queue_name(branch_id=branch_id, queue_id=queue_id, old_name=current_queue_name, new_name=new_queue_name)


    if queue_doc.get().exists:
        queue_content = queue_doc.get().to_dict()
        serializer = QueueInFirebaseSerializer(data=queue_content)
        serializer.is_valid(raise_exception=True)
        branch_address = serializer.retrieve_branch_address(serializer.data.get("branch_id"))
        context.update(queue_content)
        
        if branch_address:
            context.update({"branch_address": branch_address})
        return render(request, "./queue/manage_queue.html", context=context)
    return Response("Provided queue ID didn't match any queue!", status=status.HTTP_406_NOT_ACCEPTABLE)
