from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница
    path('choose_degree', views.choose_degree, name='choose_degree'),  # Главная страница
]
