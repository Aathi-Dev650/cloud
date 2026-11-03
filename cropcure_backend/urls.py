from django.contrib import admin
from django.urls import path, include

from disease_detection.views import app_shell, supplied_page, control_centre, toggle_user_access


urlpatterns = [
    path('control/', control_centre, name='control-centre'),
    path('control/users/<int:user_id>/toggle/', toggle_user_access, name='toggle-user-access'),

    path('', app_shell, name='app'),
    path('<str:page>.html', supplied_page, name='supplied-page'),

    path(
        'admin/',
        admin.site.urls
    ),

    path(
        'api/disease/',
        include('disease_detection.urls')
    ),

]
