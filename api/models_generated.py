from django.db import models # For the LOVE of GOD, dont remove this!!
from main.api_auth.APIUser import APIUser


class user1_4defb8(APIUser):
    name = models.CharField(blank=True, null=True, max_length=255)
    id = models.IntegerField(primary_key=True)
    project_pk = 52
    class Meta:
        app_label = 'api'
