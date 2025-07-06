from rest_framework.views import APIView
from .serializers import User, UserSerializer
from .models import UserProfile
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework. response import Response
from rest_framework import status
import logging
from django.forms.models import model_to_dict
from rest_framework_simplejwt.authentication import JWTAuthentication
from ._parser import Field, ModelSchema, ProjectSchema
from .models import UserProfile, UserProject
from ._parser import ModelSchema, Field
from .tasks import migrate_model
from .db_parser import DBConfig
from django.db import transaction


def delete_all():
    for u in User.objects.all():
        u.delete()
# delete_all()

# print(UserProject.objects.get())


logger = logging.getLogger(__name__)


class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Signup failed: {str(e)}", exc_info=True)  # 🔥 logs stack trace
            return Response({
                'success': False,
                'message': str(e),
            }, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
            logger.error(f"Signup failed: Unimplemnted Method /GET", exc_info=True)  # 🔥 logs stack trace
            return Response({
                'success': False,
                'message': "Method not Implemented",
            }, status=status.HTTP_403_FORBIDDEN)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


    def get(self,request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            return Response({"success":True, "data":profile}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success":False, "message":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def patch(self, request):
        try:
            data = request.data
            user = request.user
            userprofile = UserProfile.objects.get(user= user)
            with transaction.atomic():
                for field in data.keys():
                    field = field.lower()
                    if field == 'password':
                        user.set_password(data[field])
                        continue
                    if field == 'database':
                        db_data = data[field]
                        config = DBConfig(
                            name=db_data['name'],
                            user_profile_id=str(userprofile.profile_id),
                            db_engine_name=db_data['engine'],
                            db_host=db_data['host'],
                            db_user=db_data['user'],
                            db_port=str(db_data['port']),
                            db_password=db_data['password'],
                            options=db_data.get('options',{})
                        )

                        if config.is_valid():
                            userprofile.database = config.get()
                            # register_database(config.get())
                            
                            userprofile.save()
                            continue
                        raise ValueError("Invalid database data")
                       
                    if hasattr(user, field):
                        setattr(user, field, data[field])
                    elif hasattr(userprofile, field):
                        setattr(userprofile, field, data[field])

                user.save()
                userprofile.save()
                return Response({"success":True, "data":userprofile.get()}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"success":False, "message":str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        try:
            request.user.delete()
            return Response({"success":True, "data":{}}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"success":False, "message":str(e.args)}, status=status.HTTP_400_BAD_REQUEST)

class ProjectView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def post(self, request):
        try:
            with transaction.atomic():
                user = request.user
                userprofile = UserProfile.objects.get(user = user)
                data = request.data or {}

                # {name:project_name, database:{db_config}}
                db_data = data.get('database',{})
                if db_data != {}:
                    config = DBConfig(
                    name=db_data['name'],
                    user_profile_id=str(userprofile.profile_id),
                    db_engine_name=db_data['engine'],
                    db_host=db_data['host'],
                    db_user=db_data['user'],
                    db_port=str(db_data['port']),
                    db_password=db_data['password'],
                    options=db_data.get('options',{})
                )

                    if config.is_valid():
                        userprofile.database = config.get()
                        project = UserProject.objects.create(user_profile=userprofile, name=data.get('name'), database=config.get())
                        project.save()
                        return Response({"success":True, "data":project.get()}, status=status.HTTP_201_CREATED)
                    return Response({"success":False, "message":"Invalid Database config"}, status=status.HTTP_400_BAD_REQUEST)
                
                project = UserProject.objects.create(name=data.get('name'), user_profile=userprofile)
                project.save()
                
                    
                return Response({"succcess":True, "data":project.get()}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"success":False, "message":str(e)}, status=status.HTTP_400_BAD_REQUEST)
    def patch(self, request):
        try:
            with transaction.atomic():
                user = request.user
                userprofile = UserProfile.objects.get(user=user)
                project_id = request.headers.get("X-Project-ID")
                project = UserProject.objects.get(project_id = project_id,user_profile=userprofile)
                data = request.data
                for field in data:
                    if field == "database":
                        db_data = data.get('database')
                        config = DBConfig(
                        name=db_data['name'],
                        user_profile_id=str(userprofile.profile_id),
                        db_engine_name=db_data['engine'],
                        db_host=db_data['host'],
                        db_user=db_data['user'],
                        db_port=str(db_data['port']),
                        db_password=db_data['password'],
                        options=db_data.get('options',{})
                        )
                        if config.is_valid():
                            userprofile.database = config.get()
                            project = UserProject.objects.create(user_profile=userprofile, name=data.get('name'), database=config.get())
                            project.save()
                    else:
                        if hasattr(project, field):
                            setattr(project, field, data[field])
                project.save()
                return Response({"success":True, "data":project.get()}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"success":False, "message":str(e)}, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request, project_id=None):
        try:
            user = request.user
            userprofile = UserProfile.objects.get(user=user)
            projects = [p.get() for p in UserProject.objects.filter(user_profile=userprofile).all()]
            return Response({"success":True, "data":projects}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success":False, "message":str(e)}, status=status.HTTP_400_BAD_REQUEST)
class ModelView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


    def post(self, request):
        try:
            with transaction.atomic():
                user = request.user
                data = request.data
                project_id = data.get('project_id')
                project = UserProject.objects.get(project_id=project_id, user_profile__user=user)
                model_name = data.get('name')
                params = data.get('params', {})
                use_for_auth = params.get('use_for_auth', False)
                auth = params.get('auth', False)
                actions = params.get('actions', [])
                raw_fields = params.get('fields', [])

                fields = []
                for field_dict in raw_fields:
                    fields.append(Field(**field_dict))

                model_schema = ModelSchema(
                    name=model_name,
                    use_for_auth=use_for_auth,
                    auth=auth,
                    actions=actions,
                    fields=fields,
                    project_id=project.id
                )

                if not model_schema.is_valid():
                    return Response({"error": "Invalid schema"}, status=status.HTTP_400_BAD_REQUEST)

        
                existing = any(s.get("name") == model_schema.name for s in project.schemas)
                if existing:
                    return Response({"error": "Schema already exists"}, status=status.HTTP_400_BAD_REQUEST)

                
                model_schema.save()
                schema_data = model_schema.model_dump()
                project.schemas.append(schema_data)
                project.save()
                migrate_model.delay(str(model_schema.name), project.project_id)

                return Response({"message": "Schema saved and migration started"}, status=status.HTTP_201_CREATED)
        
            # return Response(request.data)
            
        except Exception as e:
            return Response({"success":False, "message":"View " +str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, model_name:str = None):
        try:
            project_id = request.headers.get("X-Project-ID")
            user = request.user
            if not model_name:
                project = UserProject.objects.get(project_id  = project_id, user_profile__user=user)
                return Response({"success":True, "data":project.schemas}, status=status.HTTP_200_OK)
            for schema in project.schemas:
                if schema['model_name'] == model_name:
                    return Response({"success":True, "data":schema}, status=status.HTTP_200_OK)
            raise ValueError(f"Model with name <{model_name}> does not exist")
        except Exception as e:
            return Response({"success":False, "message":str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
       


