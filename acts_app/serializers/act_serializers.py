from rest_framework import serializers
from acts_app.models import Act, Address
from drf_writable_nested.serializers import WritableNestedModelSerializer
from acts_app.serializers.damage_serializers import DamageCreateSerializer, DamageRetrieveSerializer, \
    DamagePdfSerializer
from docs_app.serializers.doc_serializers import ActImageSerializer
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
    victim = VictimSerializer(read_only=True)

    class Meta:
        model = Act
        fields = ('id', 'number', 'employee', 'victim', 'damages',)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class ActCreateOrUpdateSerializer(WritableNestedModelSerializer):
    victim = VictimSerializer(required=False, allow_null=True)
    damages = DamageCreateSerializer(many=True)
    is_sms = serializers.BooleanField(required=False, allow_null=True)
    address = AddressSerializer()

    class Meta:
        model = Act
        fields = ('id', 'number', 'employee', 'municipality', 'address', 'building_type', 'victim', 'damages', 'is_sms')


class ActSigningSerializer(WritableNestedModelSerializer):
    act_images = ActImageSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Act
        fields = ('id', 'act_images',)


class ActForPdfSerializer(WritableNestedModelSerializer):
    municipality = serializers.CharField(source='municipality.name', read_only=True)
    building_type = serializers.CharField(source='building_type.name', read_only=True)
    victim = VictimSerializer(read_only=True)

    damages = DamagePdfSerializer(many=True)
    employee = EmployeeSerializer(required=False, allow_null=True)

    act_images = ActImageSerializer(many=True)

    address = serializers.CharField(source='address.name', read_only=True)

    class Meta:
        model = Act
        fields = ('id', 'number', 'created_at', 'municipality', 'building_type', 'victim', 'address', 'employee',
                  'signed_at', 'damages', 'act_images')
