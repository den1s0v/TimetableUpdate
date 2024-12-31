from django.core.management.base import BaseCommand
import logging

from myproject.settings import DATA_STORAGE_DIR, GOOGLE_AUTH_FILE

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Запуск обновления данных'

    def handle(self, *args, **kwargs):
        logger.info("Запущена задача cron")

        # Добавить все необходимые библиотеки
        from .version_core.storage_manager_google_drive import StorageManagerGoogleDrive
        from .version_core.storage_manager import StorageManager
        from .version_core.filemanager import FileManager

        import fs.copy

        # Путь к корневой папке локального хранилища
        local_dir = DATA_STORAGE_DIR
        local_dir.mkdir(exist_ok=True)
        local_fs = fs.open_fs(str(local_dir))

        # Создать хранилища
        sm_google = StorageManagerGoogleDrive("google drive", GOOGLE_AUTH_FILE)
        sm_local = StorageManager("local", local_fs)

        # Создать класс управления файлами
        file_manager = FileManager()

        # Добавить в него проинициализированные хранилища
        file_manager.add_storage(sm_local)
        file_manager.add_storage(sm_google)

        # Выполнить обновление файлов
        file_manager.update_timetable()

        print("Задача cron выполнена!")
