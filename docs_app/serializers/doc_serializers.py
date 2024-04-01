from rest_framework import serializers

from docs_app.models import DamageImage


class DamageImageSerializer(serializers.ModelSerializer):
    file = serializers.CharField()

    class Meta:
        model = DamageImage
        fields = '__all__'
