from pathlib import Path

from django.apps import AppConfig

from myproject.settings import BASE_DIR, DATA_STORAGE_DIR

TAG_CATEGORY_LIST = [
    'education_form',
    'degree', # Потом нужно убрать
    'faculty',
    'course',
]
DOWNLOAD_STORAGE_TYPE = "google drive"
AVAILABLE_KEYS = {'time_update', 'analyze_url', 'download_storage'}

class TimetableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'timetable'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        self.file_manager = None

    def ready(self):
        # Добавить все необходимые библиотеки
        from timetable.StorageManagerGoogleDrive import StorageManagerGoogleDrive
        from timetable.StorageManager import StorageManager
        from timetable.filemanager import FileManager
        import fs.copy

        # Путь к json файл
        json_dir = str(BASE_DIR / "auth" / "google_drive_auth.json")

        # Путь к корневой папке локального хранилища
        local_dir = DATA_STORAGE_DIR
        local_dir.mkdir(exist_ok=True)
        local_fs = fs.open_fs(str(local_dir))

        # Создать хранилища
        self.sm_google = StorageManagerGoogleDrive("google drive", json_dir)
        self.sm_local = StorageManager("local", local_fs)

        # Создать класс управления файлами
        self.file_manager = FileManager()
        # Добавить в него проинициализированные хранилища
        self.file_manager.add_storage(self.sm_local)
        self.file_manager.add_storage(self.sm_google)