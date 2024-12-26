from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница
    path('choose_degree', views.choose_degree, name='choose_degree'),  # Главная страница
    path('timetable', views.timetable_list, name='timetable'),
    path('timetable_params', views.timetable_params, name='timetable_params' ),
]
