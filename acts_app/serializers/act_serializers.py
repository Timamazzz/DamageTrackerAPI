from rest_framework import serializers

from DamageTrackerAPI.utils.fields import PhoneField
from acts_app.models import Act, SignCode, BuildingType
from drf_writable_nested.serializers import WritableNestedModelSerializer

from acts_app.serializers.damage_serializers import DamageSerializer, DamageCreateSerializer
from datetime import datetime
import random
import string
from django.utils import timezone

from users_app.serializers.user_serializers import VictimSerializer


class ActSerializer(serializers.ModelSerializer):
    class Meta:
        model = Act
        fields = '__all__'


class ActListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Act
        fields = ('number', 'employee')


class ActCreateSerializer(WritableNestedModelSerializer):
    victim = VictimSerializer()
    damages = DamageCreateSerializer()

    class Meta:
        model = Act
        fields = ('municipality', 'address', 'building_type', 'victim', 'damages')


class ActUpdateSerializer(WritableNestedModelSerializer):
    damages = DamageCreateSerializer()

    class Meta:
        model = Act
        fields = ('id',) + ActCreateSerializer.Meta.fields
