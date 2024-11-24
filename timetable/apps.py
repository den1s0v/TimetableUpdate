from django.apps import AppConfig

class TimetableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'timetable'

    def ready(self):
        # Добавить все необходимые библиотеки
        from timetable.StorageManagerGoogleDrive import StorageManagerGoogleDrive
        from timetable.StorageManager import StorageManager
        from timetable.filemanager import FileManager
        import fs.copy

        # Путь к json файл
        json_dir = "C:/Users/Ilya/Downloads/apt-sentinel-441610-i2-ad78fb036ada.json"
        # Путь к корневой папке локального хранилища
        local_fs = fs.open_fs('osfs://C:/Users/Ilya/Documents/Файлы сервера/файлы')

        # Создать хранилища
        sm_google = StorageManagerGoogleDrive("google drive", json_dir)
        sm_local = StorageManager("local", local_fs)

        # Создать класс управления файлами
        fm = FileManager()
        # Добавить в него проинициализированные хранилища
        fm.add_storage(sm_local)
        fm.add_storage(sm_google)
        # Обновить расписание
        fm.update_timetable()