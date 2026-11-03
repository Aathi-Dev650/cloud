"""MobileNetV2 disease-classification inference, loaded only when requested."""
from functools import lru_cache
import json
from pathlib import Path

from django.conf import settings


class ModelUnavailable(Exception):
    """Raised when the trained model artifact is not ready for inference."""


@lru_cache(maxsize=1)
def _load_model_and_labels():
    model_path = Path(settings.DISEASE_MODEL_PATH)
    labels_path = Path(settings.DISEASE_LABELS_PATH)
    if not model_path.is_file() or not labels_path.is_file():
        raise ModelUnavailable('Disease model is not installed. Train it with ml/train.py, then restart the server.')
    try:
        import tensorflow as tf
        import numpy as np
        import cv2
    except ImportError as exc:
        raise ModelUnavailable('TensorFlow/OpenCV is not installed. Run pip install -r requirements.txt.') from exc
    try:
        labels = json.loads(labels_path.read_text(encoding='utf-8'))
        model = tf.keras.models.load_model(model_path, compile=False)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise ModelUnavailable(f'Could not load disease model: {exc}') from exc
    if not isinstance(labels, list) or not labels:
        raise ModelUnavailable('The model labels file must be a non-empty JSON list.')
    return model, labels, tf, np, cv2


def predict_disease(uploaded_image):
    """Return a model label, model probability, and an image-derived crop name."""
    model, labels, tf, np, cv2 = _load_model_and_labels()
    try:
        encoded = np.frombuffer(uploaded_image.read(), dtype=np.uint8)
        source = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        if source is None:
            raise ValueError('Image decoder returned no pixels.')
    except (OSError, ValueError) as exc:
        raise ValueError('The uploaded file is not a valid image.') from exc
    image = cv2.resize(source, (224, 224), interpolation=cv2.INTER_AREA)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # The saved model includes MobileNetV2 preprocessing as its second layer;
    # pass raw 0--255 RGB pixels here so inference exactly matches training.
    batch = np.expand_dims(image.astype(np.float32), axis=0)
    scores = model.predict(batch, verbose=0)[0]
    index = int(np.argmax(scores))
    if index >= len(labels):
        raise ModelUnavailable('The model output count does not match the labels file.')
    label = str(labels[index])
    confidence = round(float(scores[index]) * 100, 2)
    if float(scores[index]) < settings.DISEASE_MIN_CONFIDENCE:
        return {
            'label': 'unknown_retake_photo',
            'crop': 'unknown',
            'disease': 'Unable to identify confidently',
            'confidence': confidence,
            'needs_retake': True,
        }
    # Supports PlantVillage labels and the underscore-only labels emitted by
    # the supplied training archive (for example ``Tomato_Early_blight``).
    if '___' in label:
        crop, disease = label.split('___', 1)
        crop, disease = crop.replace('_', ' '), disease.replace('_', ' ')
    elif ' - ' in label:
        crop, disease = label.split(' - ', 1)
    else:
        crop, separator, disease = label.partition('_')
        if not separator:
            crop, disease = 'unknown', label
        else:
            disease = ' '.join(disease.replace('_', ' ').split())
    crop = ' '.join(crop.replace('_', ' ').split()).lower()
    return {'label': label, 'crop': crop, 'disease': disease, 'confidence': confidence, 'needs_retake': False}
