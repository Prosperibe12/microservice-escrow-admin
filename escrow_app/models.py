from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from auditlog.registry import auditlog
from escrow_app.helpers.models import HelperModel

from rest_framework_simplejwt.tokens import RefreshToken

class MyUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        password = 'Password123'
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, **extra_fields)

class Role(models.Model):
    Role_id = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.Role_id}::{self.Name}"

class User(HelperModel,AbstractBaseUser,PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Email and password are required. Other fields are optional.
    """
    full_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=False, null=False, unique=True)
    phone_number = models.CharField(blank=False, null=False, max_length=14)
    Role = models.ForeignKey(Role, on_delete=models.CASCADE, blank=True, null=True)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    objects = MyUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number"]

    def __str__(self):
        return f"{self.email}"

    def tokens(self):
        tokens = RefreshToken.for_user(self)
        return {
            'refresh': str(tokens),
            'access': str(tokens.access_token)
        }
        
#####################################################################################
class AppUsers(HelperModel):
    """
    A Model that implements APP Users Details
    """
    app_user = models.AutoField(blank=True, null=False,primary_key=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    reference_id = models.IntegerField(blank=True, null=True, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_updated = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email}"