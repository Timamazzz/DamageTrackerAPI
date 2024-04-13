from django.core.management.base import BaseCommand
from acts_app.models import Municipality, BuildingType, DamageType
from users_app.managment.commands.lists import municipalities, building_types, damage_types


class Command(BaseCommand):
    help = 'Initialize database'

    def handle(self, *args, **options):
        for name in municipalities:
            Municipality.objects.get_or_create(name=name)

        for data in building_types:
            BuildingType.objects.get_or_create(name=data["name"], is_victim=data["is_victim"])

        for name in damage_types:
            DamageType.objects.get_or_create(name=name)

        self.stdout.write(self.style.SUCCESS('Successfully init the database'))
