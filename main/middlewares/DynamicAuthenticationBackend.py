from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from api.models_generated import *
from main.middlewares.current_request import get_current_project
from main.models import UserProject
from django.conf import settings
import jwt
from django.apps import apps

class APIAuthenticationTemplate(BaseAuthentication):
    """
    Custom DRF Authentication for dynamically generated models marked with 'use_for_auth'.
    Resolves user per project via JWT.
    """
    def __init__(self,*args, **kwargs):
        super().__init__()

    def __call__(self,request):
        self.authenticate(request)
    def authenticate(self, request):
        token = self.get_token_from_request(request)
        if not token:
            return None

        try:
            payload = self.decode_token(token)
            project_id = get_current_project()
            user = self.get_user_from_payload(payload, project_id)
            if not user:
                raise AuthenticationFailed("User not found")
            return (user, None)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")
        except Exception as e:
            raise AuthenticationFailed(str(e))

    def get_token_from_request(self, request):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.split("Bearer ")[1]
        return None

    def decode_token(self, token):
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

    def get_user_from_payload(self, payload: dict, project_id):
        if payload.get("token_type") != "access":
            raise AuthenticationFailed("Invalid token type")

        user_pk = payload.get("pk", None)
        if user_pk is None:
            print(payload)
            raise AuthenticationFailed("Invalid token payload: missing user ID")

        try:
            project = UserProject.objects.get(project_id=project_id)
        except UserProject.DoesNotExist:
            raise AuthenticationFailed("Invalid project context")
        except Exception as e:
            raise AuthenticationFailed(e)

        auth_schema = next(
            (schema for schema in project.schemas if schema.get('migration_status') == "SUCCESS" and schema.get('use_for_auth') is True),
            None
        )

        if not auth_schema:
            raise AuthenticationFailed("Authentication model does not exist")

        try:
            auth_model = apps.get_model(app_label="api", model_name=auth_schema['model_name'])
            return auth_model.objects.get(pk=user_pk)
        except LookupError:
            raise AuthenticationFailed("Auth model could not be resolved")
        except auth_model.DoesNotExist:
            raise AuthenticationFailed("User not found")
