from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from shared.models import BaseModel


class Role(models.TextChoices):
    ADMIN = 'admin'
    FACTORY = 'factory'
    MANAGER = 'manager'
    ACCOUNTANT = 'accountant'
    WAREHOUSE_MANAGER = 'warehouse_manager'

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra):
        user = self.model(username=username, **extra)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, username, password=None, **extra):
        extra.setdefault('role', Role.ADMIN)
        return self.create_user(username, password, **extra)
    
class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=Role.choices)
    warehouse_id = models.UUIDField(null=True, blank=True)  # ← ИСПРАВЛЕНО: UUIDField вместо UUIDFiled
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    objects = UserManager()

    def __str__(self):
        return self.username