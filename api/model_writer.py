import os
from main._parser import Field
import uuid
GENERATED_MODELS_FILE = os.path.join(os.path.dirname(__file__), "models_generated.py")

def write_model_to_file(model_name: str, fields: list[str],user_profile_pk):
    """
    Writes a Django model to models_generated.py if it doesn't already exist.
    """
    
    fields.append(f"    project_pk = {user_profile_pk}")
    field_lines = '\n'.join(fields)
    
    model_code = f"""
class {model_name}(models.Model):
{field_lines}
    class Meta:
        app_label = 'api'
"""

    # Check for existence
    if os.path.exists(GENERATED_MODELS_FILE):
        with open(GENERATED_MODELS_FILE, 'r') as file:
            if f"class {model_name}(" in file.read():
                print(f"[SKIP] Model {model_name} already exists.")
                return

    # Write (append) the new model
    with open(GENERATED_MODELS_FILE, 'a') as file:
        file.write("\n" + model_code.strip() + "\n")

    print(f"[OK] Model {model_name} written to models_generated.py")


def field_to_django(field:Field):
    INDENT = "    "
    name = field.name
    ftype = field.type
    options = []

    if field.primary_key:
        options.append("primary_key=True")
    else:
        options.append(f"blank={field.blank}")
        options.append(f"null={field.null}")
    
    field_map = {
        "str": "CharField(max_length=255,",
        "int": "IntegerField(",
        "float": "FloatField(",
        "bool": "BooleanField(",
        "text": "TextField(",
    }

    

    if ftype not in field_map:
        raise ValueError(f"Unsupported field type: {ftype}")

    return f"{INDENT}{name} = models.{field_map[ftype]}{', '.join(options)})"



# print(field_to_django(Field(name="id", blank=True, null=True, type="text")))