"""Dropbox storage for privately scoped farmer photo uploads."""
import hashlib
import uuid
from pathlib import Path

import dropbox
from django.conf import settings
from dropbox.exceptions import ApiError
from dropbox.files import WriteMode


def client():
    if not settings.DROPBOX_ACCESS_TOKEN:
        raise RuntimeError('Set DROPBOX_ACCESS_TOKEN to enable private photo storage.')
    return dropbox.Dropbox(settings.DROPBOX_ACCESS_TOKEN)


def save_photo(uid, uploaded_file):
    """Upload bytes to a private per-user Dropbox folder and return its path."""
    user_folder = hashlib.sha256(uid.encode('utf-8')).hexdigest()[:24]
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix not in {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}:
        suffix = '.jpg'
    path = f"{settings.DROPBOX_ROOT}/users/{user_folder}/{uuid.uuid4().hex}{suffix}"
    dbx = client()
    folder = ''
    for segment in (settings.DROPBOX_ROOT.strip('/'), 'users', user_folder):
        folder += f'/{segment}'
        try:
            dbx.files_get_metadata(folder)
        except ApiError:
            dbx.files_create_folder_v2(folder, autorename=False)
    dbx.files_upload(uploaded_file.read(), path, mode=WriteMode.add, autorename=False)
    return path


def temporary_photo_link(path):
    """Return a short-lived Dropbox preview URL for a verified owner's record."""
    if not path:
        return ''
    return client().files_get_temporary_link(path).link
