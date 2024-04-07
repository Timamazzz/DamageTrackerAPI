from DamageTrackerAPI.utils.ModelViewSet import ModelViewSet
from DamageTrackerAPI.utils.smsc_api import SMSC
from acts_app.filters import ActFilter
from acts_app.models import Act, BuildingType, Municipality, SignCode
from acts_app.serializers.act_serializers import ActSerializer, ActListSerializer, ActCreateSerializer
from acts_app.serializers.building_type_serializers import BuildingTypeSerializer
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
        'create': ActCreateSerializer,
    }

    def perform_create(self, serializer):
        act = serializer.save()

        building_type_id = serializer.validated_data.get('building_type')
        building_type = BuildingType.objects.get(pk=building_type_id)

        if building_type.is_victim:
            victim_id = serializer.validated_data.get('victim')
            victim = User.objects.get(pk=victim_id)

            try:
                sign_code = SignCode.objects.get(act=act, user=victim)
                sign_code.code = SignCode.generate_activation_code()
                sign_code.save()
            except SignCode.DoesNotExist:
                sign_code = SignCode.objects.create(act=act, user=victim)

            if sign_code.code:
                smsc = SMSC()
                message = (
                    f'Ваш код:{sign_code.code} \n Проверить и скачать статус акта можно на сайте belid.ru, указав '
                    f'свой номер телефона')
                smsc.send_sms(f'7{victim.phone_number}', message, sender="BIK31.RU")

    def perform_update(self, serializer):
        act = serializer.save()

        building_type_id = serializer.validated_data.get('building_type')
        building_type = BuildingType.objects.get(pk=building_type_id)

        if building_type.is_victim:
            victim_id = serializer.validated_data.get('victim')
            victim = User.objects.get(pk=victim_id)

            try:
                sign_code = SignCode.objects.get(act=act, user=victim)
                sign_code.code = SignCode.generate_activation_code()
                sign_code.save()
            except SignCode.DoesNotExist:
                sign_code = SignCode.objects.create(act=act, user=victim)

            if sign_code.code:
                smsc = SMSC()
                message = (
                    f'Ваш код:{sign_code.code} \n Проверить и скачать статус акта можно на сайте belid.ru, указав '
                    f'свой номер телефона')
                smsc.send_sms(f'7{victim.phone_number}', message, sender="BIK31.RU")


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
