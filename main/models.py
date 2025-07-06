from django.db import models
from django.contrib.auth.models import User
import uuid
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='userprofile')
    profile_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    api_url = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"<user: {self.user.id} - profile_id: {self.profile_id}/>"
    def get(self):
        projects = [p.get() for p in UserProject.objects.filter(user_profile=self).all()]
        return {"id":self.profile_id,"username":self.user.username, "email":self.user.email, "first_name":self.user.first_name, "last_name":self.user.last_name, "projects":projects}

class UserProject(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE,related_name="userproject")
    name = models.TextField()
    project_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    schemas = models.JSONField(default=list)
    database = models.JSONField(default=dict)
    
    def get(self):
        return {"id":self.project_id,"name":self.name, "schemas":self.schemas, "database":self.database}

    def __str__(self):
        return f"<id: {self.project_id} - name: {self.name} />"
    

