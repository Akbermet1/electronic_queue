import uuid
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from user.forms import RegisterUserForm
from electronic_queue.firestore import db
from institution.views import INSTITUTIONS_COLLECTION_ID, BRANCH_COLLECTION_ID
from django.contrib.auth.decorators import login_required



def register_user_view(response):
    if response.method == "POST":
        form = RegisterUserForm(response.POST)
        if form.is_valid():
            form.save()
            institution_name = form.cleaned_data['institution_name']
            institution_email = form.cleaned_data["email"]
            institution_id = str(uuid.uuid4())[:10]
            institution_ref = db.collection(INSTITUTIONS_COLLECTION_ID).document(institution_id)
            institution_fields = {
                "institution_id": institution_id,
                "name": institution_name,
                "email": institution_email,
                "branches": [],
                "queues": [],
            }
            institution_ref.set(institution_fields)
            # change the name of the view that the user gets redirected to 
            return redirect("list-institutions")
    else:
        form = RegisterUserForm()

    return render(response, "./register/register.html", {"form": form}) 


@login_required(login_url="/api/user/login/")
def manage_user_account_view(request):
    institution_email = request.user.email
    institution_ref = db.collection(INSTITUTIONS_COLLECTION_ID)
    institution_matches = institution_ref.where("email", "==", institution_email).stream()
    all_institutions = [institution.to_dict() for institution in institution_matches]

    institution_doc = {}
    branches = []
    true_match_found = False
    if len(all_institutions) == 1:
        institution_doc = all_institutions[0]
        true_match_found = True

        institution_id = institution_doc.get("institution_id")
        branches_ref = db.collection(BRANCH_COLLECTION_ID)
        docs_of_branches = branches_ref.where("institution_id", "==", institution_id).stream()
        branches = [branch.to_dict() for branch in docs_of_branches]
    
    print(institution_doc)
    context = {
        "institution": institution_doc,
        "branches": branches,
        "true_match_found": true_match_found,
    }
    print(request.user)
    print(request.user.email)
    return render(request, "./institution/manage_account.html", context=context)

