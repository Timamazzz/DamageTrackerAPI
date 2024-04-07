from django_filters import rest_framework as filters

from users_app.models import User


class UserFilter(filters.FilterSet):
    class Meta:
        model = User
        fields = {
            'phone_number': ['exact'],
        }
