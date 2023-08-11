from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from branch.views import BRANCH_COLLECTION_ID
from electronic_queue.firestore import db
from the_queue.views import INSTITUTIONS_COLLECTION_ID


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


@api_view(["GET"])
def list_all_branches_of_institution_view(request, institution_id):
    branches_ref = db.collection(BRANCH_COLLECTION_ID)
    docs_of_branches = branches_ref.where("institution_id", "==", institution_id).stream()
    branches = [branch.to_dict() for branch in docs_of_branches]
    instituion = db.collection(INSTITUTIONS_COLLECTION_ID).document(institution_id).get().to_dict()
    context = {
        "branches": branches,
        "instituion": instituion
    }
    return render(request, "./institution/list_branches.html", context=context)
