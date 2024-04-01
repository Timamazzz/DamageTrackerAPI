from django.shortcuts import render

from DamageTrackerAPI.utils.ModelViewSet import ModelViewSet
from acts_app.models import Act, BuildingType
from acts_app.serializers.act_serializers import ActSerializer, ActListSerializer, ActCreateSerializer
from acts_app.serializers.building_type_serializers import BuildingTypeSerializer


# Create your views here.
class ActViewSet(ModelViewSet):
    queryset = Act.objects.all()
    serializer_class = ActSerializer

    serializer_list = {
        'list': ActListSerializer,
        'create': ActCreateSerializer
    }


class MunicipalityViewSet(ModelViewSet):
    queryset = Act.objects.all()
    serializer_class = ActSerializer

    serializer_list = {
        'list': ActListSerializer
    }


class BuildingTypeViewSet(ModelViewSet):
    queryset = BuildingType.objects.all()
    serializer_class = BuildingTypeSerializer

    serializer_list = {
        'list': BuildingTypeSerializer,
    }
