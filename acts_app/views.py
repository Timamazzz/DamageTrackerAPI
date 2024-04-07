from django.shortcuts import render

from DamageTrackerAPI.utils.ModelViewSet import ModelViewSet
from acts_app.models import Act, BuildingType, Municipality
from acts_app.serializers.act_serializers import ActSerializer, ActListSerializer, ActCreateSerializer
from acts_app.serializers.building_type_serializers import BuildingTypeSerializer
from acts_app.serializers.municipality_serializers import MunicipalitySerializer


# Create your views here.
class ActViewSet(ModelViewSet):
    queryset = Act.objects.all()
    serializer_class = ActSerializer
    search_fields = ['number',
                     'employee__first_name', 'employee__last_name', 'employee__patronymic',
                     'victim_first_name', 'victim_last_name', 'victim_patronymic', '']
    serializer_list = {
        'list': ActListSerializer,
        'create': ActCreateSerializer
    }


class MunicipalityViewSet(ModelViewSet):
    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializer

    serializer_list = {
        'list': MunicipalitySerializer
    }


class BuildingTypeViewSet(ModelViewSet):
    queryset = BuildingType.objects.all()
    serializer_class = BuildingTypeSerializer

    serializer_list = {
        'list': BuildingTypeSerializer,
    }
