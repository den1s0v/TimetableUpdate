import asyncio
import json
import threading


from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from myproject.settings import GOOGLE_AUTH_FILE
from timetable.apps import AVAILABLE_KEYS
from timetable.cron_utils import create_update_timetable_cron_task
from timetable.models import Task, Snapshot, Setting
from timetable.task.make_task import make_task
from timetable.task.snapshot import task_make_snapshot

storage_types = ['Google Drive', 'Yandex Drive', 'Локальное хранилище']
snapshot_types = ['Вся система', 'База данных', 'Google Drive', 'Yandex Drive', 'Локальное хранилище']
clear_types = ['Вся система', 'Все хранилища', 'Google Drive', 'Yandex Drive', 'Локальное хранилище']

def admin_login(request):
    """
    Обработчик авторизации.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_panel')
        else:
            return render(request, 'admin_login.html', {'error': 'Неверные учетные данные или нет доступа'})
    return render(request, 'admin_login.html')

@login_required
def admin_panel(request):
    """
    Обработчик панели администратора.
    """
    if not request.user.is_staff:
        return redirect('admin_login')

    params = {
        'storage_types': storage_types,
        'snapshot_types': snapshot_types,
        'clear_types': clear_types
    }
    return render (request, 'admin_panel.html', params)

def put_google_auth_file(request):
    """
    Обновить файл авторизации гугл.
    """
    if request.method == 'PUT':
        try:
            # Получаем содержимое тела запроса
            file_content = request.body.decode('utf-8')  # Читаем тело запроса как текст

            # Преобразуем содержимое в JSON (если требуется)
            file_data = json.loads(file_content)

            # Сохраняем файл на сервере (опционально)
            with GOOGLE_AUTH_FILE.open(mode='w', encoding='utf-8') as f:
                json.dump(file_data, f, indent=4)

            return JsonResponse({'status': 'success', 'message': 'Файл загружен'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Неверный формат JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Метод не поддерживается'}, status=405)
    text = request.POST.get('text')
    return HttpResponse(status=200)

def set_system_params(request):
    """
    Обработчик задания настроек для системы.
    """
    data = json.loads(request.body)

    for key, value in data.items():
        # Проверка на наличие ключа в списке допустимых настроек
        if key not in AVAILABLE_KEYS:
            continue

        # Сохранение ключа в память
        setting, created = Setting.objects.get_or_create(key=key)
        setting.value = value
        setting.save()

        # Выполнение дополнительных действия для конкретных ключей
        match (key):
            case 'time_update':
                create_update_timetable_cron_task()

    return HttpResponse(status=200)

def snapshot(request):
    """
    Обработчик запросов по снимкам.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        if (action == 'make_new'):
            snapshot = request.POST.get('snapshot')
            params = {
                'action' : action,
                'snapshot' : snapshot,
            }
            snapshot_task = Task.objects.create(status="running", params=params)
            threading.Thread(target=asyncio.run, args=(make_task(snapshot_task),)).start()
            return JsonResponse({'status':snapshot_task.status, 'id': snapshot_task.id}, status=202)

    elif request.method == 'GET':
        keys = request.GET.keys()
        if 'process_id' in keys:
            process_id = request.GET.get('process_id')
            task = Task.objects.get(id=int(process_id))
            if (task is not None):
                return JsonResponse({'status': task.status, 'result': task.result, 'error_message': task.error_message},
                                    status=200)
        elif 'snapshot_type' in keys:
            snapshot_type = request.GET.get('snapshot_type')
            snapshot = Snapshot.objects.filter(type=snapshot_type).order_by('-timestamp').first()
            if snapshot is not None:
                return JsonResponse({'url' : snapshot.get_url()}, status=200)
            else:
                return JsonResponse({'url' : ""}, status=200)

    return HttpResponse(status=400)

def manage_storage(request):
    """Обработчик управления хранилищами."""
    if request.method == 'POST':
        action = request.POST.get('action')
        if (action == 'dell'):
            component = request.POST.get('component')
            params = {
                'action': action,
                'component': component,
            }
            snapshot_task = Task.objects.create(status="running", params=params)
            threading.Thread(target=asyncio.run, args=(make_task(snapshot_task),)).start()
            return JsonResponse({'status': snapshot_task.status, 'id': snapshot_task.id}, status=202)

    elif request.method == 'GET':
        keys = request.GET.keys()
        if 'process_id' in keys:
            process_id = request.GET.get('process_id')
            task = Task.objects.get(id=int(process_id))
            if (task is not None):
                return JsonResponse({'status': task.status, 'result': task.result, 'error_message': task.error_message},
                                    status=200)


    return HttpResponse(status=400)

