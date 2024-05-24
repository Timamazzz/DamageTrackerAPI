from uuid import uuid4
import requests
import os
from datetime import datetime

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


def compress_image(uploaded_file, max_size=(1024, 1024)):
    image = Image.open(uploaded_file)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    buffer = BytesIO()
    image.save(buffer, format='JPEG', quality=85)
    buffer.seek(0)

    compressed_file = InMemoryUploadedFile(buffer, None, uploaded_file.name, 'image/jpeg', buffer.tell(), None)
    return compressed_file


class FileUploadSerializer(serializers.Serializer):
    """
    Сериализатор для загрузки файлов.
    """
    files = serializers.ListField(child=serializers.FileField(max_length=100000, allow_empty_file=False, use_url=False))


def save_uploaded_files(uploaded_files, path):
    """
    Функция для сохранения загруженных файлов.

    :param uploaded_files: Список загруженных файлов
    :param path: Путь для сохранения файлов
    :return: Список данных о сохраненных файлах
    """
    result_data = []

    for uploaded_file in uploaded_files:
        original_name = None
        extension = None
        url = None

        if isinstance(uploaded_file, str):
            # Если передан URL файла, загружаем его содержимое
            response = requests.get(uploaded_file)
            if response.status_code == 200:
                content_type = response.headers.get('content-type')
                extension = content_type.split('/')[-1] if content_type else ''
                new_name = f"{uuid4().hex}_{datetime.now().strftime('%Y%m%d%H%M%S')}{extension}"

                save_path = default_storage.save(os.path.join(path, new_name), ContentFile(response.content))
                url = default_storage.url(save_path)
        else:
            # Если передан объект файла, сохраняем его
            original_name = uploaded_file.name
            extension = os.path.splitext(original_name)[-1].lower()
            new_name = f"{uuid4().hex}_{datetime.now().strftime('%Y%m%d%H%M%S')}{extension}"

            # Определение MIME-типа файла
            mime_type = uploaded_file.content_type
            if uploaded_file.size > 1024 * 1024 and mime_type.startswith(
                    'image/'):  # Если файл больше 1 МБ и является изображением, сжимаем его
                try:
                    uploaded_file = compress_image(uploaded_file)
                except Exception as e:
                    raise ValueError(f"Ошибка при сжатии изображения: {str(e)}")

            save_path = default_storage.save(os.path.join(path, new_name), uploaded_file)
            url = default_storage.url(save_path)

            # Удаляем префикс 'media' из URL
            if url.startswith('/media/'):
                url = url[len('/media/'):]

        file_data = {
            'file': url,
            'original_name': original_name,
            'extension': extension,
        }

        result_data.append(file_data)

    return result_data


class FileUploadView(APIView):
    """
    Представление для загрузки файлов.
    """
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        uploaded_files = request.FILES.getlist('files')
        path = request.GET.get('path', 'uploads/')

        try:
            result_data = save_uploaded_files(uploaded_files, path)
            return Response(result_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
