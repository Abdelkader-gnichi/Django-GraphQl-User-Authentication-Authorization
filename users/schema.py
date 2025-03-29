import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class UserType(DjangoObjectType):
    class Meta:
        model = UserModel
        # Exclude sensitive fields like password
        exclude = ('password', 'is_superuser', 'is_staff')
      