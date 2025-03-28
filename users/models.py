from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.

class BaseModelMixin(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class CustomUser(AbstractUser, BaseModelMixin):
    
    email = models.EmailField(max_length=255, blank=False, null=False, unique=True, required=True, verbose_name='email')

    USERNAME_FIELD = 'username' # default value (username): unique identifier for authentication (login)  mechanism
    EMAIL_FIELD = 'email' # default value (email): Specifies the name of the field that holds the user's email address for communication and identification (like password resets).



