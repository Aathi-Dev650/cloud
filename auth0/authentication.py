"""Validate Auth0 access tokens issued for the CropCure API."""
import jwt
from jwt.exceptions import PyJWKClientError, PyJWTError
from django.conf import settings
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed


class Auth0User:
    is_authenticated = True
    is_active = True
    is_staff = False
    is_superuser = False

    def __init__(self, claims):
        self.sub = claims['sub']
        self.username = self.sub
        self.email = claims.get('email', '')
        self.first_name = claims.get('name', '')

    def __str__(self):
        return self.sub


class Auth0JWTAuthentication(BaseAuthentication):
    def authenticate_header(self, request):
        return 'Bearer'

    def authenticate(self, request):
        header = get_authorization_header(request).split()
        if not header:
            return None
        if len(header) != 2 or header[0].lower() != b'bearer':
            raise AuthenticationFailed('Use an Auth0 bearer access token.')
        if not settings.AUTH0_DOMAIN or not settings.AUTH0_AUDIENCE:
            raise AuthenticationFailed('Auth0 API settings are missing. Configure AUTH0_DOMAIN and AUTH0_AUDIENCE.')
        issuer = f"https://{settings.AUTH0_DOMAIN}/"
        try:
            signing_key = jwt.PyJWKClient(f"{issuer}.well-known/jwks.json").get_signing_key_from_jwt(header[1].decode())
            claims = jwt.decode(
                header[1], signing_key.key, algorithms=['RS256'],
                audience=settings.AUTH0_AUDIENCE, issuer=issuer,
            )
        except (PyJWTError, PyJWKClientError, UnicodeDecodeError) as exc:
            raise AuthenticationFailed('The Auth0 access token is invalid or expired.') from exc
        return Auth0User(claims), claims
