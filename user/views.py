from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from user.forms import RegisterUserForm


def register_user_view(response):
    if response.method == "POST":
        form = RegisterUserForm(response.POST)
        if form.is_valid():
            form.save()
            # change the name of the view that the user gets redirected to 
            return redirect("list-institutions")
    else:
        form = RegisterUserForm()

    return render(response, "./register/register.html", {"form": form}) 

