from . import _parser
from django.conf import settings
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from django.db import models
from django.contrib.auth.models import User
from .models import UserProfile
import importlib
import sys
from django.apps import apps

def reload_and_register_models(app_label):
    models_module = f"{app_label}.models_generated"
    
    if models_module in sys.modules:
        del sys.modules[models_module]
    
    mod = importlib.import_module(models_module)
    
    for model_name in dir(mod):
        model = getattr(mod, model_name)
        if isinstance(model, type) and issubclass(model, models.Model):
            try:
                apps.register_model(app_label, model)
            except LookupError:
                pass  

def register_database(config: dict):
    """
    Injects a new DB config into Django's settings.DATABASES at runtime.
    """
    if not isinstance(config, dict):
        raise ValueError("Expected a dictionary")

    for alias, db_settings in config.items():
        if alias not in settings.DATABASES:
            settings.DATABASES[alias] = db_settings
            print(f"📦 Database '{alias}' registered successfully.")
        else:
            raise ValueError(f"⚠️ Database '{alias}' already exists in settings.")
    return True    


ACTION_TO_VIEW = {
    "getAll": ListAPIView,
    "create": CreateAPIView,
    "getOne": RetrieveAPIView
}
MODEL_ACTIONS = ACTION_TO_VIEW.keys() # for now we are limiting it to basic CRUD, no complex query

DJANGO_COLUMNS = {
    "str": models.TextField,
    "char": models.CharField,
    "text": models.TextField,
    "number": models.IntegerField,
    "int":  models.IntegerField,
    "link": models.ForeignKey # We will come back to it.
}

def preview_model(schema: _parser.ModelSchema):
    """
    Dynamically creates a model class from schema (in-memory only).
    Useful for validation or preview — not saved or migrated.
    """
    columns = {}
    for field in schema.fields:
        column = DJANGO_COLUMNS[field.type]
        if field.primary_key:
            columns[field.name] = column(primary_key=True, unique=True)
        else:
            columns[field.name] = column(blank=field.blank, null=field.null)
    
    model = type(
        schema.model_name,
        (models.Model,),
        {
            "__module__": "",
            **columns,
            "Meta": type("Meta", (), {"app_label": "api"})
        }
    )
    return model

def create_models(modelschemas:list[_parser.ModelSchema]):
    pass 

def create_serializer():
    pass

def create_endpoints():
    pass


def create_authentiction_for_project():
    pass

def update_model(model_name:str, update_schema):
    pass

def create_app():
    pass

def create_project(project_schema:_parser.ProjectSchema):
    create_models()
    create_serializer()
    create_endpoints()
    create_authentiction_for_project()
