from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from acts_app.models import Damage, DamageType


class DamageSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Damage
        fields = '__all__'


class DamageTypeSerializer(WritableNestedModelSerializer):
    class Meta:
        model = DamageType
        fields = ('id', 'name')


class DamageCreateSerializer(WritableNestedModelSerializer):
    damage_type = DamageTypeSerializer()

    class Meta:
        model = Damage
        exclude = ('act',)


class DamagePdfSerializer(WritableNestedModelSerializer):
    damage_type = serializers.CharField(source='damage_type.name', read_only=True)

    class Meta:
        model = Damage
        fields = ('damage_type',)


class DamageRetrieveSerializer(WritableNestedModelSerializer):
    damage_type = serializers.CharField(source='damage_type.name', read_only=True)

    # name = serializers.CharField(source='name.name', read_only=True)

    class Meta:
        model = Damage
        exclude = ('act',)


class DamageTypeSerializer(WritableNestedModelSerializer):
    class Meta:
        model = DamageType
        fields = '__all__'
