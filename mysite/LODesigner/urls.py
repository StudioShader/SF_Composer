from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # path("index/", views.index, name="main_index"),
    path("lo_designer/add_cycle_object/", views.add_cycle_object, name="add_cycle_object"),
    path("lo_designer/delete_all_cycle_objects/", views.delete_all_cycle_objects, name="delete_all_cycle_objects"),
    path("lo_designer/get_object_by_key/", views.get_object_by_key, name="get_object_by_key"),
    path("lo_designer/cycle_objects/", views.cycle_objects, name="cycle_objects"),
    path('lo_designer/<str:project_key>', views.lodesigner, name='lo_designer'),
    path("lo_designer/publish/<str:project_key>", views.publish_project, name="publish_project"),
    path('simulate/<str:project_key>', views.simulate, name='simulate'),
    path("sign-up/", views.sign_up, name="sign_up"),
    path("create_project/", views.create_project, name="create_project"),
    path("published/", views.published_projects, name="published"),
]