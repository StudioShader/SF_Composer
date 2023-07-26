from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # path("index/", views.index, name="main_index"),
    path('lo_designer/', views.lodesigner, name='lo_designer'),
    path("sign-up/", views.sign_up, name="sign_up"),
    path("create_project", views.create_project, name="create_project"),
    path("add_cycle_object", views.add_cycle_object, name="add_cycle_object")
]