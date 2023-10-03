import uuid
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from user.forms import RegisterUserForm
from electronic_queue.firestore import db
from institution.views import INSTITUTIONS_COLLECTION_ID


def register_user_view(response):
    if response.method == "POST":
        form = RegisterUserForm(response.POST)
        if form.is_valid():
            form.save()
            institution_name = form.cleaned_data['institution_name']
            institution_id = str(uuid.uuid4())[:10]
            institution_ref = db.collection(INSTITUTIONS_COLLECTION_ID).document(institution_id)
            institution_fields = {
                "institution_id": institution_id,
                "name": institution_name,
                "branches": [],
                "queues": [],
            }
            institution_ref.set(institution_fields)
            # change the name of the view that the user gets redirected to 
            return redirect("list-institutions")
    else:
        form = RegisterUserForm()

    return render(response, "./register/register.html", {"form": form}) 

