from rest_framework import status
from rest_framework.response import Response
from django.apps import apps
import jwt
from rest_framework.decorators import APIView
from main.middlewares import current_request
from .utils import import_serializer
import datetime
from django.conf import settings
class APISignUpView(APIView):
    def post(self, request):
        try:
            auth_schema = current_request.get_auth_schema()
            if auth_schema is None:
                raise ValueError("Invalid Project")

            serializer_class = import_serializer(auth_schema['model_name'])
            serializer = serializer_class(data=request.data)

            if serializer.is_valid():
                instance = serializer.save()
                access_payload = {
                        "pk": instance.pk,
                        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5),
                        "iat": datetime.datetime.now(datetime.timezone.utc),
                        "token_type": "access"
                }
                refresh_payload = {
                        "pk": instance.pk,
                        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30),
                        "iat": datetime.datetime.now(datetime.timezone.utc),
                        "token_type": "refresh"
                }

                return Response({"token":{"access":jwt.encode(payload=access_payload, key=settings.SECRET_KEY,algorithm="HS256"),"refresh":jwt.encode(payload=refresh_payload, key=settings.SECRET_KEY,algorithm="HS256")}}, status=status.HTTP_201_CREATED)
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
