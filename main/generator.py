from pydantic import BaseModel
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from .parser import DataTypeSchema
from django.contrib.auth import models
from . import serializers
from django.urls import path
from django.core import cache

MODEL_ACTIONS = ["getAll", "create", "update"] # for now we are limiting it to basic CRUD, no complex query
ACTION_TO_VIEW = {
    "getAll": ListAPIView,
    "create": CreateAPIView,
    "getOne": RetrieveAPIView
}
SIMPLE_TO_DJANGO = {
    "text": {"type": models.CharField, "kwargs": {"max_length": 255}},
    "number": {"type": models.IntegerField, "kwargs": {}},
    "link": {"type": models.ForeignKey, "kwargs": {"on_delete": models.CASCADE}}
}
def create_model(schema:DataTypeSchema):
    fields = {}
    for field in schema["fields"]:
        mapping = SIMPLE_TO_DJANGO[field["type"]]
        kwargs = mapping["kwargs"].copy()
        if field.get("maxLength"):
            kwargs["max_length"] = field["maxLength"]
        if field.get("linksTo"):
            kwargs["to"] = field["linksTo"]
        fields[field["name"]] = mapping["type"](**kwargs)
    
    model_class = type(schema["dataType"], (models.Model,), {
        "__module__": "dynamic_models",
        **fields,
        "Meta": type("Meta", (), {"app_label": "dynamic_app"})
    })
    return model_class

def create_views(model, serializer, schema):
    views = {}
    for action in schema["actions"]:
        view_class = ACTION_TO_VIEW.get(action)
        if view_class:
            views[action] = type(f"{model.__name__}{action}View", (view_class,), {
                "queryset": model.objects.all(),
                "serializer_class": serializer,
                "authentication_classes": [schema.get("auth", "None")],
                "permission_classes": ["IsAuthenticated" if schema.get("auth") == "loginRequired" else "AllowAny"]
            })
    return views
def create_urls(model, views):
    urls = []
    for action, view in views.items():
        if action == "getAll":
            urls.append(path(f"api/{model.__name__.lower()}s/", view.as_view()))
        elif action == "getOne":
            urls.append(path(f"api/{model.__name__.lower()}s/<int:pk>/", view.as_view()))
        elif action == "create":
            urls.append(path(f"api/{model.__name__.lower()}s/create/", view.as_view()))
    return urls

def create_serializer(model, schema):
    class Meta(object):
        model = model
        fields: list | str = [f["name"] for f in schema["fields"]] | "__all__"
    
    return type(f"{model.__name__}Serializer", (serializers.ModelSerializer,), {"Meta": Meta})

def cache_components(model_name, serializer, views, urls):
    cache.set(f"api_{model_name}", {"serializer": serializer, "views": views, "urls": urls}, timeout=3600)
