from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timezone
from dropbox.exceptions import DropboxException
from google.api_core.exceptions import GoogleAPICallError
from firebase_admin.exceptions import FirebaseError
import json
from pathlib import Path
from .inference import ModelUnavailable, predict_disease
from .models import DiseaseDetection, FarmerProfile
from dropbox_integration.storage import client as dropbox_client, save_photo, temporary_photo_link
from firebase.firestore import client as firestore_db


LOW_CONFIDENCE_THRESHOLD = 55


def _guidance_for(database, prediction):
    """Fetch editorial guidance; the neural network supplies only the class."""
    for snapshot in database.collection('diseases').stream():
        item = snapshot.to_dict() or {}
        if item.get('model_label') == prediction['label'] or (
            str(item.get('crop', '')).lower() == prediction['crop'].lower()
            and str(item.get('disease', '')).lower() == prediction['disease'].lower()
        ):
            return item
    return None


def _serialize(document):
    document['id'] = str(document.pop('_id', document.get('id', '')))
    path = document.pop('image_path', '')
    document['image_url'] = ''
    if path:
        try:
            document['image_url'] = temporary_photo_link(path)
        except Exception:
            pass
    document.pop('owner', None)
    document.pop('model_label', None)
    return document


@ensure_csrf_cookie
def app_shell(request):
    return render(request, 'disease_detection/app.html', {'auth0_config': {
        'domain': settings.AUTH0_DOMAIN,
        'clientId': settings.AUTH0_CLIENT_ID,
        'audience': settings.AUTH0_AUDIENCE,
        'redirectUri': settings.AUTH0_CALLBACK_URL,
        'logoutUri': settings.AUTH0_LOGOUT_URL,
    }})


def _frontend_bridge():
    """Inject public Auth0 SPA settings into the static multi-page UI."""
    config = {
        'domain': settings.AUTH0_DOMAIN,
        'clientId': settings.AUTH0_CLIENT_ID,
        'audience': settings.AUTH0_AUDIENCE,
        'redirectUri': settings.AUTH0_CALLBACK_URL,
        'logoutUri': settings.AUTH0_LOGOUT_URL,
    }
    serialized = json.dumps(config).replace('</', '<\\/')
    return (
        '<link rel="stylesheet" href="/static/css/multipage-app.css">'
        '<link rel="stylesheet" href="/static/css/tamil-heritage.css">'
        f'<script>window.CROPCURE_AUTH0={serialized};</script>'
        '<script src="https://cdn.auth0.com/js/auth0-spa-js/2.1/auth0-spa-js.production.js"></script>'
        '<script src="/static/js/auth0-bootstrap.js"></script>'
        '<script src="/static/js/multipage-app.js"></script>'
    )


def supplied_page(request, page):
    """Serve an original supplied UI page without parsing its JS bindings."""
    pages = {'home', 'detection', 'recommend', 'history', 'profile', 'index', 'signup'}
    if page not in pages:
        from django.http import Http404
        raise Http404
    from django.http import HttpResponse
    from pathlib import Path
    page_file = Path(settings.BASE_DIR) / 'frontend' / 'templates' / 'pages' / f'{page}.html'
    html = page_file.read_text(encoding='utf-8')
    bridge = _frontend_bridge()
    return HttpResponse(html.replace('</body>', f'{bridge}</body>'), content_type='text/html; charset=utf-8')


@staff_member_required(login_url='/admin/login/')
def control_centre(request):
    """A compact, staff-only operating view for the local CropCure service."""
    labels_path = Path(settings.DISEASE_LABELS_PATH)
    try:
        labels = json.loads(labels_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        labels = []
    recent = DiseaseDetection.objects.select_related('user').order_by('-detected_at')[:12]
    context = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'total_analyses': DiseaseDetection.objects.count(),
        'review_count': DiseaseDetection.objects.filter(status='Needs review / retake photo').count(),
        'model_labels': labels,
        'model_available': labels_path.is_file() and Path(settings.DISEASE_MODEL_PATH).is_file(),
        'model_threshold': int(settings.DISEASE_MIN_CONFIDENCE * 100),
        'recent_analyses': recent,
        'users': User.objects.select_related('farmer_profile').order_by('-date_joined')[:12],
        'crop_summary': DiseaseDetection.objects.values('crop').annotate(total=Count('id')).order_by('-total')[:6],
    }
    return render(request, 'disease_detection/control_centre.html', context)


@staff_member_required(login_url='/admin/login/')
def toggle_user_access(request, user_id):
    """Enable/disable a farmer account without exposing privilege escalation."""
    if request.method != 'POST':
        return redirect('control-centre')
    user = get_object_or_404(User, pk=user_id)
    if user == request.user:
        messages.error(request, 'You cannot disable your own administrator account.')
    elif user.is_superuser or user.is_staff:
        messages.error(request, 'Manage staff accounts through Django administration.')
    else:
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        messages.success(request, f"{user.username} is now {'active' if user.is_active else 'disabled'}.")
    return redirect('control-centre')


@api_view(['GET'])
@permission_classes([AllowAny])
def test_api(request):
    return Response({
        "message": "CropCure API is working!",
        "status": "success"
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def farmer_profile(request):
    """Read or update the Firestore profile identified by the verified Auth0 sub."""
    try:
        database = firestore_db()
        profile_ref = database.collection('users').document(request.user.sub)
        snapshot = profile_ref.get()
        profile = snapshot.to_dict() if snapshot.exists else {}
        if request.method == 'POST':
            for field in ('full_name', 'email', 'mobile_number', 'district', 'state', 'language'):
                if field in request.data:
                    profile[field] = str(request.data[field]).strip()
            profile.setdefault('full_name', request.user.first_name or request.user.username)
            profile.setdefault('email', request.user.email)
            profile.setdefault('state', 'Tamil Nadu')
            profile.setdefault('language', 'English')
            profile.setdefault('created_at', datetime.now(timezone.utc))
            profile['updated_at'] = datetime.now(timezone.utc)
            profile_ref.set(profile, merge=True)
    except (RuntimeError, GoogleAPICallError, FirebaseError, OSError) as exc:
        return Response({'detail': f'Firestore is not ready: {exc}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({
        'username': request.user.username,
        'name': profile.get('full_name') or request.user.first_name or request.user.username,
        'email': profile.get('email') or request.user.email,
        'mobile_number': profile.get('mobile_number', ''),
        'district': profile.get('district', ''),
        'state': profile.get('state', 'Tamil Nadu'),
        'language': profile.get('language', 'English'),
        'joined_at': profile.get('created_at'),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_detection(request):
    image = request.FILES.get('image')
    if not image:
        return Response({'detail': 'Please select a leaf image.'}, status=400)
    if not image.content_type or not image.content_type.startswith('image/'):
        return Response({'detail': 'Please upload a valid image file.'}, status=400)
    if image.size > 10 * 1024 * 1024:
        return Response({'detail': 'Image must be smaller than 10 MB.'}, status=400)
    try:
        prediction = predict_disease(image)
    except (ModelUnavailable, ValueError) as exc:
        return Response({'detail': str(exc)}, status=503)
    low_confidence = prediction['confidence'] < LOW_CONFIDENCE_THRESHOLD
    assessment_status = 'Needs review / retake photo' if prediction.get('needs_retake') or low_confidence else ('No Disease Detected' if prediction['disease'].lower() == 'healthy' else 'Disease Detected')
    photo_path = ''
    try:
        image.seek(0)
        photo_path = save_photo(request.user.sub, image)
        database = firestore_db()
        guidance = _guidance_for(database, prediction)
        document = {
            'owner': request.user.sub,
            'crop': prediction['crop'],
            'model_label': prediction['label'],
            'disease': prediction['disease'],
            'confidence': prediction['confidence'],
            'status': assessment_status,
            'needs_retake': prediction.get('needs_retake', False),
            'guidance_available': bool(guidance),
            'created_at': datetime.now(timezone.utc),
            'image_path': photo_path,
            'image_name': Path(image.name).name,
            'image_content_type': image.content_type,
        }
        if guidance:
            document['symptoms'] = guidance.get('symptoms', [])
            document['solution'] = guidance.get('solution', [])
            document['prevention'] = guidance.get('prevention', [])
        document_ref = database.collection('crop_analyses').document()
        document_ref.set(document)
        document['_id'] = document_ref.id
        return Response(_serialize(document), status=status.HTTP_201_CREATED)
    except (RuntimeError, DropboxException, GoogleAPICallError, FirebaseError, OSError) as exc:
        if photo_path:
            try:
                dropbox_client().files_delete_v2(photo_path)
            except Exception:
                pass
        return Response({'detail': f'Cloud storage is not ready: {exc}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detection_history(request):
    try:
        database = firestore_db()
        from google.cloud.firestore_v1 import FieldFilter
        items = database.collection('crop_analyses').where(filter=FieldFilter('owner', '==', request.user.sub)).order_by('created_at', direction='DESCENDING').limit(50).stream()
        return Response([_serialize({**item.to_dict(), '_id': item.id}) for item in items])
    except (RuntimeError, GoogleAPICallError, FirebaseError, OSError) as exc:
        return Response({'detail': f'Firestore is not ready: {exc}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
