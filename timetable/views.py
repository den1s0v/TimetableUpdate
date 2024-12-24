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
