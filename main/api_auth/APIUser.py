from django.db import models
from uuid import uuid4
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser

class APIUser(models.Model):
    """Lightweight user object for API authentication"""
    user_id = models.UUIDField(default=uuid4, unique=True, editable=False)
    username = models.CharField(max_length=120, unique=True, blank=True, null=True)
    password = models.TextField()
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    _password_set = False
    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        if self.username is None and self.email is None:
            raise ValueError("User must have username or email")
        if self.username and any(not i.isalnum() for i in self.username):
            raise ValueError("Username must conatin only Alpha-numeric characters")
        
        
    def __str__(self):
        return f"APIUser(id={self.user_id})"
    
    def get_username(self):
        return self.username
    
    def is_authenticated(self):
        return True
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Store original password to detect changes
            self._original_password = self.password
    
    def set_password(self, raw_password):
        """Set password (will be hashed on save)"""
        self.password = raw_password
        self._password_set = True
    
    def check_password(self, raw_password):
        """Check if provided password matches stored hash"""
        if not self.password:
            return False
        return check_password(raw_password, self.password)
    
    def save(self, *args, **kwargs):
        """Hash password before saving"""
        # Hash password if it's new or changed and not already hashed
        if (self._password_set or 
            (self.password and self.password != self._original_password and 
            not self.password.startswith(('pbkdf2_', 'argon2', 'bcrypt', 'scrypt')))):
            self.password = make_password(self.password)
        
        super().save(*args, **kwargs)
        
        # Reset tracking variables
        self._password_set = False
        self._original_password = self.password
    
    @classmethod
    def authenticate(cls, username, password):
        """
        Authenticate user by username and password
        Usage: APIUserData.authenticate('john', 'plaintext_password')
        """
        try:
            user = cls.objects.get(username=username, is_active=True)
            if user.check_password(password):
                return user
            return None
        except cls.DoesNotExist:
            return None
    

