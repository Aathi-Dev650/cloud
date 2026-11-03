from django.contrib import admin

from .models import DiseaseDetection, FarmerProfile


@admin.register(DiseaseDetection)
class DiseaseDetectionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'crop',
        'disease',
        'confidence',
        'status',
        'detected_at'
    )

    list_filter = (
        'disease',
        'detected_at'
    )

    search_fields = (
        'disease',
        'user__username'
    )


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'district', 'state', 'mobile_number', 'language')
    list_filter = ('state', 'language')
    search_fields = ('user__username', 'user__email', 'district', 'mobile_number')
