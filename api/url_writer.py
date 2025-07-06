import os

GENERATED_URLS_FILE = os.path.join(os.path.dirname(__file__), "urls_generated.py")

def write_url(model_name: str):
    view_class_name = f"{model_name}View"
    url_path = model_name.lower()

    if os.path.exists(GENERATED_URLS_FILE):
        with open(GENERATED_URLS_FILE, "r") as f:
            if f"path('{url_path}/'" in f.read():
                print(f"[SKIP] URL for {model_name} already exists.")
                return

    code = f"""
from api.views_generated import {view_class_name}


urlpatterns += [
    path("{url_path}/", {view_class_name}.as_view()),
]
""".strip()

    # If file doesn't exist or has no base list, create it
    if not os.path.exists(GENERATED_URLS_FILE) or 'urlpatterns = [' not in open(GENERATED_URLS_FILE).read():
        with open(GENERATED_URLS_FILE, 'w') as f:
            f.write("from django.urls import path\nurlpatterns = []\n")

    with open(GENERATED_URLS_FILE, "a") as f:
        f.write("\n\n" + code)

    print(f"[OK] URL for {model_name} added.")
