from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def choose_degree(request):
    degrees = [
        {
            'title': 'Бакалавриат (специалитет)',
            'image': 'bachelor_image.png',
            'params': '?degree=bachelor',
            'css_class': 'degree-card-bachelor',
            'separator_class': 'degree-card-separator-line-bachelor',
        },
        {
            'title': 'Магистратура',
            'params': '?degree=master',
            'image': 'master_image.png',
            'css_class': 'degree-card-master',
            'separator_class': 'degree-card-separator-line-master',
        },
        {
            'title': 'Аспирантура',
            'params': '?degree=postgraduate',
            'image': 'phd_image.png',
            'css_class': 'degree-card-postgraduate',
            'separator_class': 'degree-card-separator-line-postgraduate',
        },
    ]
    return render(request, 'choose_degree.html', {'degrees': degrees})
