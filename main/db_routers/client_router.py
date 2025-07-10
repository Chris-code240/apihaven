from main.middlewares.current_request import get_current_request
from main.models import UserProject
from uuid import UUID
from django.conf import settings
from main.middlewares.current_request import get_current_request, get_current_project
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

class ClientRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label != 'api':
            return None

        # 1. Hints
        if (db_alias := hints.get("db_alias")):
            return db_alias

        # 2. Background model introspection
        if (project_pk := getattr(model, 'project_pk', None)):
            try:
                user_project = UserProject.objects.get(pk=project_pk)
                db_alias = list(user_project.database.keys())[0]
                settings.DATABASES.update(user_project.database)
                return db_alias
            except UserProject.DoesNotExist:
                print("User does not exist")
                return 'default'
            except Exception as e:
                print(f"Routing Error: {e}")
                return 'default'

   
        project_id = get_current_project()
        if project_id:
            try:
                user_project = UserProject.objects.get(project_id=project_id)
                db_alias = list(user_project.database.keys())[0]
                settings.DATABASES.update(user_project.database)
                return db_alias
            except UserProject.DoesNotExist:
                pass
            except Exception as e:
                print(e)
                pass

            return 'default'
    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)



    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label != "api":
            return None

        if model_name is None:
            print("model is None so...no migration")
            return False
        
        model = apps.get_model(app_label="api", model_name=model_name)
        if hasattr(model, 'project_pk'):
            project = UserProject.objects.get(pk = model.project_pk)
            print("model has pk but db in database is ", db in project.database)

            return db in project.database
        print("Model has no pk so No migration")
        return False