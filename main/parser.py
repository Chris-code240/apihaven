from pydantic import BaseModel
MODEL_ACTIONS = ["getAll", "create", "update"] # for now we are limiting it to basic CRUD, no complex query
from pydantic import BaseModel
from django.db import models

class FieldSchema(BaseModel):
    name: str
    type: str  # text, number, link
    primary_key: bool = False
    max_length: int | None = None
    links_to: str | None = None

class DataTypeSchema(BaseModel):
    dataType: str
    fields: list[FieldSchema]
    actions: list[str] = []
    auth: str | None = None

# Example schema from UI
schema = DataTypeSchema(
    dataType="Order",
    fields=[
        FieldSchema(name="order_id", type="text", primary_key=True),
        FieldSchema(name="user", type="link", links_to="User"),
        FieldSchema(name="total_price", type="number"),
        FieldSchema(name="status", type="text", max_length=20)
    ],
    actions=["getAll", "create", "update"],
    auth="loginRequired"
)

# Map to Django
FIELD_MAP = {"text": models.CharField, "number": models.IntegerField, "link": models.ForeignKey}
def create_model(schema: DataTypeSchema):
    fields = {}
    for f in schema.fields:
        field_type = FIELD_MAP[f.type]
        kwargs = {"primary_key": f.primary_key} if f.primary_key else {}
        if f.max_length:
            kwargs["max_length"] = f.max_length
        if f.links_to:
            kwargs["to"] = f.links_to
            kwargs["on_delete"] = models.CASCADE
        fields[f.name] = field_type(**kwargs)
    return type(schema.dataType, (models.Model,), {"__module__": "dynamic", **fields})

