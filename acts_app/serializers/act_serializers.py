from rest_framework import serializers
from acts_app.models import Act
from drf_writable_nested.serializers import WritableNestedModelSerializer
from acts_app.serializers.damage_serializers import DamageCreateSerializer, DamageRetrieveSerializer
from users_app.serializers.user_serializers import VictimSerializer, EmployeeSerializer


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

    class Meta:
        model = Act
        fields = ('id', 'number', 'employee', 'damages')


class ActCreateOrUpdateSerializer(WritableNestedModelSerializer):
    victim = VictimSerializer(required=False, allow_null=True)
    damages = DamageCreateSerializer(many=True)

    class Meta:
        model = Act
        fields = ('id', 'number', 'employee', 'municipality', 'address', 'building_type', 'victim', 'damages')
        extra_kwargs = {'number': {'read_only': True}}


class ActSigningSerializer(serializers.Serializer):
    code = serializers.CharField()

    class Meta:
        fields = ('code',)


class ActForPdfSerializer(WritableNestedModelSerializer):
    municipality = serializers.CharField(source='municipality.name', read_only=True)
    building_type = serializers.CharField(source='building_type.name', read_only=True)
    victim = VictimSerializer(read_only=True)

    damages = DamageCreateSerializer(many=True)
    employee = EmployeeSerializer(required=False, allow_null=True)

    class Meta:
        model = Act
        fields = ('id', 'number', 'created_at', 'municipality', 'building_type', 'victim', 'address', 'damages',
                  'employee', 'signed_at')
