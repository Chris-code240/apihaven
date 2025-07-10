import uuid
from pydantic import BaseModel, Field as PydanticField, field_validator, model_validator
from typing import List, Optional
from django.contrib.auth.models import User
from .models import UserProject
import datetime
import hashlib
from pydantic import ValidationInfo
from main.middlewares import current_request

from django.apps import apps

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
    ('foreign_key', 'ForeignKey'),
    ('ont_to_one', 'OneToOne'),
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
    target_model: Optional[str] = None
    
    @field_validator('target_model')
    def validate_target_model(cls, v, info: ValidationInfo):
        if v is None:
            return v 
        try:
            model = apps.get_model(app_label="api", model_name=v)
            project_id = current_request.get_current_project()
            project = UserProject.objects.get(project_id=project_id)

            # Check if model belongs to the current project
            if getattr(model, 'project_pk', None) != project.pk:
                raise ValueError(f"Target model <{v}> does not belong to this project")
            return v

        except LookupError:
            raise ValueError(f"Target model <{v}> not found in app 'api'")
        except UserProject.DoesNotExist:
            raise ValueError("Current project context is invalid or missing")
        except Exception as e:
            raise ValueError(f"Error validating target_model: {str(e)}")
    


    @model_validator(mode="after")
    def validate_type_and_target_model(self):
        if self.target_model:
            if self.type not in {"foreign_key", "one_to_one"}:
                raise ValueError(f"Field type '{self.type}' is not allowed with a target_model")
        else:
            if self.type in {"foreign_key", "one_to_one"}:
                raise ValueError(f"Field of type '{self.type}' must have a target_model specified")
        return self



    @field_validator('type')
    def validate_type(cls, v):
        if v not in dict(FIELD_TYPE_CHOICES):
            raise ValueError(f"Invalid type: {v}")
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
    project_id:str
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
        if not UserProject.objects.filter(project_id=v).exists():
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
            print(self._erros)
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

        # ✅ New: Check relationship fields
        from .models import UserProject  # ensure local import

        try:
            user_project = UserProject.objects.get(project_id=self.project_id)
        except UserProject.DoesNotExist:
            raise ValueError("Invalid project ID")

        existing_model_names = {
            s['model_name']: s.get("migration_status", "PENDING")
            for s in user_project.schemas
        }

        for field in self.fields:
            if field.type in ('foreign_key', 'one_to_one'):
                if not field.target_model:
                    raise ValueError(f"Field '{field.name}' must specify 'target_model' for relationships")

                status = existing_model_names.get(field.target_model)
                if not status:
                    raise ValueError(f"Target model '{field.target_model}' not found in project")
                if status != "SUCCESS":
                    raise ValueError(f"Target model '{field.target_model}' is not yet migrated")

    def save(self):
        from .models import UserProject  # ensure local import

        user_project = UserProject.objects.get(project_id=self.project_id)

        existing_names = [s['name'] for s in user_project.schemas]

        if self.name in existing_names:
            raise ValueError(f"Schema <{self.name} /> already exists")
        
        if self.use_for_auth:
            reserved = {"username", "email", "password"}
            self.fields = [f for f in self.fields if f.name.lower() not in reserved]

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
('Invalid project ID')

