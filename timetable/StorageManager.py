from abc import ABC, abstractmethod

import fs
import fs.copy
from fs.memoryfs import FS

from timetable.models import Resource, FileVersion, Storage
class StorageManager(ABC):
    def __init__(self, storage_type:str, fs_root:FS):
        self.fs_root = fs_root
        self.storage_type = storage_type

    def add_new_file_version(self, local_file_path:str, resource:Resource, file_version:FileVersion):
        fs_local = fs.open_fs('osfs://')
        # Проверить наличие предыдущих версий
        previous_file_version = FileVersion.objects.filter(resource_id = file_version.resource).order_by('-last_changed').second()
        if previous_file_version is not None:
            # Перевести актуальную версию в архивную
            self.__move_actual_file_version_to_archive(previous_file_version)
            # Перезаписать файл с последней версией
            self.__rewrite_file(fs_local, local_file_path, self.fs_root, self.__create_actual_file_path(resource, file_version))
        else:
            # Создать новый файл актуальной версии
            self.__copy_file(fs_local, local_file_path, self.fs_root, self.__create_actual_file_path(resource, file_version))

    def __move_actual_file_version_to_archive(self, resource: Resource, file_version: FileVersion):
        """
        Ищет последнюю версию ресурса. Создаёт архивный файл с информацией из последней версии. Обновляет запись в базе данных.
        :param resource: Запись базы данных с информацией о ресурсе.
        :param file_version: Запись базы данных с информацией о версии файла.
        :return:
        """
        # Найти предыдущую версию, которая является актуальной
        storage = Storage.objects.filter(storage_type=self.storage_type, file_version_id=file_version.id).first()
        if storage is None:
            raise Exception("Storage does not exist")

        # Создать для версии архивный путь
        archive_path = self.__create_archive_file_path(resource, file_version)
        current_path = storage.path

        # Сохранить файл под новым названием
        self.__copy_file(self.fs_root, current_path, self.fs_root, archive_path)

        # Обновить параметры записи базы данных
        storage.name = self.__get_archive_file_name(resource, file_version)
        storage = self._update_storage_link(archive_path, storage)
        storage.save()


    def __rewrite_file(self, fs_source:FS, source_file_path: str, fs_destination:FS, destination_file_path: str, chunk_size: int = 4096):
        """
        Перезаписывает файл из одной файловой системы, файлом из другой файловой системы.
        :param fs_source: Файловая система источника.
        :param source_file_path: Путь к исходному файлу.
        :param fs_destination: Файловая система назначения.
        :param destination_file_path: Путь к целевому файлу.
        :param chunk_size: Размер буфера для чтения данных.
        """
        # Создаём пути к папкам
        fs_source.makedirs(fs.path.dirname(source_file_path))
        fs_destination.makedirs(fs.path.dirname(destination_file_path))
        # Открываем файлы и делаем перезапись
        with fs_source.open(source_file_path, 'rb') as source_file:
            with fs_destination.open(destination_file_path, 'wb') as target_file:
                while chunk:
                    # Чтение части данных из исходного файла
                    chunk = source_file.read(chunk_size)
                    # Проверка на окончание файла
                    if not chunk:
                        break
                    # Запись части данных в целевой файл
                    target_file.write(chunk)
        # Задаём файлам открытые права доступа
        self._make_file_public(fs_source, source_file_path)
        self._make_file_public(fs_destination, destination_file_path)


    def __copy_file(self, fs_source:FS, source_file_path: str, fs_destination:FS, destination_file_path: str):
        """
        Копирует файл из одной файловой системы в другую.
        :param fs_source: Файловая система источника.
        :param source_file_path: Путь к исходному файлу.
        :param fs_destination: Файловая система назначения.
        :param destination_file_path: Путь к целевому файлу.
        """
        # Создаём путь к файлу
        fs_destination.makedirs(fs.path.dirname(destination_file_path))
        # Копируем файл
        fs.copy.copy_file(fs_source, source_file_path, fs_destination, destination_file_path)
        # Задаём новому файлу открытые права доступа
        self._make_file_public(fs_destination, destination_file_path)

    def __create_actual_file_path(self, resource:Resource, file_version:FileVersion):
        new_dir = self.__get_path(resource)
        self.fs_root.makedirs(new_dir, recreate=True)
        return new_dir + '/' + self.__get_actual_file_path(resource, file_version)

    def __create_archive_file_path(self, resource:Resource, file_version:FileVersion):
        new_dir = self.__get_path(resource)
        self.fs_root.makedirs(new_dir, recreate=True)
        return new_dir + '/' + self.__get_archive_file_name(resource, file_version)

    @classmethod
    def __get_actual_file_path(cls, resource:Resource, file_version:FileVersion):
        return resource.name + file_version.mimetype

    @classmethod
    def __get_archive_file_name(cls, resource:Resource, file_version:FileVersion):
        return resource.name + file_version.last_changed.strftime('%Y%m%d%H%M%S') + file_version.mimetype

    @classmethod
    def __get_path (cls, resource:Resource):
        return f"{resource.path}/{resource.name}/"

    @abstractmethod
    def _update_storage_link(self, file_dir:str, storage:Storage):
        storage.resource_url = None
        storage.download_url = None
        return storage

    @abstractmethod
    def _make_file_public(self, fs, file_dir:str):
        pass