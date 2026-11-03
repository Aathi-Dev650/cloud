from django.urls import path

from .views import (
    test_api,
    create_detection,
    farmer_profile,
    detection_history,
)


urlpatterns = [

    path(
        'test/',
        test_api
    ),

    path(
        'create/',
        create_detection
    ),
    path('auth/me/', farmer_profile),
    path('auth/profile/', farmer_profile),
    path('history/', detection_history),
]
