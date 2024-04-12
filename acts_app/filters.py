from django_filters import rest_framework as filters

from acts_app.models import Act


class ActFilter(filters.FilterSet):
    class Meta:
        model = Act
        fields = {
            'employee': ['exact'],
            'victim': ['exact'],
        }
