from django.db import models
import random
import string
from django.utils import timezone

from users_app.models import User


class Position(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название")

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"
        app_label = "employees_app"

    def __str__(self):
        return self.title


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, verbose_name="Пользователь")
    phone_number = models.CharField(max_length=11, verbose_name="Номер телефона")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    patronymic = models.CharField(max_length=100, verbose_name="Отчество", blank=True, null=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name="Должность")

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        app_label = "employees_app"

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.patronymic or ''}"


class ActivationCode(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, verbose_name="Сотрудник")
    code = models.CharField(max_length=4, verbose_name="Код активации")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    @staticmethod
    def generate_activation_code():
        return ''.join(random.choice(string.digits) for _ in range(4))

    @property
    def is_expired(self):
        expiration_time = self.created_at + timezone.timedelta(hours=3)
        return timezone.now() > expiration_time

    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = self.generate_activation_code()
        super().save(*args, **kwargs)
