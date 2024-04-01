from rest_framework import serializers
from DamageTrackerAPI.utils.fields import PhoneField
from users_app.models import User


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


class VictimGetOrCreateSerializer(serializers.Serializer):
    phone_number = PhoneField(help_text="На этот номер пострадавшему/представителю придет СМС для подписания акта")

    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'patronymic', 'phone_number',)
