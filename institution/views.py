from django.shortcuts import render
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
