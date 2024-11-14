from django.db import models


class Resource(models.Model):
    """
    Таблица resource хранит основные сведения о ресурсе, такие как имя, путь и метаданные.
    """
    last_update = models.DateTimeField()  # Дата последнего обновления ресурса
    name = models.CharField(max_length=255)  # Имя ресурса
    path = models.CharField(max_length=255, null=True, blank=True)  # Путь к файлу
    metadata = models.JSONField(null=True, blank=True)  # Дополнительные метаданные в формате JSON

    class Meta:
        db_table = 'resource'
        verbose_name = 'Ресурс'
        verbose_name_plural = 'Ресурсы'


class FileVersion(models.Model):
    """
    Таблица file_version хранит версии файлов, относящиеся к определенному ресурсу.
    """
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="versions")  # Связь с ресурсом
    mimetype = models.CharField(max_length=45, null=True, blank=True)  # MIME-тип файла
    url = models.TextField(null=True, blank=True)  # URL-адрес файла
    timestamp = models.DateTimeField(auto_now_add=True)  # Время добавления версии
    last_changed = models.DateTimeField(null=True, blank=True)  # Дата последнего изменения
    hashsum = models.CharField(max_length=255)  # Хэш-сумма файла

    class Meta:
        db_table = 'file_version'
        verbose_name = 'Версия файла'
        verbose_name_plural = 'Версии файлов'


class Storage(models.Model):
    """
    Таблица storage хранит информацию о местоположении файла и его ссылках на скачивание.
    """
    file_version_id = models.ForeignKey(FileVersion, on_delete=models.CASCADE, related_name="storages")  # Связь с версией файла
    storage_type = models.CharField(max_length=127)  # Тип хранилища, например, локально или облако
    name = models.CharField(max_length=255)  # Имя ресурса
    path = models.CharField(max_length=255, null=True, blank=True)  # Путь к файлу внутри хранилища
    download_url = models.TextField(null=True, blank=True)  # Ссылка для скачивания файла
    resource_url = models.TextField(null=True, blank=True)  # Прямая ссылка на ресурс в хранилище

    class Meta:
        db_table = 'storage'
        verbose_name = 'Хранилище'
        verbose_name_plural = 'Хранилища'
