from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    The User class is an inheritor of the AbstractUser class from the django.contrib.auth.models library.
    This is the data model contained in the user database table.
    """
    pass
