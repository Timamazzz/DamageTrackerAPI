from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import random
import string
from django.utils import timezone
from django.contrib.auth.hashers import make_password

from acts_app.models import Municipality


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The phone number must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)


class Position(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название")

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"
        app_label = "users_app"

    def __str__(self):
        return self.title


class User(AbstractUser):
    patronymic = models.CharField(max_length=100, verbose_name="Отчество", blank=True, null=True)
    phone_number = models.CharField(max_length=11, verbose_name="Номер телефона", unique=True, )
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, verbose_name="Должность", null=True, blank=True)
    workplace = models.CharField(max_length=100, verbose_name="Место работы", null=True, blank=True)
    password = models.CharField("Пароль", null=True, blank=True, max_length=128)
    username = models.CharField(
        "имя пользователя",
        max_length=150,
        unique=False,
    )

    objects = CustomUserManager()

    municipality = models.ForeignKey(Municipality, null=True, blank=True, on_delete=models.CASCADE,
                                     verbose_name="Муниципалитет")
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        app_label = "users_app"

    def __str__(self):
        return f"{self.phone_number}"


class ActivationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    code = models.CharField(max_length=4, verbose_name="Код активации")
    upd_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Код активации"
        verbose_name_plural = "Коды активации"
        app_label = "users_app"

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
