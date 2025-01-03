from django.http import HttpResponseNotAllowed, JsonResponse

# Create your views here.
from django.shortcuts import render
from openpyxl.compat import deprecated

from timetable.models import Tag, Resource, FileVersion, Storage, Setting
from ..apps import TAG_CATEGORY_LIST, LOCAL_STORAGE_NAME


def timetable_list(request):
    first_select_items = get_selector_items(Tag.objects.all(), TAG_CATEGORY_LIST[0])
    return render(request, 'timetable_list.html', {'first_select_items': first_select_items})

def timetable_params(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    tags = dict(request.GET)  # Получаем фильтры из GET-параметров

    resources = get_resource_by_tag(tags)

    # Получаем все теги, связанные с этими ресурсами
    related_tags = Tag.objects.filter(resources__in=resources).distinct()

    # Исключаем уже использованные фильтры
    for key, values in tags.items():
        related_tags = related_tags.exclude(category=key)

    # Получаем только уникальные названия категорий
    categories = set()
    for tag in related_tags:
        categories.add(tag.category)

    if len(categories) == 0:
        # Отправить список записей
        answer = get_files_list_answer(resources)
    else:
        # Отправить следующий селектор
        answer = get_new_selector_answer(categories, related_tags)

    return JsonResponse(answer)

def get_resource_by_tag(tags):
    # Получаем начальный QuerySet всех ресурсов
    resources = Resource.objects.filter(deprecated=False)

    # Фильтруем ресурсы для каждого переданного тега
    for key, values in tags.items():
        value = values[0]
        resources = resources.filter(tags__name=value, tags__category=key)

    return resources.distinct()

def get_new_selector_answer(categories, related_tags):
    # Определяем следующую категорию
    next_category = None
    for category in TAG_CATEGORY_LIST:
        if category in categories:
            next_category = category
            break

    # Для категории определяем список тегов
    selector_items = get_selector_items(related_tags, next_category)

    # Формируем ответ
    answer = {
        "result": "selector",
        "selector_name": next_category,
        "selector_description": "Выбрать что-то новое",
        "selector_items": selector_items
    }

    return answer

def get_selector_items(tags, next_category):
    selector_items = list()
    for tag in tags:
        if tag.category == next_category:
            selector_items.append(tag.name)
    return selector_items

def get_files_list_answer(resources):
    files = []
    try:
         download_storage_type = Setting.objects.get(key='download_storage').value
    except Setting.DoesNotExist:
        download_storage_type = LOCAL_STORAGE_NAME

    for resource in resources:
        last_version = FileVersion.objects.filter(resource=resource).order_by('-last_changed','-timestamp').first()
        storages = Storage.objects.filter(file_version=last_version)
        view_urls = dict()
        archive_urls = dict()
        download_url = ""
        for storage in storages:
            storage_type = storage.storage_type
            if storage_type == download_storage_type:
                download_url = storage.download_url

            resource_url = storage.resource_url
            if resource_url is not None:
                view_urls[storage_type] = resource_url

            archive_url = storage.archive_url
            if archive_url is not None:
                archive_urls[storage_type] = archive_url

        res_data = {
            "name": resource.name,
            "last_update" : resource.last_update,
            "download_url": download_url,
            "view_urls" : view_urls,
            "archive_urls" : archive_urls
        }

        files.append(res_data)

    # Формируем ответ
    answer = {
        "result": "files",
        "files": files
    }

    return answer