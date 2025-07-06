import os

GENERATED_VIEWS_FILE = os.path.join(os.path.dirname(__file__), "views_generated.py")

def write_view(model_name: str):
    view_class_name = f"{model_name}View"
    serializer_class_name = f"{model_name}Serializer"

    # Check for existing view
    if os.path.exists(GENERATED_VIEWS_FILE):
        with open(GENERATED_VIEWS_FILE, "r") as f:
            if f"class {view_class_name}(" in f.read():
                print(f"[SKIP] View {view_class_name} already exists.")
                return

    code = f"""
from api.models_generated import {model_name}
from api.serializers_generated import {serializer_class_name}

class {view_class_name}(APIView):
    def get(self, request):
        queryset = {model_name}.objects.all()
        serializer = {serializer_class_name}(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = {serializer_class_name}(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
""".strip()

    with open(GENERATED_VIEWS_FILE, "a") as f:
        f.write("\n\n" + code)

    print(f"[OK] View {view_class_name} written.")
