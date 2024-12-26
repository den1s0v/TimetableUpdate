from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def choose_degree(request):
    degrees = [
        {
            'title': 'Бакалавриат (специалитет)',
            'url': 'schedule_bachelor_form_find.html',
            'image': 'bachelor_image.png',
            'css_class': 'degree-card-bachelor',
            'separator_class': 'degree-card-separator-line-bachelor',
        },
        {
            'title': 'Магистратура',
            'url': 'schedule_master_form_find.html',
            'image': 'master_image.png',
            'css_class': 'degree-card-master',
            'separator_class': 'degree-card-separator-line-master',
        },
        {
            'title': 'Аспирантура',
            'url': 'schedule_postgraduate_form_find.html',
            'image': 'phd_image.png',
            'css_class': 'degree-card-postgraduate',
            'separator_class': 'degree-card-separator-line-postgraduate',
        },
    ]
    return render(request, 'choose_degree.html', {'degrees': degrees})

def timetable_list(request):
    first_select_items = [
        'Очная',
        'Очно-заочная форма',
        'Заочная'
    ]
    return render(request, 'timetable_list.html', {'first_select_items': first_select_items})

def timetable_params(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    tags = dict(request.GET)
    for key, value in tags.items():
        print(key, value)

    answer = {
        "result" : "selector",
        "selector_name" : "Факультет",
        "selector_description" : "Выбрать факультет",
        "selector_items" : [
            "ФЭВТ",
            "ХТФ",
            "ФАСТИВ"
        ]
    }
    return JsonResponse(answer)
