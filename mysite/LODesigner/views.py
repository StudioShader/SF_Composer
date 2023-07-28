from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin, xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm, ProjectForm
from .models import Project, LOCircuit, LOConnection, LODevice
import json
from django.core import serializers
from django.http import JsonResponse

def index(request):
    projects = Project.objects.all()
    return render(request, "projects_list.html", {"projects": projects})

@xframe_options_sameorigin
def lodesigner(request, project_key):
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
        if request.POST['object_type'] == "LODevice":
            current_project = Project.objects.get(pk=request.POST['parent_key'])
            lodevice = LODevice(project_key=current_project)
            obj = json.loads(request.POST['data'])
            for key in obj:
                setattr(lodevice, key, obj[key])
            lodevice.save()
        if request.POST['object_type'] == "LOConnection":
            current_project = Project.objects.get(pk=request.POST['parent_key'])
            connection = LOConnection(project_key=current_project)
            obj = json.loads(request.POST['data'])
            for key in obj:
                print(obj[key])
                setattr(connection, key, obj[key])
            connection.save()
    return HttpResponse("Some http response data")

@csrf_exempt
@login_required(login_url="/login")
def delete_all_cycle_objects(request):
    if request.method == 'POST':
        print(request.POST)
        project_devices = LODevice.objects.filter(project_key=request.POST['parent_key'])
        for device in project_devices:
            device.delete()
        project_connections = LOConnection.objects.filter(project_key=request.POST['parent_key'])
        for connection in project_connections:
            connection.delete()
    return HttpResponse("Some http response data")

@csrf_exempt
@login_required(login_url="/login")
def get_object_by_key(request):
    if request.method == 'GET':
        if Project.objects.filter(id=request.GET['key']).exists():
            current_project = Project.objects.get(pk=request.GET['key'])
            serialized_obj = serializers.serialize('json', [current_project])
            print(JsonResponse(serialized_obj, safe=False))
            return JsonResponse(serialized_obj, safe=False)
    return HttpResponse("None project was found")


@csrf_exempt
@login_required(login_url="/login")
def cycle_objects(request):
    if request.method == 'GET':
        if request.GET['object_type'] == "LODevice":
            devices = LODevice.objects.filter(project_key=request.GET['parent_key'])
            serialized_devices = serializers.serialize('json', devices)
            # print(JsonResponse(serialized_devices, safe=False))
            return JsonResponse(serialized_devices, safe=False)
        if request.GET['object_type'] == "LOConnection":
            connections = LOConnection.objects.filter(project_key=request.GET['parent_key'])
            serialized_connections = serializers.serialize('json', connections)
            # print(JsonResponse(serialized_devices, safe=False))
            return JsonResponse(serialized_connections, safe=False)
    return HttpResponse("None devices was found")