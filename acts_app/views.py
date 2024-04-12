from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from DamageTrackerAPI.utils.ModelViewSet import ModelViewSet
from DamageTrackerAPI.utils.smsc_api import SMSC
from acts_app.filters import ActFilter, DamageNameFilter
from acts_app.models import Act, BuildingType, Municipality, ActSign, DamageType, DamageName
from acts_app.serializers.act_serializers import ActSerializer, ActListSerializer, ActCreateOrUpdateSerializer, \
    ActSigningSerializer, ActRetrieveSerializer, ActForPdfSerializer
from acts_app.serializers.building_type_serializers import BuildingTypeSerializer
from acts_app.serializers.damage_serializers import DamageTypeSerializer, DamageNameSerializer
from acts_app.serializers.municipality_serializers import MunicipalitySerializer
from users_app.models import User
from dadata import Dadata
from dotenv import load_dotenv
import os

load_dotenv()


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
        'signing': ActSigningSerializer,
        'pdf': ActForPdfSerializer
    }

    @action(detail=True, methods=['post'])
    def signing(self, request, pk=None):
        code = request.query_params.get('code')
        act = self.get_object()

        try:
            if code:
                sign = ActSign.objects.get(act=act, code=code)
            else:
                sign = ActSign.objects.get(act=act, is_photo=True)
        except ActSign.DoesNotExist:
            if code:
                return Response({'error': 'Неверный код активации'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Договор не ожидает активации по фото'}, status=status.HTTP_400_BAD_REQUEST)

        if sign.is_expired:
            return Response({'error': 'Срок действия подписи истек'}, status=status.HTTP_400_BAD_REQUEST)

        if not code:
            try:
                print('request.data', request.data)
                serializer = self.get_serializer(act, data=request.data, partial=False)
                serializer.is_valid(raise_exception=True)
                images = serializer.validated_data.get('act_images', None)
                print('images', images)
                if not images:
                    return Response({'error': 'Отсутствуют изображения'}, status=status.HTTP_400_BAD_REQUEST)
                serializer.save()
            except Exception as e:
                print('error:', e)
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        act.signed_at = timezone.now()
        act.save()

        sign.delete()

        return Response({'number': f"{act.number}"}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        copy_data = request.data
        copy_data['employee'] = request.user.id
        copy_data['number'] = Act.generate_number()

        serializer = self.get_serializer(data=copy_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['POST'], detail=True, url_path='send-sign')
    def send_sign(self, request, pk=None):
        is_code = request.data.get('is_code', False)
        is_photo = request.data.get('is_photo', False)

        act = self.get_object()

        try:
            sign = ActSign.objects.get(act=act)
        except ActSign.DoesNotExist:
            sign = ActSign.objects.create(act=act)

        if is_code and act.victim and act.building_type.is_victim:
            sign.code = ActSign.generate_activation_code()
            sign.save()

            if sign.code:
                smsc = SMSC()
                message = (
                    f'Ваш код:{sign.code} \n Проверить и скачать статус акта можно на сайте belid.ru, указав '
                    f'свой номер телефона')
                smsc.send_sms(f'7{act.victim.phone_number}', message, sender="BIK31.RU")
                act.save()

                return Response({'message': f"{sign.code}"}, status=status.HTTP_200_OK)

        if is_photo:
            sign.is_photo = True
            sign.save()
            return Response({'message': f"ok"}, status=status.HTTP_200_OK)

        if not act.building_type.is_victim:
            act.signed_at = timezone.now()
            act.save()
            return Response({'message': f"ok"}, status=status.HTTP_200_OK)

        return Response({'message': {"Dont work"}}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True)
    def pdf(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False, url_path='get-address')
    def get_address(self, request):
        query = request.GET.get('query', '')

        if not query:
            return Response([])

        fias_id = os.environ.get('FIAS_ID')
        token = os.environ.get('DADATA_TOKEN')
        secret = os.environ.get('DADATA_SECRET')

        locations = [{"fias_id": fias_id}]
        dadata = Dadata(token, secret)

        try:
            result = dadata.suggest(name="address", query=query, locations=locations)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)


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
