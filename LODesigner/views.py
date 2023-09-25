from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.clickjacking import (
    xframe_options_sameorigin,
    xframe_options_exempt,
)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm, ProjectForm
from .models import Project, LOCircuit, LOConnection, LODevice
from .serializers import LODeviceSerializer, ProjectSerializer
import json
from json import JSONEncoder
from django.core import serializers
from django.http import JsonResponse
from rest_framework.renderers import JSONRenderer
from simulation import SFSimulation as sfs
import numpy


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


@login_required(login_url="/login")
def index(request):
    projects = Project.objects.filter(user=request.user)
    serialized_projects = ProjectSerializer(projects, many=True)
    final_json = json.dumps(serialized_projects.data)
    return render(
        request,
        "projects_list.html",
        {"projects": projects, "projects_json": final_json, "only_published": 'false'},
    )

def home(request):
    return redirect("/login")

def about(request):
    return render(request, "about.html")

@xframe_options_sameorigin
def lodesigner(request, project_key):
    print(request.GET["only_published"])
    print(type(request.GET["only_published"]))
    if request.GET["only_published"] == 'false':
        return render(request, "lo_designer.html", {"project_key": project_key, "only_published": request.GET["only_published"]})
    if request.GET["only_published"] == "'false'":
        return render(request, "lo_designer.html", {"project_key": project_key, "only_published": 'false'})
    return render(request, "lo_designer.html", {"project_key": project_key, "only_published": 'true'})


def sign_up(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/LODesigner")
    else:
        form = RegisterForm()
    return render(request, "registration/sign_up.html", {"form": form})


def published_projects(request):
    projects = Project.objects.filter(published=True)
    serialized_projects = ProjectSerializer(projects, many=True)
    final_json = json.dumps(serialized_projects.data)
    return render(
        request,
        "projects_list.html",
        {"projects": projects, "projects_json": final_json, "only_published": 'true'},
    )


@login_required(login_url="/login")
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect("/LODesigner")
    else:
        form = ProjectForm()
    return render(request, "create_project.html", {"form": form})

@csrf_exempt
@login_required(login_url="/login")
def publish_project(request, project_key):
    if request.method == "POST":
        if request.user.groups.filter(name='mod').exists():
            projects = Project.objects.get(pk=project_key)
            projects.published = True
            projects.save()
            return HttpResponse("Project was succesfully published")
        else:
            return HttpResponse("You are not authorized to publish projects, please contact ivanogloblin2022@gmail.com")

@csrf_exempt
@login_required(login_url="/login")
def add_cycle_object(request):
    if request.method == "POST":
        if request.POST["object_type"] == "LODevice":
            current_project = Project.objects.get(pk=request.POST["parent_key"])
            lodevice = LODevice(project_key=current_project)
            obj = json.loads(request.POST["data"])
            for key in obj:
                setattr(lodevice, key, obj[key])
            lodevice.save()
        if request.POST["object_type"] == "LOConnection":
            current_project = Project.objects.get(pk=request.POST["parent_key"])
            connection = LOConnection(project_key=current_project)
            obj = json.loads(request.POST["data"])
            for key in obj:
                setattr(connection, key, obj[key])
            connection.save()
    return HttpResponse("Some http response data")


@csrf_exempt
@login_required(login_url="/login")
def delete_all_cycle_objects(request):
    if request.method == "POST":
        print(request.POST)
        project_devices = LODevice.objects.filter(
            project_key=request.POST["parent_key"]
        )
        for device in project_devices:
            device.delete()
        project_connections = LOConnection.objects.filter(
            project_key=request.POST["parent_key"]
        )
        for connection in project_connections:
            connection.delete()
    return HttpResponse("Some http response data")


@csrf_exempt
@login_required(login_url="/login")
def get_object_by_key(request):
    if request.method == "GET":
        if Project.objects.filter(id=request.GET["key"]).exists():
            current_project = Project.objects.get(pk=request.GET["key"])
            serialized_obj = serializers.serialize("json", [current_project])
            # print(JsonResponse(serialized_obj, safe=False))
            return JsonResponse(serialized_obj, safe=False)
    return HttpResponse("None project was found")


@csrf_exempt
@login_required(login_url="/login")
def cycle_objects(request):
    print("cycle_objects")
    if request.method == "GET":
        if request.GET["object_type"] == "LODevice":
            devices = LODevice.objects.filter(project_key=request.GET["parent_key"])
            # serialized_devices = serializers.serialize('json', devices)
            serialized_devices = LODeviceSerializer(devices, many=True)
            print(JsonResponse(serialized_devices.data, safe=False))
            return JsonResponse(serialized_devices.data, safe=False)
        if request.GET["object_type"] == "LOConnection":
            connections = LOConnection.objects.filter(
                project_key=request.GET["parent_key"]
            )
            serialized_connections = serializers.serialize("json", connections)
            # print(JsonResponse(serialized_devices, safe=False))
            return JsonResponse(serialized_connections, safe=False)
    return HttpResponse("None devices was found")


# @xframe_options_sameorigin
@csrf_exempt
@login_required(login_url="/login")
def simulate(request, project_key):
    if request.method == "GET":
        if project_key == -1:
            return HttpResponse("none project selected yet, please select a project")
        print(request.GET.get("backend"))
        if project_key != -1:
            devices = LODevice.objects.filter(project_key=project_key)
            connections = LOConnection.objects.filter(project_key=project_key)
            # sfs.Circuit().simulate()
            print(request.GET.get("measurements"))
            result = sfs.Circuit(
                name=("circuit" + str(project_key)),
                backend=request.GET.get("backend"),
                simulation_option=request.GET.get("measurements"),
                number_of_shots=request.GET.get("shots"),
                cutoff_dim=request.GET.get("cutoff_dim"),
            ).construct_circuit(project_key, devices, connections)
            # serialized_U = [[str(element) for element in string] for string in U]
            # data = json.dumps(U, cls=NumpyArrayEncoder)
            # return JsonResponse(data, safe=False)
            return HttpResponse(result)
        return HttpResponse("none project selected yet")
    return HttpResponse("not a Get request")
