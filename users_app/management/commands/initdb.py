from django.core.management.base import BaseCommand
from acts_app.models import Municipality, BuildingType, DamageType


class Command(BaseCommand):
    help = 'Initialize database'

    municipalities = [
        "Белгородская область",
        "Белгородский район",
        "Город Белгород",
        "Алексеевский городской округ",
        "Борисовский район",
        "Валуйский городской округ",
        "Вейделевский район",
        "Волоконовский район",
        "Губкинский городской округ",
        "Грайворонский городской округ",
        "Ивнянский район",
        "Корочанский район",
        "Красненский район",
        "Красногвардейский район",
        "Краснояружский район",
        "Новооскольский городской округ",
        "Прохоровский район",
        "Ракитянский район",
        "Ровеньский район",
        "Старооскольский городской округ",
        "Шебекинский городской округ",
        "Чернянский район",
        "Яковлевский городской округ"
    ]

    building_types = [
        {"name": "Хозяйственные постройки", "is_victim": True},
        {"name": "Жилые постройки с хозпостройками (ИЖС)", "is_victim": True},
        {"name": "Жилые постройки с хозпостройками (МКД)", "is_victim": True},
        {"name": "Жилые постройки (ИЖС)", "is_victim": True},
        {"name": "Жилые постройки (МКД)", "is_victim": True},
        {"name": "Место общего пользования", "is_victim": False},
    ]

    damage_types = [
        "Внутренние работы (пол)",
        "Внутренние работы (стены)",
        "Оконные блоки",
    ]

    def handle(self, *args, **options):
        for name in self.municipalities:
            Municipality.objects.get_or_create(name=name)

        for data in self.building_types:
            BuildingType.objects.get_or_create(name=data["name"], is_victim=data["is_victim"])

        for name in self.damage_types:
            DamageType.objects.get_or_create(name=name)

        self.stdout.write(self.style.SUCCESS('Successfully init the database'))
