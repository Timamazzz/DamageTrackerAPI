from datetime import datetime
from django.db import models
import random
import string
from django.utils import timezone


class Municipality(models.Model):
    name = models.CharField(max_length=1024, verbose_name="Название муниципалитета")

    class Meta:
        verbose_name = "Муниципалитет"
        verbose_name_plural = "Муниципалитеты"
        app_label = "acts_app"

    def __str__(self):
        return self.name


class BuildingType(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название типа постройки")
    is_victim = models.BooleanField(default=True, verbose_name="Собственность пострадавшего")

    class Meta:
        verbose_name = "Тип постройки"
        verbose_name_plural = "Типы построек"
        app_label = "acts_app"

    def __str__(self):
        return self.name


class Address(models.Model):
    name = models.CharField(max_length=255, verbose_name="Адрес")
    fias_id = models.CharField(max_length=255, verbose_name="Фиас id")

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"
        app_label = "acts_app"

    def __str__(self):
        return self.name


class Act(models.Model):
    number = models.CharField(max_length=255, verbose_name="Номер акта")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    employee = models.ForeignKey('users_app.User', on_delete=models.CASCADE, related_name="acts_created",
                                 verbose_name="Сотрудник")
    victim = models.ForeignKey('users_app.User', on_delete=models.CASCADE, related_name="acts_victim",
                               verbose_name="Пострадавший объект", null=True, blank=True)
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, verbose_name="Муниципалитет")
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name="acts", verbose_name="Адрес")

    building_type = models.ForeignKey(BuildingType, on_delete=models.CASCADE, verbose_name="Тип постройки",
                                      related_name="acts")

    signed_at = models.DateTimeField(null=True, blank=True, verbose_name="Время подписания")

    file = models.FileField(null=True, blank=True, verbose_name="Файл")

    class Meta:
        verbose_name = "Акт"
        verbose_name_plural = "Акты"
        app_label = "acts_app"

    def __str__(self):
        return f'Акт №{self.number} от {self.created_at.strftime("%d.%m.%Y")}'

    @staticmethod
    def generate_number():
        current_date = datetime.now().strftime("%d%m%Y")
        russian_chars = 'АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ'
        digits = string.digits
        random_chars = ''.join(random.choices(russian_chars + digits, k=4))
        return f"{current_date}{random_chars}"


class DamageType(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название типа повреждения")

    class Meta:
        verbose_name = "Тип повреждения"
        verbose_name_plural = "Типы повреждений"
        app_label = "acts_app"

    def __str__(self):
        return self.name


class Damage(models.Model):
    act = models.ForeignKey(Act, on_delete=models.CASCADE, verbose_name="Акт", related_name="damages")
    damage_type = models.ForeignKey(DamageType, on_delete=models.CASCADE, verbose_name="Тип повреждения",
                                    related_name="damages")
    count = models.PositiveIntegerField(verbose_name="Количество повреждений")
    note = models.TextField(verbose_name="Примечание")

    class Meta:
        verbose_name = "Повреждение"
        verbose_name_plural = "Повреждения"
        app_label = "acts_app"

    def __str__(self):
        return f'Повреждение в акте №{self.act.number}: {self.damage_type.name}'


class ActSign(models.Model):
    act = models.ForeignKey(Act, on_delete=models.CASCADE, verbose_name="Акт")
    code = models.CharField(max_length=4, verbose_name="Код")
    is_photo = models.BooleanField(default=False, verbose_name="Подпись по фото")
    upd_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Подпись акта"
        verbose_name_plural = "Подписи акта"
        app_label = "acts_app"

    def __str__(self):
        return f'Подпись акта №{self.act.number} ({self.code})'

    @staticmethod
    def generate_activation_code():
        return ''.join(random.choice(string.digits) for _ in range(4))

    @property
    def is_expired(self):
        expiration_time = self.upd_at + timezone.timedelta(hours=3)
        return timezone.now() > expiration_time

    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = self.generate_activation_code()
        super().save(*args, **kwargs)
