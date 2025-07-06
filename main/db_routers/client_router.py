from main.middlewares.current_request import get_current_request
from main.models import UserProject
from uuid import UUID
from django.conf import settings
from main.middlewares.current_request import get_current_request, get_current_project

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

# Still baffles me why this verson of allow_mirate dont
# work as intended.
    # def allow_migrate(self, db, app_label, model_name=None, **hints):
    #     if app_label != 'api':
    #         return None

    #     db_alias = hints.get("db_alias")
    #     if db_alias:
    #         return db == db_alias
    #     return db == 'default'

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # since the previous version is not working as intended,
        # we have enforce that very migration provided a target database
                # else, nothing happens


        if app_label != 'api':
            return None
        if not settings.DEBUG and not hints.get("db_alias"):
            return False  # Never allow migrations without alias in production
        return db == hints.get("db_alias", db)


