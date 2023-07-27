from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    published = models.BooleanField(default = False)
    # png = models.TextField()
    def __str__(self):
        return self.name + '\n' + self.description
    

class LODevice(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    type = models.CharField(max_length=50)
    theta = models.CharField(max_length=50)
    phi = models.CharField(max_length=50)
    n = models.CharField(max_length=50)
    input_type = models.CharField(max_length=50, default = "0")
    x = models.IntegerField(default = 100)
    y = models.IntegerField(default = 100)
    project_key = models.ForeignKey(Project, on_delete=models.CASCADE)

class LOConnection(models.Model):
    line_json = models.TextField()

class LOCircuit(models.Model):
    name = models.CharField(max_length=50)
    modes = models.IntegerField()
    matrix = models.TextField()
    inv = models.TextField()
    result = models.TextField()
    fidelities = models.TextField()
    cgate_run_x = models.TextField()
    cgate_run_y = models.TextField()
    cgate_run_z = models.TextField()