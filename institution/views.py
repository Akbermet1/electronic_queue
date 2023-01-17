from django.shortcuts import render


def list_institutions(request):
    return render(request, "list_institutions.html")


def test_view(request):
    return render(request, "base.html")
