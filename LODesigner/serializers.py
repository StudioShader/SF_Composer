from rest_framework import serializers

from .models import LODevice, Project

class LODeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LODevice
        fields = ['id', 'pk', 'type', 'theta', 'phi', 'n', 'input_type', 'x', 'y', 'project_key']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'user', 'created', 'updated', 'published']