from rest_framework import serializers
from .models import DiseaseDetection


class DiseaseDetectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = DiseaseDetection
        fields = [
            'id',
            'crop',
            'disease',
            'confidence',
            'status',
            'detected_at'
        ]
