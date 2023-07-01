from __future__ import annotations
from typing import Optional
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.forms import ValidationError
from django.http import HttpRequest
from django.utils import timezone


# Extending from Django's built-in user model.
# See: https://docs.djangoproject.com/en/4.2/ref/contrib/auth/#user-model
# See: https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#substituting-a-custom-user-model
# See: https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#specifying-a-custom-user-model


class UserManager(BaseUserManager):
  def create_user(self, username: str, password: Optional[str] = None, **extra_fields) -> User:
    user = self.model(username=username, **extra_fields)
    user.password = make_password(password)
    user.save()
    return user

  def create_superuser(self, username: str, password: Optional[str] = None, **extra_fields) -> User:
    extra_fields.setdefault('admin', True)
    return self.create_user(username, password, **extra_fields)


def username_validator(username: str) -> None:
  if username.strip() != username:
    raise ValidationError('Username must not start with or end with a whitespace.')
  if len(username) < 3:
    raise ValidationError('Username must be at least 3 characters long.')


def user_directory_path(self: models.Model, filename: str) -> str:
  return 'accounts/user_{0}/{1}'.format(self.pk, filename)


# User privilege level for application and approval
class Privilege(models.IntegerChoices):
  AUDIT = 1, '审计'
  PRESIDENT = 2, '主席'
  COMMITTEE = 3, '执委'
  MEMBER = 4, '部员'
  VISITOR = 5, '访客'

# CSSA departments
class Department(models.IntegerChoices):
    UNDEFINED = 0, '未分配'
    PRESIDENT = 1, '主席团'
    SECRETARY = 2, '秘书处'
    TREASURER = 3, '财务处'
    CAREERS = 4, '事业部'
    MEDIA = 5, '媒体部'
    SPONSORSHIP = 6, '赞助部'
    ARTS = 7, '文艺部'
    CULTURE = 8, '文化部'
    ENTERTAINMENT = 9, '外联部'
    SPORTS = 10, '体育部'
    

class User(AbstractBaseUser):
  username = models.CharField(max_length=150, unique=True, validators=[username_validator])

  name = models.CharField(max_length=150)
  email = models.EmailField()
  admin = models.BooleanField(default=False)

  approval_level = models.IntegerField(choices=Privilege.choices, default=Privilege.VISITOR)
  application_level = models.IntegerField(choices=Privilege.choices, default=Privilege.VISITOR)
  department = models.IntegerField(choices=Department.choices, default=Department.UNDEFINED)

  avatar = models.ImageField(upload_to=user_directory_path, blank=True)
  bio = models.TextField(blank=True)
  date_joined = models.DateTimeField(default=timezone.now)

  objects = UserManager()

  REQUIRED_FIELDS = []
  USERNAME_FIELD = 'username'
  EMAIL_FIELD = 'email'

  def __str__(self) -> str:
    return str(self.name)

  # The following properties are required by the Django administration site.

  @property
  def is_staff(self) -> bool:
    return self.admin

  @property
  def is_active(self) -> bool:
    return True

  def has_perm(self, perm: str, obj=None) -> bool:
    return self.admin

  def has_module_perms(self, app_label: str) -> bool:
    return self.admin
  

# Adding custom authentication backend, modified from Django's built-in ModelBackend
# https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#writing-an-authentication-backend
# https://github.com/django/django/blob/main/django/contrib/auth/backends.py

# This import must be put after the declaration of `class User`.
from django.contrib.auth.backends import BaseBackend  # nopep8


class AuthBackend(BaseBackend):
  def user_can_authenticate(self, user: User) -> bool:
    return user.is_active

  def get_user(self, pk: int) -> Optional[User]:
    try:
      user = User.objects.get(pk=pk)
    except User.DoesNotExist:
      return None
    if not self.user_can_authenticate(user):
      return None
    return user

  def authenticate(
    self,
    request: HttpRequest,
    username: Optional[str] = None,
    password: Optional[str] = None,
    **kwargs
  ) -> Optional[User]:
    if username is None or password is None:
      return None
    try:
      user = User.objects.get(username=username)
    except User.DoesNotExist:
      User().check_password(password)
      return None
    if not user.check_password(password):
      return None
    if not self.user_can_authenticate(user):
      return None
    return user
