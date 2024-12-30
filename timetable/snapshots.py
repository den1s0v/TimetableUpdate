from datetime import datetime
from pathlib import Path

from asgiref.sync import sync_to_async
from django.core.management import call_command

from myproject.settings import STATIC_ROOT


async def database_backup():
    """
    Создаёт бэкап базы данных.
    :return: Путь к файлу базы данных.
    """
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_dir = STATIC_ROOT / 'backups'  # Используем Path вместо строки
    backup_dir.mkdir(parents=True, exist_ok=True)  # Создаём директорию, если её нет

    backup_file = backup_dir / f'backup_{now}.json'  # Создаём путь к файлу

    with backup_file.open('w') as f:  # Открываем файл с использованием Path
        await sync_to_async(call_command)('dumpdata', stdout=f)

    return backup_file