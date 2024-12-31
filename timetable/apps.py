from pathlib import Path

from django.apps import AppConfig

TAG_CATEGORY_LIST = [
    'education_form',
    'degree', # Потом нужно убрать
    'faculty',
    'course',
]
DOWNLOAD_STORAGE_TYPE = "google drive"
AVAILABLE_KEYS = {'time_update', 'analyze_url', 'google_json_dir', 'google_json_dir'}

class TimetableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'timetable'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)

    def ready(self):
        # Создать задачу в кроне на обновление системы
        from timetable.cron_utils import create_update_timetable_cron_task
        create_update_timetable_cron_task()
