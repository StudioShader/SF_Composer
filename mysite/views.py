from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.clickjacking import (
    xframe_options_sameorigin,
    xframe_options_exempt,
)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
import json
from json import JSONEncoder
from django.core import serializers
from django.http import JsonResponse
from rest_framework.renderers import JSONRenderer
from simulation import SFSimulation as sfs
import numpy


def home(request):
    return redirect("/login")