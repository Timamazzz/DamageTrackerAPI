from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from acts_app.models import Damage
from docs_app.serializers.doc_serializers import DamageImageSerializer


class DamageSerializer(WritableNestedModelSerializer):

    class Meta:
        model = Damage
        fields = '__all__'


class DamageCreateSerializer(WritableNestedModelSerializer):
    damage_images = DamageImageSerializer()

    class Meta:
        model = Damage
        exclude = ('act',)
