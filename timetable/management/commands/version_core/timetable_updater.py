import os
import subprocess
import logging
from pathlib import Path

from myproject.settings import TEMP_DIR, LIBREOFFICE_EXE
from timetable.models import Resource, FileVersion, Tag, Setting
from .file_data import FileData
from .parser import WebParser
from .storage_manager import StorageManager

logger = logging.getLogger(__name__)


class TimetableUpdater:
    def __init__(self, web_parser: WebParser, storages: list[StorageManager], temp_dir: Path = TEMP_DIR):
        self.__web_parser = web_parser
        self.__storages = storages
        self.temp_dir = temp_dir
        os.environ["TMPDIR"] = str(temp_dir)

    def add_storage(self, storage: StorageManager):
        """
        Добавить новое хранилище.
        :param storage: Хранилище файлов.
        """
        self.__storages.append(storage)
        logger.info(f"Storage added: {storage}")

    def update_timetable(self, timetable_url: str):
        """
        Обновляет информацию о расписании.
        """
        logger.info(f"Starting timetable update from {timetable_url}")
        # Получить все файлы с помощью парсера
        files = self.__web_parser.get_files_from_webpage(timetable_url)
        logger.info(f"Found {len(files)} files to process.")
        # Создать множество обработанных ресурсов
        processed_resource_ids = set()

        # Для всех файлов
        for file_data in files:
            file_path = None
            # Попытаться обработать файл
            try:
                # Загрузить и конвертировать файл если это необходимо
                file_path = self._download_and_convert(file_data)
                logger.debug(f"Downloaded and converted file: {file_data.get_path()}")
                # Получает записи базы данных
                resource = file_data.get_resource()
                file_version = file_data.get_file_version(file_path)

                # Получает запись из базы данных
                resource_from_db = Resource.objects.filter(
                    path=resource.path, name=resource.name
                ).first()

                # Сохранить ресурс, если он является новым
                if resource_from_db is None:
                    self._save_new_resource(resource, file_version, file_path)
                    logger.info(f"Saved new resource: {resource}")
                # Иначе обновить существующий ресурс
                else:
                    self._update_existing_resource(resource_from_db, resource, file_version, file_path)
                    logger.info(f"Updated existing resource: {resource_from_db}")

                # Добавить ресурс в множество обработанных
                processed_resource_ids.add(resource.id)
            # Отловить ошибку
            except Exception as e:
                logger.error(f"Error processing file {file_data.get_path()}: {e}", exc_info=True)
            # Удалить временный файл, если он был создан
            finally:
                if file_path is not None and file_path.exists():
                    file_path.unlink() # Удалить файл
                    logger.debug(f"Temporary file deleted: {file_path}")

        if files:
            self._deprecate_processed_resources(processed_resource_ids)
            logger.debug("Deprecated unused resources.")

    def _download_and_convert(self, file_data:FileData):
        """
        Скачать файл и конвертировать его, если есть такая необходимость.
        :param file_data: Информация о файле.
        """
        file_path = file_data.download_file(self.temp_dir)
        logger.debug(f"File downloaded: {file_path}")
        return self._convert_xls_to_xlsx(file_path)

    def _save_new_resource(self, resource, file_version, file_path):
        """
        Сохранить новый ресурс
        """
        resource.save()
        file_version.resource = resource
        file_version.save()
        self._save_to_storages(file_path, resource, file_version)

    def _update_existing_resource(self, resource_from_db, resource, file_version, file_path):
        resource_from_db.tags.set(self._get_or_create_tags(resource.get_not_saved_tags()))
        resource_from_db.deprecated = False
        resource_from_db.save()
        logger.info(f"Tags updated for resource: {resource_from_db}")

        last_file_version = FileVersion.objects.filter(resource=resource_from_db).order_by(
            '-last_changed', '-timestamp'
        ).first()

        if last_file_version is None or self._is_new_version(file_version, last_file_version):
            file_version.resource = resource_from_db
            file_version.save()
            self._save_to_storages(file_path, resource_from_db, file_version)
            logger.info(f"New file version saved: {file_version}")

    def _save_to_storages(self, file_path, resource, file_version):
        for storage in self.__storages:
            storage.add_new_file_version(file_path, resource, file_version)
            logger.info(f"File saved to storage: {storage.get_storage_type()}")

    def _convert_xls_to_xlsx(self, xls_file_path: Path, delete_xls=True):
        if xls_file_path.suffix != '.xls':
            return xls_file_path

        xlsx_file_path = xls_file_path.with_suffix('.xlsx')
        result = subprocess.run([
            LIBREOFFICE_EXE, "--headless", "--convert-to", "xlsx", "--outdir", str(xlsx_file_path.parent), str(xls_file_path)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            logger.info(f"File converted to xlsx: {xlsx_file_path}")
            if delete_xls:
                xls_file_path.unlink()
                logger.info(f"Original xls file deleted: {xls_file_path}")
        else:
            logger.warning(f"Failed to convert file: {xls_file_path}")

        return xlsx_file_path if result.returncode == 0 else xls_file_path

    @staticmethod
    def _is_new_version(new_version, last_version):
        return new_version.hashsum != last_version.hashsum

    @staticmethod
    def _get_or_create_tags(tags):
        return [Tag.objects.get_or_create(name=tag.name, category=tag.category)[0] for tag in tags]

    def _deprecate_processed_resources(self, used_resource_ids):
        resources = Resource.objects.exclude(id__in=used_resource_ids).filter(deprecated=False)
        for resource in resources:
            resource.deprecated = True
            resource.save()
            logger.info(f"Resource deprecated: {resource}")