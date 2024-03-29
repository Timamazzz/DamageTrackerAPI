from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        app_label = "users_app"

    def __str__(self):
        return f"{self.last_name} {self.first_name}"



