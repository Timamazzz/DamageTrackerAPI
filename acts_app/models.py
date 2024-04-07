from datetime import datetime

from django.db import models

from DamageTrackerAPI.utils.smsc_api import SMSC
from users_app.models import User
import random
import string
from django.utils import timezone


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
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="acts_created",
                                 verbose_name="Сотрудник")
    victim = models.ForeignKey(User, on_delete=models.CASCADE, related_name="acts_victim",
                               verbose_name="Пострадавший объект", null=True, blank=True)
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, verbose_name="Муниципалитет")
    address = models.CharField(max_length=2048, verbose_name="Адрес")

    building_type = models.ForeignKey(BuildingType, on_delete=models.CASCADE, verbose_name="Тип постройки",
                                      related_name="acts")

    signed_at = models.DateTimeField(null=True, blank=True, verbose_name="Время подписания")

    class Meta:
        verbose_name = "Акт"
        verbose_name_plural = "Акты"
        app_label = "acts_app"

    def save(self, *args, **kwargs):
        print('self', self.__dict__)
        if not self.pk:
            current_date = datetime.now().strftime("%d%m%Y")
            random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
            self.number = f"{current_date}{random_chars}"

        if self.building_type.is_victim and not self.signed_at:
            print('hello')
            try:
                sign_code = SignCode.objects.get(act=self, user=self.victim)
                sign_code.code = SignCode.generate_activation_code()
                sign_code.save()
                print('sign_code1')
            except SignCode.DoesNotExist:
                sign_code = SignCode.objects.create(act=self, user=self.victim)
                print('sign_code2')

            if sign_code.code:
                smsc = SMSC()
                message = (
                    f'Ваш код:{sign_code.code} \n Проверить и скачать статус акта можно на сайте belid.ru, указав '
                    f'свой номер телефона')
                response = smsc.send_sms(f'7{self.victim.phone_number}', message, sender="BIK31.RU")
                print(response)

        else:
            self.signed_at = timezone.now()

        super().save(*args, **kwargs)


class DamageType(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название типа повреждения")

    class Meta:
        verbose_name = "Тип повреждения"
        verbose_name_plural = "Типы повреждений"
        app_label = "acts_app"

    def __str__(self):
        return self.name


class DamageName(models.Model):
    type = models.ForeignKey(DamageType, on_delete=models.CASCADE, verbose_name="Тип повреждения",
                             related_name="damage_names")
    name = models.CharField(max_length=255, verbose_name="Наименование повреждения")

    class Meta:
        verbose_name = "Наименование повреждения"
        verbose_name_plural = "Наименования повреждений"
        app_label = "acts_app"

    def __str__(self):
        return self.name


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


class SignCode(models.Model):
    act = models.ForeignKey(Act, on_delete=models.CASCADE, verbose_name="Акт")
    code = models.CharField(max_length=4, verbose_name="Код")
    upd_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Код подписи"
        verbose_name_plural = "Коды подписи"
        app_label = "acts_app"

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
