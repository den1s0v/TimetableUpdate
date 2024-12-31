import subprocess

from myproject.settings import BASE_DIR, VIRTUALENV_PATH
from timetable.models import Setting


def add_cron_task(task_name, interval_minutes):
    """
    Добавляет или обновляет задачу cron.
    """
    # Команда для выполнения
    command = f"{str(VIRTUALENV_PATH)}/bin/python {str(BASE_DIR / 'manage.py')} {task_name}"

    # Удаление старой задачи с этим именем
    remove_cron_task(task_name)

    # Добавление новой задачи
    cron_command = f"(crontab -l; echo '*/{interval_minutes} * * * * {command}') | crontab -"
    subprocess.run(cron_command, shell=True, check=True)


def remove_cron_task(task_name):
    """
    Удаляет задачу cron с указанным именем.
    """
    command = f"crontab -l | grep -v '{task_name}' | crontab -"
    subprocess.run(command, shell=True, check=True)


def list_cron_tasks():
    """
    Возвращает текущий список задач cron.
    """
    result = subprocess.run("crontab -l", shell=True, capture_output=True, text=True)
    return result.stdout

def create_update_timetable_cron_task():
    # Время обновления задачи
    try:
        minutes = Setting.objects.get(key='time_update').value
    except:
        minutes = '30'


    # Создать задачу в кроне на обновление системы
    add_cron_task('update_timetable', minutes)