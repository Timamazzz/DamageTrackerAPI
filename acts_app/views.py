from datetime import datetime

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from DamageTrackerAPI.utils.ModelViewSet import ModelViewSet
from DamageTrackerAPI.utils.phones import SMSRU
from acts_app.filters import ActFilter
from acts_app.models import Act, BuildingType, Municipality, ActSign, DamageType
from acts_app.serializers.act_serializers import ActSerializer, ActListSerializer, ActCreateOrUpdateSerializer, \
    ActSigningSerializer, ActRetrieveSerializer, ActForPdfSerializer
from acts_app.serializers.building_type_serializers import BuildingTypeSerializer
from acts_app.serializers.damage_serializers import DamageTypeSerializer
from acts_app.serializers.municipality_serializers import MunicipalitySerializer
from dadata import Dadata
from dotenv import load_dotenv
import os
from django.http import HttpResponse
from xml.etree.ElementTree import Element, SubElement, tostring

load_dotenv()


# Create your views here.
class ActViewSet(ModelViewSet):
    queryset = Act.objects.all().order_by('-id')
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
                serializer = self.get_serializer(act, data=request.data, partial=False)
                serializer.is_valid(raise_exception=True)
                images = serializer.validated_data.get('act_images', None)
                if not images:
                    return Response({'error': 'Отсутствуют изображения'}, status=status.HTTP_400_BAD_REQUEST)
                serializer.save()
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        act.signed_at = timezone.now()
        act.save()

        sign.delete()

        return Response({'number': f"{act.number}"}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        copy_data = request.data
        copy_data['employee'] = request.user.id
        copy_data['number'] = Act.generate_number()
        is_victim = copy_data.get('victim', None)
        if is_victim is None:
            copy_data['signed_at'] = datetime.now()

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
                sms_client = SMSRU()
                message = (
                    f'Ваш код:{sign.code} \n Проверить и скачать статус акта можно на сайте belid.ru, указав '
                    f'свой номер телефона')
                sms_client.send_sms(f'7{act.victim.phone_number}', message, json=False)

                act.save()

                return Response({'message': f"ok"}, status=status.HTTP_200_OK)

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

    @action(detail=False, methods=['GET'], url_path='xml')
    def generate_xml_for_date(self, request):
        date_str = request.GET.get('date')
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Некорректный формат даты'}, status=status.HTTP_400_BAD_REQUEST)

        acts = Act.objects.filter(created_at__date=date)
        if not acts.exists():
            return Response({'error': 'Акты не найдены'}, status=status.HTTP_404_NOT_FOUND)

        root = Element('acts')

        for act in acts:
            act_element = SubElement(root, 'act')

            number_element = SubElement(act_element, 'number')
            number_element.text = act.number

            created_at_element = SubElement(act_element, 'created_at')
            created_at_element.text = act.created_at.strftime('%Y-%m-%d %H:%M:%S')

            employee_element = SubElement(act_element, 'employee')
            if act.employee:
                employee_last_name_element = SubElement(employee_element, 'last_name')
                employee_last_name_element.text = act.employee.last_name
                employee_first_name_element = SubElement(employee_element, 'first_name')
                employee_first_name_element.text = act.employee.first_name
                employee_patronymic_element = SubElement(employee_element, 'patronymic')
                employee_patronymic_element.text = act.employee.patronymic
                employee_phone_element = SubElement(employee_element, 'phone_number')
                employee_phone_element.text = act.employee.phone_number
            else:
                employee_element.text = "null"

            victim_element = SubElement(act_element, 'victim')
            if act.victim:
                victim_last_name_element = SubElement(victim_element, 'last_name')
                victim_last_name_element.text = act.victim.last_name
                victim_first_name_element = SubElement(victim_element, 'first_name')
                victim_first_name_element.text = act.victim.first_name
                victim_patronymic_element = SubElement(victim_element, 'patronymic')
                victim_patronymic_element.text = act.victim.patronymic
                victim_phone_element = SubElement(victim_element, 'phone_number')
                victim_phone_element.text = act.victim.phone_number
            else:
                victim_element.text = "null"

            municipality_element = SubElement(act_element, 'municipality')
            municipality_element.text = act.municipality.name

            address_element = SubElement(act_element, 'address')
            if act.address:
                address_name_element = SubElement(address_element, 'name')
                address_name_element.text = act.address.name

                address_fias_id_element = SubElement(address_element, 'fias_id')
                address_fias_id_element.text = act.address.fias_id

            building_type_element = SubElement(act_element, 'building_type')
            building_type_element.text = act.building_type.name

            signed_at_element = SubElement(act_element, 'signed_at')
            if act.signed_at:
                signed_at_element.text = act.signed_at.strftime('%Y-%m-%d %H:%M:%S')
            else:
                signed_at_element.text = "null"

            act_images_element = SubElement(act_element, 'act_images')
            for act_image in act.act_images.all():
                act_image_element = SubElement(act_images_element, 'act_image')
                act_image_url_element = SubElement(act_image_element, 'url')
                act_image_url_element.text = request.build_absolute_uri(act_image.file.url.replace('/media/', '/'))

            damages_element = SubElement(act_element, 'damages')
            for damage in act.damages.all():
                damage_element = SubElement(damages_element, 'damage')
                damage_type_element = SubElement(damage_element, 'damage_type')
                damage_type_element.text = damage.damage_type.name
                count_element = SubElement(damage_element, 'count')
                count_element.text = str(damage.count)
                note_element = SubElement(damage_element, 'note')
                note_element.text = damage.note

                damage_images_element = SubElement(damage_element, 'damage_images')
                for damage_image in damage.damage_images.all():
                    damage_image_element = SubElement(damage_images_element, 'damage_image')
                    damage_image_url_element = SubElement(damage_image_element, 'url')
                    damage_image_url_element.text = request.build_absolute_uri(
                        damage_image.file.url.replace('/media/', '/'))

        xml_string = tostring(root, encoding='utf-8').decode('utf-8')

        response = HttpResponse(xml_string, content_type='application/xml')
        response['Content-Disposition'] = 'attachment; filename="acts.xml"'
        return response


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
