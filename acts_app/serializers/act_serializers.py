from drf_writable_nested import NestedCreateMixin
from rest_framework import serializers
from acts_app.models import Act
from drf_writable_nested.serializers import WritableNestedModelSerializer
from acts_app.serializers.damage_serializers import DamageCreateSerializer, DamageRetrieveSerializer, \
    DamagePdfSerializer
from docs_app.serializers.doc_serializers import ActImageSerializer
from users_app.serializers.user_serializers import VictimSerializer, EmployeeSerializer
from datetime import datetime
import random
import string


class ActSerializer(serializers.ModelSerializer):
    class Meta:
        model = Act
        fields = '__all__'


class ActListSerializer(serializers.ModelSerializer):
    employee = serializers.CharField(source='employee.last_name', read_only=True)
    victim = serializers.CharField(source='victim.last_name', read_only=True)

    class Meta:
        model = Act
        fields = ('id', 'number', 'employee', 'victim')


class ActRetrieveSerializer(WritableNestedModelSerializer):
    damages = DamageRetrieveSerializer(many=True)
    employee = EmployeeSerializer(required=False, allow_null=True)
    victim = VictimSerializer(read_only=True)

    class Meta:
        model = Act
        fields = ('id', 'number', 'employee', 'victim', 'damages',)


class ActCreateOrUpdateSerializer(WritableNestedModelSerializer):
    victim = VictimSerializer(required=False, allow_null=True)
    damages = DamageCreateSerializer(many=True)
    is_sms = serializers.BooleanField(required=False, allow_null=True)

    class Meta:
        model = Act
        fields = ('id', 'number', 'employee', 'municipality', 'address', 'building_type', 'victim', 'damages', 'is_sms')
        extra_kwargs = {'number': {'read_only': True}}


class ActSigningSerializer(WritableNestedModelSerializer):
    images = ActImageSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Act
        fields = ('images',)


class ActForPdfSerializer(WritableNestedModelSerializer):
    municipality = serializers.CharField(source='municipality.name', read_only=True)
    building_type = serializers.CharField(source='building_type.name', read_only=True)
    victim = VictimSerializer(read_only=True)

    damages = DamagePdfSerializer(many=True)
    employee = EmployeeSerializer(required=False, allow_null=True)

    class Meta:
        model = Act
        fields = ('id', 'number', 'created_at', 'municipality', 'building_type', 'victim', 'address', 'employee',
                  'signed_at', 'damages')
