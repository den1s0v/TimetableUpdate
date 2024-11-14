from fs.googledrivefs import GoogleDriveFS
from googleapiclient.discovery import build
from google.oauth2 import service_account

from timetable.StorageManager import StorageManager
from timetable.models import Resource, FileVersion, Storage
class StorageManagerGoogleDrive (StorageManager):
    def __init__(self, storage_type:str, json_file_path:str):
        SCOPES = ['https://www.googleapis.com/auth/drive']
        creds = service_account.Credentials.from_service_account_file(json_file_path, scopes=SCOPES)

        fs = GoogleDriveFS(creds)
        self.service = build('drive', 'v3', credentials=creds)
        super().__init__(storage_type, fs)


    def _update_storage_link(self, file_dir:str, storage:Storage):
        file_id = self.__get_file_id(file_dir)
        storage.download_url = self.__get_download_url(file_id)
        storage.resource_url = self.__get_view_url(file_dir)
        return storage

    def _make_file_public(self, fs, file_dir:str):
        if fs != self.fs_root:
            return
        file_id = self.__get_file_id(file_dir)
        permission = {
            'type': 'anyone',  # доступ для всех
            'role': 'reader'  # доступ только для чтения
        }
        self.service.permissions().create(fileId=file_id, body=permission).execute()

    def __get_file_id(self, file_dir):
        return self.fs_root.getinfo(file_dir).raw['id']

    @staticmethod
    def __get_download_url(file_id):
        return f"https://drive.google.com/uc?id={file_id}&export=download"

    @staticmethod
    def __get_view_url(file_id):
        return f"https://drive.google.com/file/d/{file_id}/view"
