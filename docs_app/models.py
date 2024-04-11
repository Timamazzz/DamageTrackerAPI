from django.db import models

from acts_app.models import Damage, Act


# Create your models here.
class DamageImage(models.Model):
    damage = models.ForeignKey(Damage, on_delete=models.CASCADE, verbose_name='Повреждение', related_name="damage_images")
    file = models.FileField(verbose_name='Файл')
    original_name = models.CharField(max_length=255, verbose_name='Оригинальное имя')
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='Время загрузки')
    extension = models.CharField(max_length=10, verbose_name='Расширение')

    def __str__(self):
        return f'{self.original_name} ({self.damage})'

    class Meta:
        verbose_name = 'Фотография повреждения'
        verbose_name_plural = 'Фотографии повреждения'
        app_label = 'docs_app'


class ActImage(models.Model):
    act = models.ForeignKey(Act, on_delete=models.CASCADE, verbose_name='Акт', related_name="act_images")
    file = models.FileField(verbose_name='Файл')
    original_name = models.CharField(max_length=255, verbose_name='Оригинальное имя')
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='Время загрузки')
    extension = models.CharField(max_length=10, verbose_name='Расширение')

    def __str__(self):
        return f'{self.original_name} ({self.act})'

    class Meta:
        verbose_name = 'Фотография акта'
        verbose_name_plural = 'Фотографии акта'
