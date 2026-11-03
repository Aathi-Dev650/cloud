from django.db import models
from django.contrib.auth.models import User


class DiseaseDetection(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    crop = models.CharField(max_length=100)

    disease = models.CharField(
        max_length=200
    )

    confidence = models.FloatField()

    status = models.CharField(max_length=100)

    detected_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.crop}: {self.disease} - {self.confidence}%"


class FarmerProfile(models.Model):
    """Contact and locale details supplied by a CropCure farmer."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    mobile_number = models.CharField(max_length=15, blank=True)
    district = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, default='Tamil Nadu')
    language = models.CharField(max_length=20, default='English')

    def __str__(self):
        return f'Profile for {self.user.username}'
