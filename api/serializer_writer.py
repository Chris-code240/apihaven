import os
from django.apps import apps
GENERATED_SERIALIZERS_FILE = os.path.join(os.path.dirname(__file__), "serializers_generated.py")

def write_serializer(model_name: str):
    """
    Appends a ModelSerializer to serializers_generated.py if it doesn't already exist.
    """

    class_name = f"{model_name}Serializer"
    has_pk = False
    fields_ = apps.get_model(app_label="api", model_name=model_name)._meta.get_fields()
    fields = []
    for i in fields_:
        if hasattr(i, 'primary_key') and i.primary_key == True:
            has_pk = True
            continue
        fields.append(i.name)
    # Check if already written
    if os.path.exists(GENERATED_SERIALIZERS_FILE):
        with open(GENERATED_SERIALIZERS_FILE, "r") as f:
            if f"class {class_name}(" in f.read():
                print(f"[SKIP] Serializer {class_name} already exists.")
                return

    # Generate serializer code
    code = f"""
from api.models_generated import {model_name}

class {class_name}(serializers.ModelSerializer):
    class Meta:
        model = {model_name}
        fields = {fields if has_pk else '__all__'}
""".strip()

    # Append to file
    with open(GENERATED_SERIALIZERS_FILE, "a") as f:
        f.write("\n\n" + code)

    print(f"[OK] Serializer {class_name} written.")
