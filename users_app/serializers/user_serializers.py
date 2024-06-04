from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from DamageTrackerAPI.utils.fields import PhoneField
from users_app.models import User, AdditionalContact


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserSendCodeSerializer(serializers.Serializer):
    phone_number = PhoneField()

    class Meta:
        model = User
        fields = ('phone_number',)


class UserVerifyCodeSerializer(serializers.Serializer):
    code = serializers.CharField(label="Код из СМС", required=True)

    class Meta:
        fields = ('code',)


class AdditionalContactSerializer(serializers.ModelSerializer):
    phone_number = PhoneField(required=True)

    class Meta:
        model = AdditionalContact
        exclude = ['user', ]


class VictimSerializer(WritableNestedModelSerializer):
    phone_number = PhoneField(required=True)
    additional_contacts = AdditionalContactSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'last_name', 'first_name', 'patronymic', 'phone_number', 'additional_contacts')


class EmployeeSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id', 'last_name', 'first_name', 'patronymic', 'phone_number')
