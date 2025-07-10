from rest_framework.decorators import APIView
from rest_framework import status
from rest_framework.response import Response
from main.middlewares import current_request
from django.apps import apps
import jwt
from django.conf import settings
import datetime

class APITokenObtainPairView(APIView):

    def post(self, request):
        try:
            auth_schema = current_request.get_auth_schema()
            model_name = auth_schema['model_name']
            data = request.data
            if data.get('username', None) is None or data.get('password',None) is None:
                raise ValueError("Invalid Request Data")
            auth_model = apps.get_model(app_label="api", model_name=model_name)
            instance = auth_model.objects.get(username=data.get("username"), password=data.get("password"))
            return Response({"access":jwt.encode(payload={"pk": instance.pk,"exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30),"iat": datetime.datetime.now(datetime.timezone.utc),"token_type": "access"}, key=settings.SECRET_KEY,algorithm="HS256"),
                    "refresh": jwt.encode(payload={"pk": instance.pk,"exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=60),"iat": datetime.datetime.now(datetime.timezone.utc),"token_type": "refresh"}, key=settings.SECRET_KEY,algorithm="HS256")
                    }, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({"detail":str(e)}, status=status.HTTP_400_BAD_REQUEST)

