from attr.validators import instance_of
from fs.googledrivefs import GoogleDriveFS
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os

from timetable.StorageManager import StorageManager
from timetable.models import Resource, FileVersion, Storage
class StorageManagerGoogleDrive (StorageManager):
    def __init__(self, storage_type:str, json_file_path:str):
        """
        Создаёт объект
        :param storage_type:
        :param json_file_path:
        """
        # Инициализация подключеничения
        SCOPES = ['https://www.googleapis.com/auth/drive']
        creds = service_account.Credentials.from_service_account_file(json_file_path, scopes=SCOPES)

        # Подключение в библиотеке GoogleDriveFS
        fs = GoogleDriveFS(creds)
        # Подключение напрямую для получения id файлов
        self._service = build('drive', 'v3', credentials=creds)

        # Инициализация родительского класса
        super().__init__(storage_type, fs)


    def _set_storage_link(self, file_dir:str, storage:Storage):
        # Определить ID файла
        file_id = self.__get_id(file_dir)

        # Сохранить ссылки для скачивания и просмотра в записи базы данных
        storage.download_url = self.__get_download_url(file_id)
        storage.resource_url = self.__get_view_url(file_id)

        # Вернуть запись базы данных со ссылками
        return storage

    def _make_file_public(self, file_system, file_dir:str):
        # Закончить выполнение, если файловая система не является
        if not instance_of(file_system, GoogleDriveFS):
            return

        # Получить ID файла
        file_id = self.__get_id(file_dir)

        # Определить набор прав доступа
        permission = {
            'type': 'anyone',  # доступ для всех
            'role': 'reader'  # доступ только для чтения
        }

        # Применяем новые права доступа к файлу
        self._service.permissions().create(fileId=file_id, body=permission).execute()

    def __get_id(self, path):
        """
        Опредляет id файла или директории.
        :param path: Путь.
        :return: ID.
        """
        # Вернуть id файла или директории
        return self._fs_root.getinfo(path).raw['sharing']['id']

    @staticmethod
    def __get_download_url(file_id):
        """
        Возвращает ссылку на скачивание файла.
        :param file_id: ID файла.
        :return: Ссылка на скачивание
        """
        return f"https://drive.google.com/uc?id={file_id}&export=download"

    @staticmethod
    def __get_view_url(file_id):
        """
        Возвращает ссылку на просмотр файла.
        :param file_id: ID файла.
        :return: Ссылка на просмотр файла.
        """
        return f"https://drive.google.com/file/d/{file_id}/view"
