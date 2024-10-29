from django.db import models

class Origin(models.Model):
    metadata = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    last_changed = models.DateTimeField(null=True, blank=True)
    hashsum = models.CharField(max_length=255)
    url = models.TextField(null=True, blank=True)
    filename = models.CharField(max_length=255, null=True, blank=True)
    mimetype = models.CharField(max_length=45, null=True, blank=True)
    resource_id = models.IntegerField()
    is_latest_version = models.BooleanField(default=True, help_text="является ли последней версией ресурса")

    class Meta:
        db_table = 'origin'
        verbose_name = 'Информация об источнике ресурса'
        verbose_name_plural = 'Информация об источниках ресурсов'


class Resource(models.Model):
    metadata = models.JSONField(null=True, blank=True)
    path = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'resource'
        verbose_name = 'Характеристики ресурса'
        verbose_name_plural = 'Характеристики ресурсов'


class Storage(models.Model):
    metadata = models.JSONField()
    source = models.ForeignKey(Origin, on_delete=models.CASCADE, related_name='storages')
    resource_id = models.IntegerField()
    last_changed = models.CharField(max_length=45, null=True, blank=True)
    storage_type = models.CharField(max_length=127, help_text="Тип хранилища - локальная файловая система, облако")
    path = models.CharField(max_length=255, null=True, blank=True, help_text="Путь к файлу внутри хранилища")
    download_url = models.TextField(null=True, blank=True)
    resource_url = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'storage'
        verbose_name = 'Место хранения ресурса'
        verbose_name_plural = 'Места хранения ресурсов'
