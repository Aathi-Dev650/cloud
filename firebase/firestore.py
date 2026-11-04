"""Initialize the Firebase Admin SDK and provide the configured Firestore client."""
from pathlib import Path

import firebase_admin
from django.conf import settings
from firebase_admin import credentials, firestore


def client():
    if not firebase_admin._apps:
        if not settings.GOOGLE_APPLICATION_CREDENTIALS:
            raise RuntimeError('Set GOOGLE_APPLICATION_CREDENTIALS to your local Firebase service-account JSON file.')
        credential_path = Path(settings.GOOGLE_APPLICATION_CREDENTIALS)
        if not credential_path.is_absolute():
            credential_path = settings.BASE_DIR / credential_path
        if not credential_path.is_file():
            raise RuntimeError(f'Firebase service-account file not found: {credential_path}')
        credential = credentials.Certificate(str(credential_path))
        firebase_admin.initialize_app(credential)
    return firestore.client(database_id=settings.FIRESTORE_DATABASE)
