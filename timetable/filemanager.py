from pathlib import Path
import time
import random
import subprocess
import os

from myproject.settings import TEMP_DIR, LIBREOFFICE_EXE
from timetable.StorageManager import StorageManager
from timetable.models import Resource, FileVersion, Storage, Tag, Setting
from timetable.parser import WebParser

class FileManager:
    TIMETABLE_START_PATH = "Расписания/Расписание занятий/"
    MIN_SEC_DELAY_UPDATE = 5
    MAX_SEC_DELAY_UPDATE = 10

    def __init__(self):
        # Задать новую директорию временных файлов
        os.environ["TMPDIR"] = str(TEMP_DIR)
        # Создать контейнер для хранилищ
        self.__storages = []
        # Взять путь к файлам из настроек
        self.TIMETABLE_LINK = ""
        try:
            self.TIMETABLE_LINK = Setting.objects.get(key='analyze_url').value
        except Setting.DoesNotExist:
            self.TIMETABLE_LINK = "https://www.vstu.ru/student/raspisaniya/zanyatiy/"
    def add_storage(self, storage: StorageManager):
        """
        Добавить новое хранилище.
        :param storage: Хранилище файлов.
        """
        self.__storages.append(storage)

    def update_timetable(self):
        """
        Обновляет информацию о расписании
        :return:
        """
        # Получить все файлы с сайта
        files = WebParser.get_files_from_webpage(FileManager.TIMETABLE_LINK, FileManager.TIMETABLE_START_PATH)

        # Для всех файлов
        for file_data in files:
            print("path:", file_data.get_path(), "name:", file_data.get_name())

            # Скачать файл
            file_path = file_data.download_file(TEMP_DIR)
            # Конвертировать xls файл в xlsx файл, если это возможно
            file_path = self.convert_xls_to_xlsx(file_path)

            # Рассчитать ресурс, которому соответствует файл
            resource = file_data.get_resource()
            # Рассчитать версию файла
            file_version = file_data.get_file_version(file_path)

            # Загрузить файл в хранилища, если подобного ресурса раньше не существовало
            resource_from_db = Resource.objects.filter(path=resource.path, name=resource.name).first()
            if resource_from_db is None:
                # Сохранить ресурс
                resource.save()
                # Сохранить информацию о версии
                file_version.resource = resource
                file_version.save()
                # Загрузить файл во все доступные хранилища
                self.save_file_to_storages(file_path, resource, file_version)
            else:
                # Обновить список тегов
                tags = [Tag.objects.get_or_create(name=tag.name, category=tag.category)[0] for tag in resource.get_not_saved_tags()]
                print(tags)
                resource_from_db.tags.set(tags)

                # Выбрать уже существующий ресурс
                resource = resource_from_db


                # Найти последнюю запись с информацией о версии файла
                file_version_from_db = FileVersion.objects.filter(resource=resource).order_by('-last_changed',  '-timestamp').first()

                # Создать новую версию файла, если запись не найдена или старая версия неактуальная
                if file_version_from_db is None or self.need_upload_new_file_version(file_version, file_version_from_db):
                    # Создать новую запись
                    file_version.resource = resource
                    file_version.save()

                    # Загрузить файл во все доступные хранилища
                    self.save_file_to_storages(file_path, resource, file_version)

            # Удалить временный файл
            file_path.unlink()

    @classmethod
    def convert_xls_to_xlsx(cls, xls_file_path:Path|str, dell_xls = True):
        """
        Преобразовывает файл с расширением .xls в файл с расширением .xlsx.
        Если файл с другим расширением, вернёт текущий путь без преобразования.
        :param xls_file_path: Путь к файлу с расширением .xls
        :param dell_xls: Параметр удаления файла с расширением .xls после его преобразования
        :return: Путь к файлу
        """
        # Привести путь к нужному типу
        xls_file_path = Path(xls_file_path)

        # Завершить выполнение, файл имеет расширение файла не .xls
        if xls_file_path.suffix != '.xls':
            return xls_file_path

        # Путь к файлу с новым расширением
        xlsx_file_path = xls_file_path.with_suffix('.xlsx')

        # Сохранение данных в формате .xlsx

        result = subprocess.run([
            LIBREOFFICE_EXE,
            "--headless",  # Без графического интерфейса
            "--convert-to", "xlsx",
            "--outdir", str(xlsx_file_path.parent),
            str(xls_file_path)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Вернуть путь к новому файлу, если конвертация прошла успешно
        if result == 0:
            # Удаление файла
            if dell_xls:
                xls_file_path.unlink()

            # Вернуть новый путь
            return xlsx_file_path
        # Вернуть путь к первоначальному файлу, если конвертация прошла некорректно
        else:
            return xlsx_file_path

    @staticmethod
    def need_upload_new_file_version(new_version:FileVersion, last_version:FileVersion):
        """
        Определяет необходимость обновлять версию файла.
        :param new_version: Новая версия.
        :param last_version: Предыдущая версия.
        :return: Результат анализа.
        """
        return new_version.last_changed != last_version.last_changed or new_version.hashsum != last_version.hashsum

    def save_file_to_storages(self, file_path:Path|str, resource:Resource, file_version:FileVersion):
        """
        Сохранить файл во всех доступных хранилищах
        :param file_path:
        :param resource:
        :param file_version:
        :return:
        """
        # Приводим путь к файлу к нужному типу
        file_path = Path(file_path)
        for storage in self.__storages:
            storage.add_new_file_version(file_path, resource, file_version)
            print("load this file on", storage.get_storage_type())
