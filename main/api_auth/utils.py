import importlib

def import_serializer(model_name: str):
    """
    Import the serializer class for the given model name from the auto-generated serializers.
    Assumes the serializer is named as <ModelName>Serializer in api.serializers_generated.
    """
    module_path = "api.serializers_generated"
    serializer_class_name = f"{model_name}Serializer"

    try:
        module = importlib.import_module(module_path)
        serializer_class = getattr(module, serializer_class_name)
        return serializer_class
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Could not import serializer '{serializer_class_name}' from '{module_path}': {e}")
