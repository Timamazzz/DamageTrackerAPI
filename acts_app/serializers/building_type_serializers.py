from rest_framework import serializers

from acts_app.models import BuildingType


class BuildingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingType
        fields = '__all__'

