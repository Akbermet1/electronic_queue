from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from electronic_queue.firestore import db
from institution.views import INSTITUTIONS_COLLECTION_ID


class RegisterUserForm(UserCreationForm):
    email = forms.EmailField()
    institution_name = forms.CharField()

    def clean_institution_name(self):
        institution_name = self.cleaned_data["institution_name"]
        institutions_ref = db.collection(INSTITUTIONS_COLLECTION_ID)
        docs_of_institutions = institutions_ref.where("name", "==", institution_name).stream()
        all_docs = [doc.to_dict() for doc in docs_of_institutions]
        if len(all_docs) > 0:
            raise ValidationError(("This institution is already registered: %(value)s"),
                                    code="invalid",
                                    params={"value": institution_name},
            )
        return institution_name

    class Meta:
        model = User
        fields = ["institution_name", "email", "username", "password1", "password2"]
