from rest_framework import serializers

from acts_app.models import Act
from drf_writable_nested.serializers import WritableNestedModelSerializer

from acts_app.serializers.damage_serializers import DamageSerializer, DamageCreateSerializer


class ActSerializer(serializers.ModelSerializer):
    class Meta:
        model = Act
        fields = '__all__'


class ActListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Act
        fields = ('number', 'employee')


class ActCreateSerializer(WritableNestedModelSerializer):
    damages = DamageCreateSerializer()

    class Meta:
        model = Act
        fields = ('municipality', 'address', 'building_type', 'victim', 'damages')
