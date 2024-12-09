from django.db import models


class Resource(models.Model):
    """
    Таблица resource хранит основные сведения о ресурсе, такие как имя, путь и метаданные.
    """
    id = models.BigAutoField(primary_key=True)
    last_update = models.DateTimeField(auto_now=True, verbose_name="Дата последнего обновления")  # Автоматическое обновление времени
    name = models.CharField(max_length=255, verbose_name="Имя ресурса")  # Имя ресурса
    path = models.TextField(null=True, blank=True, default=None, verbose_name="Путь к ресурсу")  # Путь
    metadata = models.JSONField(null=True, blank=True, default=None, verbose_name="Метаданные")  # JSON-данные
    tags = models.ManyToManyField(
        'Tag',
        related_name='resources',
        blank=True,
        verbose_name="Теги"
    )

    class Meta:
        db_table = 'resource'
        verbose_name = 'Ресурс'
        verbose_name_plural = 'Ресурсы'
        app_label = 'timetable'

    def __str__(self):
        return f"{self.name} ({self.path})"


class FileVersion(models.Model):
    """
    Таблица file_version хранит версии файлов, относящиеся к определенному ресурсу.
    """
    id = models.BigAutoField(primary_key=True)
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        db_column='resource_id',
        related_name="versions",
        verbose_name="Связанный ресурс"
    )
    mimetype = models.CharField(max_length=45, null=True, blank=True, default=None, verbose_name="MIME-тип файла")  # MIME-тип
    url = models.TextField(null=True, blank=True, default=None, verbose_name="URL-адрес файла")  # URL
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания версии")  # Дата создания
    last_changed = models.DateTimeField(null=True, blank=True, default=None, verbose_name="Дата последнего изменения")  # Последнее изменение
    hashsum = models.CharField(max_length=255, verbose_name="Хэш-сумма файла")  # Хэш

    class Meta:
        db_table = 'file_version'
        verbose_name = 'Версия файла'
        verbose_name_plural = 'Версии файлов'
        app_label = 'timetable'

    def __str__(self):
        return f"{self.url} ({self.last_changed} | {self.timestamp}) hash {self.hashsum}"

class Storage(models.Model):
    """
    Таблица storage хранит информацию о местоположении файла и его ссылках на скачивание.
    """
    id = models.BigAutoField(primary_key=True)
    file_version = models.ForeignKey(
        FileVersion,
        on_delete=models.CASCADE,
        db_column='file_version_id',
        related_name="storages",
        verbose_name="Связанная версия файла"
    )
    storage_type = models.CharField(max_length=127, verbose_name="Тип хранилища")  # Тип хранилища
    path = models.TextField(null=True, blank=True, default=None, verbose_name="Путь к файлу")  # Путь
    download_url = models.TextField(null=True, blank=True, default=None, verbose_name="Ссылка для скачивания")  # Скачивание
    resource_url = models.TextField(null=True, blank=True, default=None, verbose_name="Ссылка на ресурс")  # Прямая ссылка

    class Meta:
        db_table = 'storage'
        verbose_name = 'Хранилище'
        verbose_name_plural = 'Хранилища'
        app_label = 'timetable'

    def __str__(self):
        return f"{self.path} ({self.storage_type})"

class Tag(models.Model):
    """
    Таблица tag хранит информацию о тегах, которые могут быть связаны с ресурсами.
    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name="Название тега")
    category = models.CharField(max_length=200, verbose_name="Название категории тега")

    class Meta:
        db_table = 'tag'
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        app_label = 'timetable'
        constraints = [
            models.UniqueConstraint(fields=['name', 'category'], name='unique_name_category')
        ]

    def __str__(self):
        return f"{self.name} ({self.category})"

