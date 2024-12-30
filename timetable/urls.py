from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница
    path('choose_degree', views.choose_degree, name='choose_degree'),  # Главная страница
    path('timetable', views.timetable_list, name='timetable'),
    path('timetable_params', views.timetable_params, name='timetable_params' ),
    path('admin/', views.admin_panel, name='admin_panel'),
    path('login/', views.admin_login, name='admin_login'),
    path('admin/auth', views.put_google_auth_file, name='put_google_auth_file'),
    path('admin/settings', views.set_system_params, name='set_system_params'),
    path('admin/snapshot', views.snapshot, name='snapshot'),
    path('admin/manage_storage', views.manage_storage, name='timetable'),
]
