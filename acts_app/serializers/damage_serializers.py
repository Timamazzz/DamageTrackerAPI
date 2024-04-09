from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from acts_app.models import Damage, DamageType, DamageName
from docs_app.serializers.doc_serializers import DamageImageSerializer


class DamageSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Damage
        fields = '__all__'


class DamageCreateSerializer(WritableNestedModelSerializer):
    damage_images = DamageImageSerializer(required=False, many=True, allow_null=True)

    class Meta:
        model = Damage
        exclude = ('act',)
        extra_kwargs = {'note': {'required': False, 'allow_null': True}}


class DamageRetrieveSerializer(WritableNestedModelSerializer):
    damage_images = DamageImageSerializer(required=False, many=True, allow_null=True)
    damage_type = serializers.CharField(source='damage_type.name', read_only=True)
    name = serializers.CharField(source='name.name', read_only=True)

    class Meta:
        model = Damage
        exclude = ('act',)
        extra_kwargs = {'note': {'required': False, 'allow_null': True}}


class DamageTypeSerializer(WritableNestedModelSerializer):
    class Meta:
        model = DamageType
        fields = '__all__'


class DamageNameSerializer(WritableNestedModelSerializer):
    class Meta:
        model = DamageName
        fields = '__all__'
