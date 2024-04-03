from django.db import models
from users_app.models import User


class Municipality(models.Model):
    name = models.CharField(max_length=1024, verbose_name="Название муниципалитета")

    class Meta:
        verbose_name = "Муниципалитет"
        verbose_name_plural = "Муниципалитеты"
        app_label = "acts_app"


class BuildingType(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название типа постройки")
    is_victim = models.BooleanField(default=True, verbose_name="Собственность пострадавшего")

    class Meta:
        verbose_name = "Тип постройки"
        verbose_name_plural = "Типы построек"
        app_label = "acts_app"


class Act(models.Model):
    number = models.CharField(max_length=255, verbose_name="Номер акта")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    name = models.CharField(max_length=255, verbose_name="Название акта")
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="acts_created",
                                 verbose_name="Сотрудник")
    victim = models.ForeignKey(User, on_delete=models.CASCADE, related_name="acts_victim",
                               verbose_name="Пострадавший объект")
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, verbose_name="Муниципалитет")
    address = models.CharField(max_length=2048, verbose_name="Адрес")

    building_type = models.ForeignKey(BuildingType, on_delete=models.CASCADE, verbose_name="Тип постройки",
                                      related_name="acts")

    class Meta:
        verbose_name = "Акт"
        verbose_name_plural = "Акты"
        app_label = "acts_app"


class DamageType(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название типа повреждения")

    class Meta:
        verbose_name = "Тип повреждения"
        verbose_name_plural = "Типы повреждений"
        app_label = "acts_app"


class DamageName(models.Model):
    type = models.ForeignKey(DamageType, on_delete=models.CASCADE, verbose_name="Тип повреждения",
                             related_name="damage_names")
    name = models.CharField(max_length=255, verbose_name="Наименование повреждения")

    class Meta:
        verbose_name = "Наименование повреждения"
        verbose_name_plural = "Наименования повреждений"
        app_label = "acts_app"


class Damage(models.Model):
    act = models.ForeignKey(Act, on_delete=models.CASCADE, verbose_name="Акт", related_name="damages")
    damage_type = models.ForeignKey(DamageType, on_delete=models.CASCADE, verbose_name="Тип повреждения",
                                    related_name="damages")
    name = models.ForeignKey(DamageName, on_delete=models.CASCADE, verbose_name="damages")
    count = models.PositiveIntegerField(verbose_name="Количество повреждений")
    note = models.TextField(verbose_name="Примечание")

    class Meta:
        verbose_name = "Повреждение"
        verbose_name_plural = "Повреждения"
        app_label = "acts_app"
