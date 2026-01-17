from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Enforce unique email
    email = models.EmailField(unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Use email as the login identifier
    USERNAME_FIELD = 'email'
    # Username is still required by AbstractUser but we make it separate
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email
