from rest_framework import serializers

from .models import LODevice

class LODeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LODevice
        fields = ['id', 'pk', 'type', 'theta', 'phi', 'n', 'input_type', 'x', 'y', 'project_key']