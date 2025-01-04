from django.http import HttpResponseNotAllowed, JsonResponse, HttpResponse

# Create your views here.
from django.shortcuts import render

from timetable.models import Tag, Resource, FileVersion, Storage, Setting
from ..apps import TAG_CATEGORY_MAP, LOCAL_STORAGE_NAME


def timetable_list(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    params = dict(request.GET.dict())
    match params.get('degree', None):
        case 'master':
            tag = Tag.objects.filter(category='degree', name__icontains='магистратура').first()
            context = {
                'page_class': 'master-page',
                'schedule_title': 'Расписания занятий для магистратуры',
                'degree_title': 'Магистратура',
                'degree_card_class': 'degree-card-master',
                'degree_separator_class': 'degree-card-separator-line-master',
                'degree_image': 'image/master_image.png',
            }
        case 'postgraduate':
            tag = Tag.objects.filter(category='degree', name__icontains='аспирантура').first()
            context = {
                'page_class': 'postgraduate-page',
                'schedule_title': 'Расписания занятий для аспирантуры',
                'degree_title': 'Аспирантура',
                'degree_card_class': 'degree-card-postgraduate',
                'degree_separator_class': 'degree-card-separator-line-postgraduate',
                'degree_image': 'image/postgraduate_image.png',
            }
        case _:
            tag = Tag.objects.filter(category='degree', name__icontains='бакалавриат').first()
            context = {
                'page_class': 'bachelor-page',
                'schedule_title': 'Расписания занятий для бакалавриата (специалитета)',
                'degree_title': 'Бакалавриат (специалитет)',
                'degree_card_class': 'degree-card-bachelor',
                'degree_separator_class': 'degree-card-separator-line-bachelor',
                'degree_image': 'image/bachelor_image.png',
            }

    if tag is None:
        return HttpResponse(status=500)
    context['required_key'] = tag.category
    context['required_value'] = tag.name
    return render(request, 'timetable_list.html', context)

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
    for category in TAG_CATEGORY_MAP.keys():
        if category in categories:
            next_category = category
            break

    # Для категории определяем список тегов
    selector_items = get_selector_items(related_tags, next_category)

    # Формируем ответ
    answer = {
        "result": "selector",
        "selector_name": next_category,
        "selector_description": TAG_CATEGORY_MAP.get(next_category, "Выбрать"),
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
        file_versions = FileVersion.objects.filter(resource=resource).order_by('-last_changed','-timestamp')
        last_version = file_versions.first()
        if file_versions.count() > 2:
            last_last_version = file_versions[1]
        else:
            last_last_version = None
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
            "last_update" : last_version.timestamp,
            "download_url": download_url,
            "view_urls" : view_urls,
            "archive_urls" : archive_urls
        }
        if last_last_version is not None:
            res_data["last_last_update"] = last_last_version.timestamp

        files.append(res_data)

    # Формируем ответ
    answer = {
        "result": "files",
        "files": files
    }

    return answer