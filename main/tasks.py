from django.core.management import call_command
from apihaven.celery import app as celery_app 
from .models import UserProject
from . import api_generator
from ._parser import ModelSchema
from uuid import UUID
from api.model_writer import write_model_to_file, field_to_django
from api.serializer_writer import write_serializer
from api.view_writer import write_view
from api.url_writer import write_url
from django.conf import settings


@celery_app.task
def migrate_model(schema_name: str, project_id:UUID ):
    try:
        user_project = UserProject.objects.get(project_id=project_id)

        for i, s in enumerate(user_project.schemas):
            if s['name'] == schema_name:
                try:
                    schema = ModelSchema(**s)
                    lines = [field_to_django(f) for f in schema.fields]
                    write_model_to_file(schema.model_name, lines,user_project.pk)
                    from importlib import import_module
                    import_module('api.models_generated')  # or the exact path you use

                    api_generator.register_database(user_project.database)
                    api_generator.reload_and_register_models('api')
                    call_command('makemigrations', 'api', interactive=False)
                    db = list(user_project.database.keys())[0]
                    settings.DATABASES[db] = user_project.database
                    print("Using", settings.DATABASES[db], "db")

                    call_command('migrate', 'api', database=db, interactive=False)

                    write_serializer(schema.model_name)
                    write_view(schema.model_name)
                    write_url(schema.model_name)
                    s['migration_status'] = "SUCCESS"
                except Exception as e:
                    s['migration_status'] = "FAILED"
                    print("Migration error:", e)
                finally:
                    user_project.schemas[i] = s
                    user_project.save()
                break
        else:
            print(f"No schema found with name {schema_name} in project: {user_project.name}")

    except UserProject.DoesNotExist:
        print(f"UserProject with ID {project_id} does not exist")
    except Exception as e:
        print(f"Unexpected error: {e}")



