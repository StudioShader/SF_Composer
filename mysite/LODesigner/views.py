from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    context = {"lo": [1, 2, 3]}
    return render(request, "index.html", context)