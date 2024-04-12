from rest_framework import serializers

from docs_app.models import DamageImage, ActImage


class DamageImageSerializer(serializers.ModelSerializer):
    file = serializers.CharField()

    class Meta:
        model = DamageImage
        exclude = ('damage',)


class ActImageSerializer(serializers.ModelSerializer):
    file = serializers.CharField()

    class Meta:
        model = ActImage
        exclude = ('act',)
