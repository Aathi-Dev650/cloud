from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from disease_detection.inference import ModelUnavailable
from auth0.authentication import Auth0User


class CropCureApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def sign_in_farmer(self):
        self.client.force_authenticate(user=Auth0User({'sub': 'auth0|test-farmer'}))

    def test_history_requires_auth0_access_token(self):
        response = self.client.get('/api/disease/history/')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.headers['WWW-Authenticate'], 'Bearer')

    def test_detection_validates_upload_before_cloud_access(self):
        self.sign_in_farmer()
        response = self.client.post('/api/disease/create/', {'crop': 'tomato'}, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], 'Please select a leaf image.')

    @patch('disease_detection.inference._load_model_and_labels')
    def test_detection_reports_a_missing_model(self, load_model):
        load_model.side_effect = ModelUnavailable('Disease model is not installed.')
        self.sign_in_farmer()
        image = SimpleUploadedFile('leaf.jpg', b'not-a-real-image', content_type='image/jpeg')
        response = self.client.post('/api/disease/create/', {'image': image}, format='multipart')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['detail'], 'Disease model is not installed.')

    def test_public_api_health_endpoint(self):
        response = self.client.get('/api/disease/test/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
