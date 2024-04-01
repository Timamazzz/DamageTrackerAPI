from rest_framework import serializers

from acts_app.models import Municipality


class MunicipalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipality
        fields = '__all__'

