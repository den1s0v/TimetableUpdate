import asyncio

from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from myproject.settings import STATIC_ROOT
from timetable.models import Task, Snapshot
from timetable.snapshots import database_backup

storage_types = ['Google Drive', 'Yandex Drive', 'Локальное хранилище']
snapshot_types = ['База данных', 'Все хранилища', 'Google Drive', 'Yandex Drive', 'Вся система']
clear_types = ['Вся система', 'Все хранилища', 'Google Drive', 'Yandex Drive']

def admin_login(request):
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
    if not request.user.is_staff:
        return redirect('admin_login')

    params = {
        'storage_types': storage_types,
        'snapshot_types': snapshot_types,
        'clear_types': clear_types
    }
    return render (request, 'admin_panel.html', params)

def put_google_auth_file(request):
    return HttpResponse(status=200)

def set_system_params(request):
    return HttpResponse(status=200)

def snapshot(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if (action == 'make_new'):
            snapshot = request.POST.get('snapshot')
            params = {
                'action' : action,
                'snapshot' : snapshot,
            }
            snapshot_task = Task.objects.create(status="running", params=params)
            async_to_sync(make_snapshot)(snapshot_task)
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
    return HttpResponse(status=200)

async def make_snapshot(task :Task):
    print(task)
    match(task.params.get('snapshot', None)):
        case 'База данных':
            file_path = await database_backup()
            print(file_path)
            result = {
                'url' : str(file_path.relative_to(STATIC_ROOT)),
            }
            task.result = result
            task.status = 'success'
            await sync_to_async(task.save)()