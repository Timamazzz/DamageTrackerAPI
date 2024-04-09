from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from DamageTrackerAPI.utils.ModelViewSet import ModelViewSet
from DamageTrackerAPI.utils.smsc_api import SMSC
from acts_app.filters import ActFilter, DamageNameFilter
from acts_app.models import Act, BuildingType, Municipality, SignCode, DamageType, DamageName
from acts_app.serializers.act_serializers import ActSerializer, ActListSerializer, ActCreateOrUpdateSerializer, \
    ActSigningSerializer, ActRetrieveSerializer, ActForPdfSerializer
from acts_app.serializers.building_type_serializers import BuildingTypeSerializer
from acts_app.serializers.damage_serializers import DamageTypeSerializer, DamageNameSerializer
from acts_app.serializers.municipality_serializers import MunicipalitySerializer
from users_app.models import User


# Create your views here.
class ActViewSet(ModelViewSet):
    queryset = Act.objects.all()
    serializer_class = ActSerializer
    filterset_class = ActFilter
    search_fields = ['number',
                     'employee__first_name', 'employee__last_name', 'employee__patronymic',
                     'victim_first_name', 'victim_last_name', 'victim_patronymic']
    serializer_list = {
        'list': ActListSerializer,
        'create': ActCreateOrUpdateSerializer,
        'retrieve': ActRetrieveSerializer,
        'update': ActCreateOrUpdateSerializer,
        'signing': ActSigningSerializer,
        'pdf': ActForPdfSerializer
    }

    @action(detail=True, methods=['post'])
    def signing(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        act = self.get_object()

        if not serializer.is_valid():
            return Response({'error': 'Неверные данные'}, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data.get('code')
        try:
            sign_code = SignCode.objects.get(act=act, code=code)
        except SignCode.DoesNotExist:
            return Response({'error': 'Неверный код активации'}, status=status.HTTP_400_BAD_REQUEST)

        if sign_code.is_expired:
            return Response({'error': 'Срок действия кода активации истек'}, status=status.HTTP_400_BAD_REQUEST)

        act.signed_at = timezone.now()
        act.save()

        sign_code.delete()

        return Response({'number': f"{act.number}"}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        copy_data = request.data
        copy_data['employee'] = request.user
        serializer = self.get_serializer(data=copy_data)
        #serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        copy_data = request.data
        copy_data['employee'] = request.user
        serializer = self.get_serializer(instance, data=copy_data, partial=partial)
        #serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(methods=['GET'], detail=True)
    def pdf(self, request):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


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


class DamageTypeViewSet(ModelViewSet):
    queryset = DamageType.objects.all()
    serializer_class = DamageTypeSerializer

    serializer_list = {
        'list': DamageTypeSerializer,
    }


class DamageNameViewSet(ModelViewSet):
    queryset = DamageName.objects.all()
    serializer_class = DamageNameSerializer
    filterset_class = DamageNameFilter

    serializer_list = {
        'list': DamageNameSerializer,
    }
