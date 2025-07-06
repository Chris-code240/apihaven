from .models import UserProfile
import uuid
from django.conf import settings
from . import api_generator
from pydantic import field_validator, BaseModel
from .models import UserProfile
import uuid
from django.db import connections
from django.db.utils import OperationalError
import os

ENGINES = {
    'sqlite3': 'django.db.backends.sqlite3',
    'postgres': 'django.db.backends.postgresql',
    'mysql': 'django.db.backends.mysql'
}

class DBConfig(BaseModel):
    name: str  # Can be full path or db name
    user_profile_id: str
    db_engine_name: str
    db_user: str = ''
    db_password: str = ''
    db_host: str = ''
    db_port: str = ''
    alias: str = 'UNKNOWN'
    db_engine: str = 'UNKNOWN'
    options: dict = {}
    _valid: bool = False

    @field_validator('user_profile_id')
    def validate_user_profile_id(cls, value):
        if not value:
            raise ValueError("User ID cannot be empty")
        if not UserProfile.objects.filter(profile_id=uuid.UUID(value)).exists():
            raise ValueError(f"User with ID {value} does not exist")
        return value

    @field_validator('db_engine_name')
    def validate_db_engine(cls, value):
        if value not in ENGINES:
            raise ValueError(f"Unsupported engine <{value} />")
        return value

    @field_validator('db_port')
    def validate_db_port(cls, value):
        if value and not str(value).isdigit():
            raise ValueError(f"DB_PORT must be numeric, got: {value}")
        return str(value)

    def test_connection(self):
        """Skip testing SQLite3 to avoid file locking issues."""
        if self.db_engine_name == 'sqlite3':
            if not os.path.exists(self.name):
                raise ValueError(f"SQLite DB not found at: {self.name}")
            # return  # Considered valid if the file exists

        alias = f"test_{self.alias}"
        test_config = {
            "ENGINE": self.db_engine,
            "NAME": self.name,
            "USER": self.db_user,
            "PASSWORD": self.db_password,
            "HOST": self.db_host,
            "PORT": self.db_port,
            "TIME_ZONE":"UTC",
            "CONN_HEALTH_CHECKS": settings.DATABASES.get('default', {}).get('CONN_HEALTH_CHECKS', False),
            "CONN_MAX_AGE": settings.DATABASES.get('dfeualt',{}).get('CONN_MAX_AGE', False),
            "ATOMIC_REQUESTS": settings.DATABASES.get('default', {}).get('ATOMIC_REQUESTS', False),
            "AUTOCOMMIT": settings.DATABASES.get('default', {}).get('AUTOCOMMIT', True),
            "TEST": settings.DATABASES.get('default', {}).get('TEST', {}),
            "OPTIONS": self.options if len(self.options) > 0 else settings.DATABASES.get('default', {}).get('OPTIONS', {}).copy()
        } if self.db_engine != "sqlite3" else  {
            "ENGINE": self.db_engine,
            "NAME": self.name,
            "TIME_ZONE":"UTC",
            "CONN_HEALTH_CHECKS": settings.DATABASES.get('default', {}).get('CONN_HEALTH_CHECKS', False),
            "CONN_MAX_AGE": settings.DATABASES.get('dfeualt',{}).get('CONN_MAX_AGE', False),
            "ATOMIC_REQUESTS": settings.DATABASES.get('default', {}).get('ATOMIC_REQUESTS', False),
            "AUTOCOMMIT": settings.DATABASES.get('default', {}).get('AUTOCOMMIT', True),
            "TEST": settings.DATABASES.get('default', {}).get('TEST', {}),
            "OPTIONS": self.options if len(self.options) > 0 else settings.DATABASES.get('default', {}).get('OPTIONS', {}).copy()
        }

        settings.DATABASES[alias] = test_config

        try:
            conn = connections[alias]
            conn.ensure_connection()
            print(f"✅ Connected to {alias} successfully.")

        except OperationalError as e:
            raise ValueError(f"❌ Failed to connect to database: {str(e)}")
        finally:
            settings.DATABASES.pop(alias, None)
        

    def clean(self):
        self.db_engine = ENGINES[self.db_engine_name]
        self.alias = f"{self.db_engine_name}_{uuid.uuid4().hex[:6]}"
        self.test_connection()

    def is_valid(self):
        self.clean()
        self._valid = True
        return True

    def get(self):
        if not self._valid:
            raise ValueError("DBConfig must be validated first")

        config = {
            "ENGINE": self.db_engine,
            "NAME": self.name,
            "TIME_ZONE":"UTC",
            "CONN_HEALTH_CHECKS": settings.DATABASES.get('default', {}).get('CONN_HEALTH_CHECKS', False),
            "CONN_MAX_AGE": settings.DATABASES.get('dfeualt',{}).get('CONN_MAX_AGE', False),
            "ATOMIC_REQUESTS": settings.DATABASES.get('default', {}).get('ATOMIC_REQUESTS', False),
            "AUTOCOMMIT": settings.DATABASES.get('default', {}).get('AUTOCOMMIT', True),
            "TEST": settings.DATABASES.get('default', {}).get('TEST', {}),
            "OPTIONS": self.options if len(self.options) > 0 else settings.DATABASES.get('default', {}).get('OPTIONS', {}).copy()
        }

        if self.db_engine_name != 'sqlite3':
            config.update({
                "USER": self.db_user,
                "PASSWORD": self.db_password,
                "HOST": self.db_host,
                "PORT": self.db_port,
                "OPTIONS": self.options if len(self.options) > 0 else settings.DATABASES.get('default', {}).get('OPTIONS', {}).copy(),
            })

        return {self.alias: config}
