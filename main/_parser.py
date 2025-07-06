import uuid
from pydantic import BaseModel, Field as PydanticField, field_validator
from typing import List, Optional
from django.contrib.auth.models import User
from .models import UserProject
import datetime
import hashlib
from pydantic import ValidationInfo



ACTION_CHOICES = [
    ('getAll','Get All'),
    ('create','Create'),
    ('delete','Delete'),
    ('update','Update'),
]

FIELD_TYPE_CHOICES = [
    ('str', 'String'),
    ('int', 'Integer'),
    ('float', 'Float'),
    ('bool', 'Boolean'),
    ('link', 'Link'),
]

PENDING = "pending"
APPLIED = "applied"
FAILED = "failed"
class Field(BaseModel):
    name: str
    blank: bool = True
    null: bool = True
    type: str
    primary_key: bool = False
    link_to: Optional[str] = None
    

    @field_validator('type')
    def validate_type(cls, v):
        if v not in dict(FIELD_TYPE_CHOICES):
            raise ValueError(f"Invalid type: {v}")
        return v

    @field_validator('link_to')
    def validate_link_to(cls, v, info: ValidationInfo):
        if info.data.get('type') == 'link' and not v:
            raise ValueError("link_to must be provided when type is 'link'")
        if info.data.get('type') != 'link' and v:
            raise ValueError("link_to must be None unless type is 'link'")
        return v
    



class ModelSchema(BaseModel):
    name: str
    use_for_auth: bool = False
    auth: bool = False
    actions: List[str]
    fields: List[Field]
    internal_id: str = PydanticField(default_factory=lambda: str(uuid.uuid4()))
    created_at:str = PydanticField(default_factory= lambda:str(datetime.datetime.now()))
    migration_status:str = PENDING
    project_id:int
    _valid: bool = False
    _erros:List = []
    model_name:str = ""


    @field_validator('actions')
    def validate_actions(cls, v):
        for i in v:
            if i not in dict(ACTION_CHOICES):
                raise ValueError(f"Invalid Model Action: {i}")
        return v
    

    @field_validator('project_id')
    def validate_dev_id(cls, v):
        if not UserProject.objects.filter(id=v).exists():
            raise ValueError(f"Project <{v}/> does not exist")
        return v
    def get_errors(self):
        return self._erros
    
    def is_valid(self) -> bool:
        try:
            self.clean()
            self._valid = True
            return True

        except Exception as e:
            self._erros.append(e)
            return False

    def clean(self) -> None:
        if not all(i.isalnum() or i == '_' for i in self.name):
            raise ValueError("Model name must be alphanumeric or underscore only")

        if self.use_for_auth:
            self.auth = True
            pk_fields = [f for f in self.fields if f.primary_key]
            if len(pk_fields) != 1:
                raise ValueError("Authentication model must have exactly one primary key")
            pk_fields[0].blank = False
            pk_fields[0].null = False


    def save(self):
        user_project = UserProject.objects.get(id=self.project_id)
    
        existing_names = [s['name'] for s in user_project.schemas]
        if self.name in existing_names:
            raise ValueError(f"Schema <{self.name} /> already exists")

        uid = hashlib.md5(f"{self.name}_{user_project.project_id}".encode()).hexdigest()[:6]
        model_name = f"{self.name}_{uid}"
        self.model_name = model_name

        user_project.schemas.append(self.model_dump()) 
        user_project.save()

    
    def update(self):
        # update schema
        pass
    def delete(self):
        pass
    def get(self):
        pass

class UpdateSchema(BaseModel):
    pass


# example usage

class ProjectSchema(BaseModel):
    name:str
    models:list[ModelSchema] = []


