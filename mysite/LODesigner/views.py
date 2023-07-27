from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin, xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm, ProjectForm
from .models import Project, LOCircuit, LOConnection, LODevice

def index(request):
    projects = Project.objects.all()
    return render(request, "projects_list.html", {"projects": projects})

@xframe_options_sameorigin
def lodesigner(request, project_key):
    print(project_key)
    return render(request, "lo_designer.html", {"project_key": project_key})

def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/LODesigner')
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {"form": form})

@login_required(login_url="/login")
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect("/LODesigner")
    else:
        form = ProjectForm()
    return render(request, "create_project.html", {"form": form})

@login_required(login_url="/login")
def home(request):
    return redirect(request, '/LODesigner/index')

@csrf_exempt
@login_required(login_url="/login")
def add_cycle_object(request):
    if request.method == 'POST':
        print("it was posted")
        print(request.POST)
        if request.POST['object_type'] == "LODevice":
            print("even passed object type")
            lodevice = LODevice(project_key=request.POST['parent_key'])
    return HttpResponse("Some http response data")