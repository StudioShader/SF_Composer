from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin

def index(request):
    context = {"lo": [1, 2, 3]}
    return render(request, "projects_list.html", context)

@xframe_options_sameorigin
def lodesigner(request):
    return render(request, "lo_designer.html")