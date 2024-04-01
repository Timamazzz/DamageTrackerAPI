from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from DamageTrackerAPI.utils.OptionsMetadata import OptionsMetadata


class ModelViewSet(viewsets.ModelViewSet):
    """
    Базовый класс для представлений наборов моделей.
    """
    serializer_list = {}  # Словарь для хранения сериализаторов для каждого действия
    metadata_class = OptionsMetadata  # Класс метаданных для представлений
    filter_backends = [DjangoFilterBackend, SearchFilter]

    def get_serializer(self, *args, **kwargs):
        """
        Получение сериализатора.
        """
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        """
        Получение класса сериализатора.
        """
        # Возвращаем класс сериализатора для текущего действия или класс по умолчанию
        return self.serializer_list.get(self.action, self.serializer_class)
