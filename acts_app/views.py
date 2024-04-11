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
                     'victim__first_name', 'victim__last_name', 'victim__patronymic']
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
        code = request.query_params.get('code')
        act = self.get_object()

        if code:
            try:
                sign_code = SignCode.objects.get(act=act, code=code)
            except SignCode.DoesNotExist:
                return Response({'error': 'Неверный код активации'}, status=status.HTTP_400_BAD_REQUEST)

            if sign_code.is_expired:
                return Response({'error': 'Срок действия кода активации истек'}, status=status.HTTP_400_BAD_REQUEST)

            act.signed_at = timezone.now()
            act.save()

            sign_code.delete()
        else:
            serializer = self.get_serializer(act, data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
            images = serializer.validated_data.get('images', None)
            if images:
                serializer.save()
                act.signed_at = timezone.now()
                act.save()
            else:
                return Response({'error': 'Отсутствуют изображения'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'number': f"{act.number}"}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        copy_data = request.data
        copy_data['employee'] = request.user.id
        copy_data['number'] = Act.generate_number()

        is_sms_send = copy_data.pop('is_sms', False)

        serializer = self.get_serializer(data=copy_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        act = self.get_object()

        if is_sms_send and act.victim:
            try:
                sign_code = SignCode.objects.get(act=self)
                sign_code.code = SignCode.generate_activation_code()
                sign_code.save()
            except SignCode.DoesNotExist:
                sign_code = SignCode.objects.create(act=self)

            if sign_code.code:
                smsc = SMSC()
                message = (
                    f'Ваш код:{sign_code.code} \n Проверить и скачать статус акта можно на сайте belid.ru, указав '
                    f'свой номер телефона')
                smsc.send_sms(f'7{act.victim.phone_number}', message, sender="BIK31.RU")
                act.save()
        elif act.victim is None:
            act.signed_at = timezone.now()
            act.save()
        else:
            return Response({'message': "Ошибка!"}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['GET'], detail=True)
    def pdf(self, request, pk=None):
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
